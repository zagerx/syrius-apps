#!/usr/bin/env python3
"""
电机监控系统主程序
架构说明:
1. 应用层 - Qt GUI界面和用户交互
2. 服务层 - CAN总线通信和数据处理
3. 驱动层 - 硬件协议实现
"""

# === 标准库导入 ===
import asyncio
import logging
import os

# === 第三方库 ===
import qasync
import numpy as np
from PyQt6.QtWidgets import QApplication

# === PyCyphal核心 ===
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.si.unit.velocity import Scalar_1_0

# === 自定义模块 ===
from MotorAsst.drivers.can.transport import CANNodeService
from MotorAsst.core.monitorthread import MonitorThread
from MotorAsst.core.commendthread import CommandThread
from MotorAsst.config.configlog import setup_logging
from MotorAsst.ui.windowmain import MainWindow
from MotorAsst.config import ConfigManager

# === DSDL消息类型 ===
# from dinosaurs.actuator.wheel_motor import SetTargetValue_2_0
from dinosaurs.peripheral import OperateRemoteDevice_1_0
from dinosaurs.actuator.wheel_motor import SetMode_2_0  # 添加这行导入

# ===== 全局状态 =====
command_thread = None  # 命令线程全局引用

# ===== 信号处理器 =====
def _handle_operation_mode(mode: str) -> None:
    """处理操作模式切换信号"""
    logging.info(f"操作模式变更: {mode}")
    if not command_thread:
        return

    if mode == "start":
        asyncio.create_task(
            command_thread.send_command("MotorEnable", {"enable_state": 0})
        )
    elif mode == "stop":
        asyncio.create_task(
            command_thread.send_command("MotorEnable", {"enable_state": 1})
        )
    elif mode == "brake_lock":
        asyncio.create_task(
            command_thread.send_command("OperateBrake", {
                "method": OperateRemoteDevice_1_0.Request.CLOSE,
                "name": "m-brake",
                "param": "mode=emergency"
            })
        )
    elif mode == "brake_unlock":
        asyncio.create_task(
            command_thread.send_command("OperateBrake", {
                "method": OperateRemoteDevice_1_0.Request.OPEN
            })
        )
def _handle_pid_params(params: dict) -> None:
    """处理PID参数设置信号"""
    logging.info(f"设置PID参数: {params}")
    if not command_thread:
        return
        
    pid_params = {
        "pid_params": [params["kp"], params["ki"], 0.0, params["kd"]],  # kc设为0
        "reserved": [0.0] * 12  # 预留参数
    }
    
    asyncio.create_task(
        command_thread.send_command("SetPidParams", pid_params)
    )

def _handle_target_value(values: dict) -> None:
    """处理目标速度设置信号"""
    logging.info(f"设置目标速度: {values}")
    if command_thread:
        # 单次发送模式
        asyncio.create_task(
            command_thread.start_velocity_loop(
                initial_velocity={"left": values["left"], "right": values["right"]}
            )
        )        
        # asyncio.create_task(            
        #     command_thread.start_velocity_loop(
        #         initial_velocity={"left": values["left"], "right": values["right"]},  # 使用UI传入的值
        #         interval_ms=300,
        #         duration_per_direction=8.0,
        #         cycles=100
        #     )
        # )

def _handle_target_clear() -> None:
    """处理目标清除信号"""
    logging.info("停止速度指令")
    if command_thread:
        asyncio.create_task(command_thread._stop_velocity_loop())
def _handle_control_mode(mode: str) -> None:
    """处理控制模式切换信号"""
    logging.info(f"控制模式变更: {mode}")
    if not command_thread:
        return

    if mode == "open_loop":
        asyncio.create_task(
            command_thread.send_command("SetMode", {
                "mode": SetMode_2_0.Request.CURRENT_MODE,
                "max_velocity": 5.0,  # 最大速度 (m/s)
                "acceleration": 1.0,  # 加速度 (m/s²)
                "deceleration": 1.0   # 减速度 (m/s²)
            })
        )
    elif mode == "velocity":
        asyncio.create_task(
            command_thread.send_command("SetMode", {
                "mode": SetMode_2_0.Request.SPEED_MODE,
                "max_velocity": 5.0,  # 最大速度 (m/s)
                "acceleration": 1.0,  # 加速度 (m/s²)
                "deceleration": 1.0   # 减速度 (m/s²)
            })
        )
    elif mode == "position":
        asyncio.create_task(
            command_thread.send_command("SetMode", {
                "mode": SetMode_2_0.Request.POSITION_MODE,
                "max_velocity": 5.0,  # 最大速度 (m/s)
                "acceleration": 1.0,  # 加速度 (m/s²)
                "deceleration": 1.0   # 减速度 (m/s²)
            })
        )
        logging.warning("位置模式暂未实现")


# ===== 主业务协程 =====
async def async_main() -> None:
    """主业务逻辑协程"""
    global command_thread

    # --- 初始化阶段 ---
    config = ConfigManager()
    setup_logging(config.app.logging)

    # --- Qt应用初始化 ---
    app = QApplication([])
    window = MainWindow()
    window.operationModeChanged.connect(_handle_operation_mode)
    window.targetValueRequested.connect(_handle_target_value)
    window.targetClearRequested.connect(_handle_target_clear)
    window.pidParamsRequested.connect(_handle_pid_params)  # 连接信号
    window.controlModeChanged.connect(_handle_control_mode)  # 新增控制模式信号连接

    # 初始化数据记录文件
    if not os.path.exists("./MotorAsst/output/odom.csv"):
        with open("./MotorAsst/output/odom.csv", "w", encoding="utf-8") as f:
            f.write("\n")

    # --- CAN总线初始化 ---
    transport = CANTransport(
        SocketCANMedia(config.driver.can.interface, mtu=config.driver.can.mtu),
        local_node_id=config.driver.can.node_id
    )
    node_service = CANNodeService(transport)
    if not await node_service.start():
        return

    try:
        # --- 线程启动 ---
        monitor_thread = MonitorThread(
            node_service,
            config.driver.monitors,
        )
        monitor_thread.signals.raw_data_updated.connect(window.on_raw_data)
        
        command_thread = CommandThread(node_service, config.driver.commands)
        
        await monitor_thread.start()
        await command_thread.start()
        
        # --- 主事件循环 ---
        window.show()
        await asyncio.get_event_loop().create_future()
        
    except asyncio.CancelledError:
        logging.info("正常退出")
    finally:
        await monitor_thread.stop()
        await command_thread.stop()
        await node_service.stop()

# ===== 程序入口 =====
def main() -> None:
    """应用入口点"""
    try:
        qasync.run(async_main())
    except KeyboardInterrupt:
        logging.info("用户终止")
    except Exception as e:
        logging.critical(f"系统错误: {e}")

if __name__ == "__main__":
    main()