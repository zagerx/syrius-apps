import logging
from typing import Optional, TypeVar, Generic
from pycyphal.application import make_node, NodeInfo, Node
from pycyphal.transport import Transport
from uavcan.node import Version_1_0

T = TypeVar('T')

class CANNodeService:
    """CAN节点服务层"""
    def __init__(self, 
                 transport: Transport, 
                 node_name: str = "motor_monitor"):
        self._transport = transport
        self._node: Optional[Node] = None
        self._logger = logging.getLogger(self.__class__.__name__)
        self._node_info = NodeInfo(
            name=node_name,
            software_version=Version_1_0(major=1, minor=0),
            unique_id=bytes.fromhex("DEADBEEFCAFEBABE12345678ABCDEF01")
        )

    async def start(self) -> bool:
        """启动节点服务"""
        try:
            self._node = make_node(
                transport=self._transport,
                info=self._node_info,
            )
            self._node.start()
            return True
        except Exception as e:
            self._logger.error(f"Node startup failed: {e}", exc_info=True)
            return False

    def create_subscriber(self, 
                         data_type: type[T], 
                         port: int) -> Optional[T]:
        """创建订阅器"""
        if self._node is None:
            self._logger.error("Node not initialized")
            return None
        try:
            return self._node.make_subscriber(data_type, port)
        except Exception as e:
            self._logger.error(f"Subscriber creation failed: {e}")
            return None

    def create_client(self,
                    data_type: type[T],
                    server_node_id: int,
                    port: int) -> Optional[T]:
        """创建客户端"""
        if self._node is None:
            self._logger.error("Node not initialized")
            return None
        try:
            return self._node.make_client(data_type, server_node_id, port)
        except Exception as e:
            self._logger.error(f"Client creation failed: {e}")
            return None
    
    async def stop(self):
        """释放所有资源"""
        if self._node:
            self._node.close()
            self._logger.info("Node stopped")