from dataclasses import dataclass
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

@dataclass
class LoggingConfig:
    """日志配置类"""
    level: str = "INFO"
    file: Path = Path("motor_assistant.log")
    max_size: int = 10  # MB
    backup_count: int = 3
    enable_console: bool = False

def setup_logging(config: LoggingConfig) -> None:
    """日志系统初始化"""
    logger = logging.getLogger()
    logger.setLevel(config.level)

    file_handler = RotatingFileHandler(
        filename=config.file,
        maxBytes=config.max_size * 1024 * 1024,
        backupCount=config.backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(file_handler)

    if config.enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(name)s: %(message)s'))
        logger.addHandler(console_handler)