from dataclasses import dataclass
from .configlog import LoggingConfig

@dataclass
class AppConfig:
    """应用层配置"""
    logging: LoggingConfig
    debug: bool = False

    @classmethod
    def default(cls):
        return cls(
            logging=LoggingConfig(),
            debug=False
        )