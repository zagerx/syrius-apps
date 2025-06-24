import asyncio
import pycyphal
import numpy as np
from pycyphal.application import make_node, NodeInfo
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.node import Version_1_0
from dinosaurs.actuator.wheel_motor import PidParameter_1_0

async def client_setpid_process():
    transport = CANTransport(
        media=SocketCANMedia("can1", mtu=8),
        local_node_id=100
    )
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="pid_setter_node",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF01")
        )
    )
    client = node.make_client(PidParameter_1_0, server_node_id=28, port_name=125)

    try:
        # 设置PID参数 [kp, ki, kc, kd]
        pid_params = np.array([1.5, 0.2, 0.0, 0.1], dtype=np.float32)
        # 预留参数设为0
        reserved = np.zeros(12, dtype=np.float32)
        
        request = PidParameter_1_0.Request(
            pid_params=pid_params,
            reserved=reserved
        )

        try:
            response, _ = await asyncio.wait_for(client.call(request), timeout=1.0)  # 解包元组
            print(f"[Response] Status: {response.status}")
            if response.status == PidParameter_1_0.Response.SET_SUCCESS:
                print("PID参数设置成功")
            else:
                print("PID参数设置失败")
        except asyncio.TimeoutError:
            print("[Timeout] 未在1秒内收到响应")
    finally:
        client.close()
        node.close()
        transport.close()

if __name__ == "__main__":
    asyncio.run(client_setpid_process())