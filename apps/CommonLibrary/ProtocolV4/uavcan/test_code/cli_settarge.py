# 回顾代码，当前实现中确实创建了一个包含单个速度值(1.0 m/s)的数组
# 可以修改为设置多个不同速度值，例如1m/s和2m/s

import asyncio
import pycyphal
import numpy as np
from pycyphal.application import make_node, NodeInfo
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.node import Version_1_0
from uavcan.si.unit.velocity import Scalar_1_0
from dinosaurs.actuator.wheel_motor import SetTargetValue_2_0

async def client_settarget_process():
    transport = CANTransport(
        media=SocketCANMedia("can1", mtu=8),
        local_node_id=100
    )
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="test_node",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF01")
        )
    )
    client = node.make_client(SetTargetValue_2_0, server_node_id=28, port_name=117)

    try:
        # 创建包含两个不同速度值的数组：1.0 m/s 和 2.0 m/s
        velocities = np.array([
            Scalar_1_0(1.3),  # 第一个电机速度 1m/s
            Scalar_1_0(2.7),   # 第二个电机速度 2m/s
            # Scalar_1_0(3.3)   # 第二个电机速度 2m/s

        ], dtype=object)
        
        request = SetTargetValue_2_0.Request(velocity=velocities)

        try:
            response = await asyncio.wait_for(client.call(request), timeout=1.0)
            print(f"[Response] Full result: {response}")
        except asyncio.TimeoutError:
            print("[Timeout] No response within 200ms")
    finally:
        client.close()
        node.close()
        transport.close()

if __name__ == "__main__":
    asyncio.run(client_settarget_process())