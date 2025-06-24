import asyncio
import logging
from typing import Tuple, Optional
from uavcan.node import Heartbeat_1_0
from .base import BaseMonitor

class CommandMonitor(BaseMonitor):
    """
    心跳监控器（完整实现BaseMonitor接口）
    """
    def __init__(self, subscriber):
        super().__init__(transport=None, port=0)  # 参数仅用于满足父类，实际不使用
        self._subscriber = subscriber
        self._logger = logging.getLogger(self.__class__.__name__)
        self._initialized = True  # 直接标记为已初始化

    async def initialize(self) -> bool:
        """实现抽象方法（实际初始化由服务层完成）"""
        return True  # 始终返回True，因为订阅器已由服务层初始化

    async def monitor(self, timeout: float) -> Tuple[bool, Optional[dict]]:
        try:
            result = await self._subscriber.receive(
                monotonic_deadline=asyncio.get_event_loop().time() + timeout
            )
            if result:
                msg, transfer = result
                if (transfer.source_node_id != 28):
                    return False, None
                return (True, result)
            return False, None
        except Exception as e:
            self._logger.error(f"Monitor error: {e}")
            return False, None

    async def close(self):
        """同步关闭方法"""
        if hasattr(self, '_subscriber') and self._subscriber:
            try:
                self._subscriber.close()
            except Exception as e:
                logging.warning(f"Subscriber close error: {e}")
            finally:
                self._subscriber = None