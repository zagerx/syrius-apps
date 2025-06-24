import asyncio
import pycyphal
from pycyphal.application import make_node, NodeInfo
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.node import Version_1_0
from dinosaurs.bootstrap.updatee import UpdateeIterator_1_0

async def get_updatee_info():
    # 初始化CAN传输层
    transport = CANTransport(
        media=SocketCANMedia("can1", mtu=8),
        local_node_id=100
    )
    
    # 创建节点
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="updatee_info_client",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF01")
        ),
    )
    
    # 创建客户端
    client = node.make_client(
        UpdateeIterator_1_0,
        server_node_id=28,
        port_name=250
    )

    try:
        # 构造请求
        request = UpdateeIterator_1_0.Request(index=0)
        
        # 发送请求并等待响应
        response = await asyncio.wait_for(client.call(request), timeout=2.0)
        
        if response is not None:
            print("\n=== 原始响应数据 ===")
            print(f"响应对象类型: {type(response)}")
            print(f"响应长度: {len(response)}")
            
            updatee = response[0].updatee
            print("\n=== Updatee描述对象 ===")
            print(f"对象类型: {type(updatee)}")
            print(f"__dict__: {updatee.__dict__}")
            
            print("\n=== 字段详情 ===")
            print(f"name (bytes): {bytes(updatee.name.tobytes())}")
            print(f"file_name (bytes): {bytes(updatee.file_name.tobytes())}")
            print(f"file_path (bytes): {bytes(updatee.file_path.tobytes())}")
            print(f"build_number: {updatee.build_number}")
            print(f"build_time (bytes): {bytes(updatee.build_time.tobytes())}")
            print(f"software_version: {updatee.software_version}")
            print(f"unique_id (hex): {bytes(updatee.unique_id.tobytes()).hex()}")
            print(f"hardware_version: {updatee.hardware_version}")
            
            if len(updatee.name) == 0:
                print("\n[提示] name字段为空，表示无可用更新项")
        else:
            print("[错误] 收到空响应")
            
    except asyncio.TimeoutError:
        print("[超时] 未收到响应")
    except Exception as e:
        print(f"[异常] {type(e).__name__}: {str(e)}")
    finally:
        client.close()
        node.close()
        transport.close()

if __name__ == "__main__":
    asyncio.run(get_updatee_info())