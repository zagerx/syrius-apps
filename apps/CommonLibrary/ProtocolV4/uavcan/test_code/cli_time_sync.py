import asyncio
import pycyphal
from pycyphal.application import make_node, NodeInfo
from pycyphal.transport.can import CANTransport
from pycyphal.transport.can.media.socketcan import SocketCANMedia
from uavcan.node import Version_1_0
from uavcan.time import Synchronization_1_0

async def time_sync_process():
    # Initialize transport and node
    transport = CANTransport(
        media=SocketCANMedia("can1", mtu=8),  # Classic CAN configuration
        local_node_id=100  # Node ID (adjust as needed)
    )
    
    node = make_node(
        transport=transport,
        info=NodeInfo(
            name="time_sync_node",
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF01")
        )
    )
    
    # Start the node
    node.start()
    
    try:
        # Create publisher for time sync messages
        pub = node.make_publisher(Synchronization_1_0, 7168)  # Fixed port ID 7168
        
        # Get current time in microseconds
        current_time_us = int(asyncio.get_event_loop().time() * 1e6)
        
        # Create sync message
        sync_msg = Synchronization_1_0(
            previous_transmission_timestamp_microsecond=current_time_us
        )
        
        # Publish the message
        await pub.publish(sync_msg)
        print(f"[Success] Published sync message with timestamp: {current_time_us} µs")
        
    finally:
        # Cleanup
        pub.close()
        node.close()
        transport.close()

if __name__ == "__main__":
    asyncio.run(time_sync_process())