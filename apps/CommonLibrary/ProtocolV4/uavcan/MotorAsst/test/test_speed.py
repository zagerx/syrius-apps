"""

低速测试代码
电机正转一段时间，反转一段时间，循环n次

"""

#!/usr/bin/env python3
import asyncio
import logging
import qasync
import numpy as np
from PyQt6.QtWidgets import QApplication
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.si.unit.velocity import Scalar_1_0
from dinosaurs.actuator.wheel_motor import SetTargetValue_2_0
from MotorAsst.drivers.can.transport import CANNodeService
from MotorAsst.core.monitorthread import MonitorThread
from MotorAsst.core.commendthread import CommandThread
from MotorAsst.config.configlog import setup_logging
from MotorAsst.ui.windowmain import MainWindow
from MotorAsst.config import ConfigManager
import os
class TargetValueClient:
    def __init__(self, node_service: CANNodeService, target_node_id: int = 28, port: int = 114):
        self._node_service = node_service
        self._target_node_id = target_node_id
        self._port = port
        self._client = None
        self._logger = logging.getLogger(self.__class__.__name__)

    async def send_velocity_command(self, velocities: list[float]) -> bool:
        """发送速度指令到目标节点"""
        if not self._client:
            self._client = self._node_service.create_client(
                SetTargetValue_2_0,
                self._target_node_id,
                self._port
            )
            if not self._client:
                self._logger.error("Failed to create SetTargetValue client")
                return False

        try:
            # 创建速度指令数组
            velocity_objects = np.array(
                [Scalar_1_0(v) for v in velocities],
                dtype=object
            )
            request = SetTargetValue_2_0.Request(velocity=velocity_objects)
            
            response = await asyncio.wait_for(
                self._client.call(request),
                timeout=1.0
            )
            
            if response:
                self._logger.info(f"Velocity command sent successfully: {response}")
                return True
            return False
        except asyncio.TimeoutError:
            self._logger.warning("Velocity command timeout")
            return False
        except Exception as ex:
            self._logger.error(f"Velocity command failed: {ex}")
            return False

    async def close(self):
        if self._client:
            self._client.close()

async def async_main():
    """主业务逻辑协程"""
    # 初始化配置和日志
    config = ConfigManager()
    setup_logging(config.app.logging)

    # 初始化Qt
    app = QApplication([])
    window = MainWindow()


    if not os.path.exists("./MotorAsst/output/odom.csv"):
        with open("./MotorAsst/output/odom.csv", "w", encoding="utf-8") as f:
            f.write("\n")

    # 初始化CAN总线
    transport = CANTransport(
        SocketCANMedia(config.driver.can.interface, mtu=config.driver.can.mtu),
        local_node_id=config.driver.can.node_id
    )
    node_service = CANNodeService(transport)
    if not await node_service.start():
        return
    # 初始化速度指令客户端
    velocity_client = TargetValueClient(node_service)
    try:
        # 启动监控线程
        monitor_thread = MonitorThread(
            node_service,
            config.driver.monitors,
        )
        monitor_thread.signals.raw_data_updated.connect(window.on_raw_data)  # 关键连接！
 
        # 启动命令线程
        command_thread = CommandThread(node_service, config.driver.commands)
        
        await monitor_thread.start()
        await command_thread.start()
        
        # 发送使能命令并启动速度循环
        if await command_thread.send_command("MotorEnable", {"enable_state": 0}):
            await command_thread.start_velocity_loop(
                initial_velocity={"left": -0.03, "right": 0.03},
                interval_ms = 300,
                duration_per_direction=8.0,
                cycles= 100
            )
        window.show()
        # window.
        await asyncio.get_event_loop().create_future()
    except asyncio.CancelledError:
        logging.info("正常退出")
    finally:
        await monitor_thread.stop()
        await command_thread.stop()
        await node_service.stop()

def main():
    try:
        qasync.run(async_main())
    except KeyboardInterrupt:
        logging.info("用户终止")

if __name__ == "__main__":
    main()