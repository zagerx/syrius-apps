import logging
from typing import Optional
from pathlib import Path
from .configdrivers import DriverConfig
from .configapp import AppConfig
from .configui import UIConfig

class ConfigManager:
    """
    配置管理器（无YAML版本）
    职责：
    1. 集中管理所有配置层级
    2. 提供默认配置
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config()
        return cls._instance

    def _init_config(self):
        """初始化所有配置层级"""
        self.driver = DriverConfig.default()
        self.app = AppConfig.default()
        self.ui = UIConfig()  # 直接实例化，不使用YAML加载

    @property
    def can_config(self):
        """快捷访问CAN配置"""
        return self.driver.can

    @property
    def monitors_config(self):
        """快捷访问监控器配置"""
        return self.driver.monitors

    @property
    def logging_config(self):
        """快捷访问日志配置"""
        return self.app.logging

    def update_ui_config(self, **kwargs):
        """动态更新UI配置"""
        for k, v in kwargs.items():
            if hasattr(self.ui, k):
                setattr(self.ui, k, v)
            else:
                logging.warning(f"无效的UI配置项: {k}")

# 示例用法：
# config = ConfigManager()
# print(config.ui.window_title)
# config.update_ui_config(window_title="新标题")