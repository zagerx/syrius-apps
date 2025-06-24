import asyncio
import logging
from typing import List,Optional,Callable
from MotorAsst.config.configdrivers import MonitorConfig
from MotorAsst.drivers.can.transport import CANNodeService

from typing import Dict, Any, List
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal

class MonitorSignals(QObject):
    """统一信号发射器"""
    raw_data_updated = pyqtSignal(str, object, int)  # (name, raw_data, priority)

class MonitorThread:
    def __init__(self, node_service: CANNodeService, monitor_configs: List[MonitorConfig]):
        self.node_service = node_service
        self.monitor_configs = monitor_configs
        self.tasks = []
        self._logger = logging.getLogger(self.__class__.__name__)
        self.signals = MonitorSignals()

    async def start(self):
        """启动所有监控任务"""
        for cfg in self.monitor_configs:
            if not cfg.enabled:
                continue
                
            subscriber = self.node_service.create_subscriber(
                cfg.data_type,
                cfg.port
            )
            if not subscriber:
                continue
            self.tasks.append(asyncio.create_task(
                self._run_monitor(cfg.monitor_class(subscriber),cfg)
            ))

    async def _run_monitor(self, monitor, config: MonitorConfig):
        """修复参数传递错误的监控循环"""
        try:
            while True:
                success, raw_data = await monitor.monitor(1.0)
                if not success:
                    continue
                # self._logger.info(raw_data)
                self.signals.raw_data_updated.emit(
                    config.display_name.lower(),
                    raw_data,
                    config.priority
                )                    
        except asyncio.CancelledError:
            self._logger.debug(f"{config.display_name} monitor stopped")
        except Exception as e:
            self._logger.error(f"Monitor error: {e}", exc_info=True)
       
    async def stop(self):
        """停止所有监控任务"""
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)