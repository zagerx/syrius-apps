#!/usr/bin/env python3
"""
订阅CAN总线上的诊断记录消息（uavcan.diagnostic.Record）
需要先运行 compile_dsdl.py 生成DSDL定义
"""

import sys
import pathlib
import asyncio
sys.path.insert(0, str(pathlib.Path(".pyFolder").resolve()))
import pycyphal
from pycyphal.application import make_node, NodeInfo
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.node import Version_1_0
from uavcan.diagnostic import Record_1_1

async def sub_record_process() -> None:
    # 初始化 CAN 接口和传输层
    media = SocketCANMedia("can1", mtu=8)
    transport = CANTransport(media, local_node_id=28)
    
    # 创建节点（显式启动）
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="diagnostic_monitor",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF01")
        )
    )
    node.start()
    
    # 创建订阅者（使用固定端口ID 8184）
    sub = node.make_subscriber(Record_1_1, 8184)
    print("正在监听诊断记录消息... (Ctrl+C退出)")

    try:
        while True:
            # 接收消息（带超时）
            result = await sub.receive(monotonic_deadline=asyncio.get_event_loop().time() + 1.0)
            if result is not None:
                msg, transfer = result
                print(f"\n诊断记录来自节点 {transfer.source_node_id}:")
                print(f"- 时间戳: {msg.timestamp.microsecond} μs")
                print(f"- 严重等级: {msg.severity.value}")
                print(f"- 消息内容: {bytes(msg.text).decode()}")
    except KeyboardInterrupt:
        pass
    finally:
        sub.close()
        node.close()
        transport.close()
        media.close()

if __name__ == "__main__":
    asyncio.run(sub_record_process())