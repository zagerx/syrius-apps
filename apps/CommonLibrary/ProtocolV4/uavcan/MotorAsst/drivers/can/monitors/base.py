from abc import ABC, abstractmethod
from typing import Optional, Tuple
from pycyphal.transport import Transport

class BaseMonitor(ABC):
    """修改基类使其更灵活"""
    def __init__(self, transport: Optional[Transport] = None, port: Optional[int] = None):
        self._transport = transport
        self._port = port
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> bool: ...

    @abstractmethod
    async def monitor(self, timeout: float) -> Tuple[bool, Optional[dict]]: ...

    @abstractmethod
    async def close(self): ...