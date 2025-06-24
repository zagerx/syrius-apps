import asyncio
import pycyphal
from pycyphal.application import make_node, NodeInfo
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.node import Version_1_0
from dinosaurs.actuator.wheel_motor import SetMode_2_0
from uavcan.si.unit.velocity import Scalar_1_0 as VelocityScalar  # 新增导入
from uavcan.si.unit.acceleration import Scalar_1_0 as AccelerationScalar  # 新增导入

async def client_motormode_process():
    transport = CANTransport(
        media=SocketCANMedia("can1", mtu=8),
        local_node_id=100
    )
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="motor_mode_client",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF03")
        )
    )
    client = node.make_client(SetMode_2_0, server_node_id=28, port_name=119)

    try:
        result = await asyncio.wait_for(
            client.call(SetMode_2_0.Request(
                # mode=SetMode_2_0.Request.SPEED_MODE,
                mode=SetMode_2_0.Request.CURRENT_MODE,
                max_velocity=VelocityScalar(5.0),
                acceleration=AccelerationScalar(1.0),
                deceleration=AccelerationScalar(1.0)
            )),
            timeout=0.2
        )
        if result is not None:
            response, _ = result  # 解包响应和传输元组
            status_map = {
                SetMode_2_0.Response.SET_SUCCESS: "Success",
                SetMode_2_0.Response.FAILED: "Failed",
                SetMode_2_0.Response.PARAMETER_NOT_INIT: "Params Not Init"
            }
            print(f"Mode set result: {status_map.get(response.status, 'Unknown')}")
    except asyncio.TimeoutError:
        print("Timeout waiting for mode set response")
    finally:
        client.close()
        node.close()
        transport.close()

if __name__ == "__main__":
    asyncio.run(client_motormode_process())