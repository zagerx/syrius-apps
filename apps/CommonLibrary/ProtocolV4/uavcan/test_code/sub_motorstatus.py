import sys
import pathlib
sys.path.append(str(pathlib.Path(".dsdl_generated").resolve()))
import asyncio
import pycyphal
import time
from pycyphal.application import make_node, NodeInfo
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.node import Version_1_0
from dinosaurs.actuator.wheel_motor import Status_1_0

class MotorStatusLogger:
    def __init__(self):
        self.start_time = time.monotonic()

    def log(self, msg, transfer):
        print("\n电机状态数据:")
        print(f"时间戳: {msg.timestamp}")
        print(f"驱动输入电流: {msg.driver_input_current.ampere:.3f}A")
        print(f"电压: {msg.voltage.volt:.3f}V")
        print(f"驱动最高温度: {msg.driver_max_temperature.kelvin:.1f}K")
        print(f"模式: {msg.mode}")
        print(f"电机状态: {msg.status}")
        print("-" * 40)

async def sub_motorstatus_process():
    logger = MotorStatusLogger()
    media = SocketCANMedia("can1", mtu=8)
    transport = CANTransport(media, local_node_id=100)
    
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="motor_status_subscriber",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF03")
        )
    )
    node.start()

    async def handler(msg, transfer):
        logger.log(msg, transfer)

    # 订阅Status消息，端口ID需要根据实际配置调整
    sub = node.make_subscriber(Status_1_0, 1101)  # 示例端口ID
    sub.receive_in_background(handler)
    
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        sub.close()
        node.close()
        transport.close()

if __name__ == "__main__":
    asyncio.run(sub_motorstatus_process())