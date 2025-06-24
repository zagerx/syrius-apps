from dataclasses import dataclass
from typing import Type, Any, List, Dict
from uavcan.node import Heartbeat_1_0
from dinosaurs.actuator.wheel_motor import SetTargetValue_2_0, OdometryAndVelocityPublish_1_0, Enable_1_0
from MotorAsst.drivers.can.monitors.base import BaseMonitor
from MotorAsst.drivers.can.monitors.commandmonitors import CommandMonitor
from uavcan.si.unit.velocity import Scalar_1_0
import numpy as np
from dinosaurs.peripheral import OperateRemoteDevice_1_0
from dinosaurs.sensor.binarysignal import BinarySignal_2_0
from dinosaurs.actuator.wheel_motor import Status_1_0  # 添加这行导入
from dinosaurs.actuator.wheel_motor import PidParameter_1_0  # 添加这行导入
from dinosaurs.actuator.wheel_motor import SetMode_2_0  # 添加这行导入

@dataclass
class CanConfig:
    """CAN总线配置"""
    interface: str = "can1"
    node_id: int = 100
    mtu: int = 8
    bitrate: int = 500000

@dataclass
class MonitorConfig:
    """数据监控配置"""
    data_type: Type[Any]
    port: int
    monitor_class: Type[BaseMonitor]
    display_name: str
    enabled: bool = True
    priority: int = 1

@dataclass
class CommandConfig:
    """命令配置"""
    data_type: Type[Any]
    server_node_id: int
    port: int
    display_name: str
    timeout: float = 1.0
    enabled: bool = True

@dataclass 
class DriverConfig:
    """驱动层总配置"""
    can: CanConfig
    monitors: List[MonitorConfig]
    commands: Dict[str, CommandConfig]

    @classmethod
    def default(cls):
        return cls(
            can=CanConfig(),
            monitors=[
                MonitorConfig(
                    data_type=Heartbeat_1_0,
                    port=7509,
                    monitor_class=CommandMonitor,
                    display_name="Heartbeat",
                    priority=2
                ),
                MonitorConfig(
                    data_type=OdometryAndVelocityPublish_1_0,
                    port=1100,
                    monitor_class=CommandMonitor,
                    display_name="Odometry",
                    priority=0
                ),
                MonitorConfig(
                    data_type=BinarySignal_2_0,
                    port=1004,  # 与sub_binarysignal.py一致
                    monitor_class=CommandMonitor,
                    display_name="BinarySignal",
                    priority=1
                ),
                MonitorConfig(
                    data_type=Status_1_0,
                    port=1101,  # 与sub_motorstatus.py一致
                    monitor_class=CommandMonitor,
                    display_name="MotorStatus",
                    priority=1  # 中频数据
                )                                
            ],
            commands={
                "MotorEnable": CommandConfig(
                    data_type=Enable_1_0,
                    server_node_id=28,
                    port=113,
                    display_name="Motor Enable",
                ),
                "SetVelocity": CommandConfig(
                    data_type=SetTargetValue_2_0,
                    server_node_id=28,
                    port=117,
                    display_name="Set Velocity"
                ),
                "OperateBrake": CommandConfig(
                    data_type=OperateRemoteDevice_1_0,
                    server_node_id=28,
                    port=121,
                    display_name="Operate Brake"
                ),
                "SetPidParams": CommandConfig(
                    data_type=PidParameter_1_0,
                    server_node_id=28,
                    port=125,
                    display_name="Set PID Parameters"
                ),                
                "SetMode": CommandConfig(
                    data_type=SetMode_2_0,
                    server_node_id=28,
                    port=119,
                    display_name="Set Motor Mode"
                ),                
            }
        )

    @staticmethod
    def build_velocity_request(params: Dict[str, float]) -> Any:
        """构建速度控制请求"""
        velocities = np.array([
            Scalar_1_0(params["left"]),
            Scalar_1_0(params["right"])
        ], dtype=object)
        return SetTargetValue_2_0.Request(velocity=velocities)