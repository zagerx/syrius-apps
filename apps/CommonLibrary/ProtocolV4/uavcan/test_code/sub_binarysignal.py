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
from dinosaurs.sensor.binarysignal import BinarySignal_2_0

class BinarySignalLogger:
    def __init__(self):
        self.start_time = time.monotonic()
        self.last_state = None

    def log(self, msg, transfer):
        device_name = bytes(msg.name.value.tobytes()).decode('utf-8').rstrip('\x00')
        print("原始数据:")
        print(f"时间戳: {msg.timestamp}")
        print(f"设备名: {device_name}")  # 使用预处理后的字符串
        print(f"状态: {msg.state}")
        print(f"设备ID: {msg.device_id}")
        print("-" * 40)

async def sub_binarysignal_process():
    logger = BinarySignalLogger()
    media = SocketCANMedia("can1", mtu=8)
    transport = CANTransport(media, local_node_id=28)
    
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="binary_signal_subscriber",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF02")
        )
    )
    node.start()

    async def handler(msg, transfer):
        logger.log(msg, transfer)

    # 订阅BinarySignal消息，使用适当的端口ID
    sub = node.make_subscriber(BinarySignal_2_0, 1004)  
    sub.receive_in_background(handler)
    
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        sub.close()
        node.close()
        transport.close()

if __name__ == "__main__":
    asyncio.run(sub_binarysignal_process())