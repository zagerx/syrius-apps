"""
Cyphal service server for receiving wheel motor target values
Listens for SetTargetValue requests on service ID 117
功能待确认
"""

import sys
import pathlib
from typing import Optional
sys.path.append(str(pathlib.Path(".dsdl_generated").resolve()))
import asyncio
import pycyphal
from pycyphal.application import make_node, NodeInfo
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.node import Version_1_0
from dinosaurs.actuator.wheel_motor import SetTargetValue_2_0

class TargetValueSubscriber:
    def __init__(self, node: pycyphal.application.Node):
        self._node = node
        self._server = node.get_server(SetTargetValue_2_0, 117)
        
    async def run(self) -> None:
        async def handler(request: SetTargetValue_2_0.Request, 
                        metadata: pycyphal.presentation.ServiceRequestMetadata) -> Optional[SetTargetValue_2_0.Response]:
            self._process_request(request, metadata)
            return SetTargetValue_2_0.Response(status=0)

        self._server.serve_in_background(handler)
        print(f"Server started on service ID {self._server.port_id}")
        while True:
            await asyncio.sleep(1)

    def _process_request(self, 
                        request: SetTargetValue_2_0.Request,
                        metadata: pycyphal.presentation.ServiceRequestMetadata) -> None:
        print("\n=== Received Target Value Request ===")
        print(f"From node: {metadata.client_node_id}")
        
        # 优先检查速度指令（根据DSDL union定义顺序）
        if request.velocity is not None:
            print(f"[ACTUAL COMMAND] Velocity targets: {[x.meter_per_second for x in request.velocity]}")
        elif request.torque is not None:
            print(f"[ACTUAL COMMAND] Torque targets: {[x.newton_meter for x in request.torque]}")
        elif request.position is not None:
            print(f"[ACTUAL COMMAND] Position targets: {[x.meter for x in request.position]}")
        else:
            print("Empty target request received")

async def main() -> None:
    media = SocketCANMedia("can1", mtu=8)
    transport = CANTransport(media, local_node_id=28)
    
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="motor_target_subscriber",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF01")
        )
    )
    node.start()

    try:
        subscriber = TargetValueSubscriber(node)
        await subscriber.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())


