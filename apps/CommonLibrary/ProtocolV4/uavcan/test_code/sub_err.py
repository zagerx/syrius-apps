#!/usr/bin/env python3
"""
订阅全局健康状态消息（dinosaurs.GlobalHealth）
"""

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(".pyFolder").resolve()))
import pycyphal
from pycyphal.application import make_node, NodeInfo
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.node import Version_1_0
from dinosaurs import GlobalHealth_1_0
import asyncio

async def sub_global_health():
    # 初始化CAN接口
    media = SocketCANMedia("can1", mtu=8)
    transport = CANTransport(media, local_node_id=100)
    
    # 创建节点
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="health_monitor",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF01")
        )
    )
    node.start()
    
    # 创建订阅者（假设端口号为7507）
    sub = node.make_subscriber(GlobalHealth_1_0, 2)
    print("正在监听全局健康状态... (Ctrl+C退出)")

    try:
        while True:
            result = await sub.receive(monotonic_deadline=asyncio.get_event_loop().time() + 1.0)
            if result is not None:
                msg, transfer = result
                print(f"\n=== 健康状态更新 [节点 {transfer.source_node_id}] ===")
                
                # 解析设备类型
                device_type = "未知设备"
                for name, value in vars(GlobalHealth_1_0).items():
                    if name.isupper() and value == msg.device_type:
                        device_type = name
                        break
                
                print(f"错误源: {msg.error_source.value.tobytes().decode()}")
                print(f"设备类型: {device_type} ({msg.device_type})")
                print(f"健康状态: {msg.health.value}")
                print(f"错误码: {msg.error_code}")
                print(f"错误信息: {msg.error_message.value.tobytes().decode()}")
                
    except KeyboardInterrupt:
        pass
    finally:
        sub.close()
        node.close()
        transport.close()
        media.close()

if __name__ == "__main__":
    asyncio.run(sub_global_health())