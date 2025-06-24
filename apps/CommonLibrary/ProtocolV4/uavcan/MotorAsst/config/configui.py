# 修复缺失的heartbeat_timeout_ms属性
from dataclasses import dataclass, field
from typing import Dict, Tuple

@dataclass
class UIConfig:
    """UI全局配置（修复版）"""
    window_title: str = "UAVCAN 电机助手"
    window_size: Tuple[int, int] = (800, 600)
    decimal_precision: int = 3
    heartbeat_timeout_ms: int = 2000  # 添加缺失的心跳超时属性
    
    status_mode_map: Dict[int, str] = field(
        default_factory=lambda: {
            0: "运行", 
            1: "初始化",
            2: "维护", 
            3: "升级"
        }
    )
    
    status_health_map: Dict[int, Tuple[str, str]] = field(
        default_factory=lambda: {
            0: ("正常", "green"),
            1: ("注意", "orange"),
            2: ("警告", "yellow"),
            3: ("故障", "red")
        }
    )
    
    label_style: str = "font-weight: bold;"
    data_label_font_size: int = 12
    data_label_min_width: int = 100