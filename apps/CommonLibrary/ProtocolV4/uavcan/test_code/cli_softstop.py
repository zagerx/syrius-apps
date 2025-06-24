import asyncio
import pycyphal
from pycyphal.application import make_node, NodeInfo
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.node import Version_1_0
from dinosaurs.actuator import SoftwareEmergencyStop_1_0

async def emergency_stop_control():
    # 初始化CAN传输层
    transport = CANTransport(
        media=SocketCANMedia("can1", mtu=8),  # 经典CAN配置
        local_node_id=100                     # 客户端节点ID
    )
    
    # 创建节点
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="emergency_stop_controller",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF01")
        )
    )
    
    # 创建客户端（端口号需与服务器端一致）
    client = node.make_client(
        SoftwareEmergencyStop_1_0,
        server_node_id=28,
        port_name=116  # 固定端口号，参考cli_motor_en.py的配置方式
    )

    try:
        # 构造紧急停止请求（STATUS_EMERGENCY=1）
        request = SoftwareEmergencyStop_1_0.Request(
            emergency_status=SoftwareEmergencyStop_1_0.Request.STATUS_EMERGENCY
        )

        # 发送请求并等待响应
        response = await asyncio.wait_for(client.call(request), timeout=0.2)
        if response is not None:
            status = response[0].status
            status_str = {
                SoftwareEmergencyStop_1_0.Response.SET_SUCCESS: "SET_SUCCESS",
                SoftwareEmergencyStop_1_0.Response.FAILED: "FAILED",
                SoftwareEmergencyStop_1_0.Response.PARAMETER_NOT_INIT: "PARAMETER_NOT_INIT"
            }.get(status, f"UNKNOWN({status})")
            print(f"[响应] 状态: {status_str}")
        else:
            print("[错误] 无响应数据")
    except asyncio.TimeoutError:
        print("[超时] 200ms内未收到响应")
    finally:
        client.close()
        node.close()
        transport.close()

if __name__ == "__main__":
    asyncio.run(emergency_stop_control())