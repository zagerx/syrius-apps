import asyncio
import pycyphal
from pycyphal.application import make_node, NodeInfo
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.node import Version_1_0
from dinosaurs.peripheral import OperateRemoteDevice_1_0

async def operate_remote_device():
    # 初始化 CAN 传输层
    transport = CANTransport(
        media=SocketCANMedia("can1", mtu=8),  # 经典 CAN 配置
        local_node_id=100                      # 客户端节点 ID
    )
    
    # 创建节点并显式配置服务端口 ID
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="remote_operator",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF01")
        ),
    )
    
    # 创建客户端
    client = node.make_client(
        OperateRemoteDevice_1_0,
        server_node_id=28,
        port_name=121
    )

    try:
        # 构造请求
        request = OperateRemoteDevice_1_0.Request(
            method=OperateRemoteDevice_1_0.Request.OPEN,
            name="m-brake",
            param="mode=high_accuracy"
        )

        # 发送请求并等待响应
        response = await asyncio.wait_for(client.call(request), timeout=2.0)  # 延长超时时间
        if response is not None:
            print(f"[成功] 设备操作结果: {response[0].result}, 返回值: {bytes(response[0].value).decode()}")
        else:
            print("[错误] 无响应数据")
    except asyncio.TimeoutError:
        print("[超时] 未收到响应")
    finally:
        client.close()
        node.close()
        transport.close()

if __name__ == "__main__":
    asyncio.run(operate_remote_device())