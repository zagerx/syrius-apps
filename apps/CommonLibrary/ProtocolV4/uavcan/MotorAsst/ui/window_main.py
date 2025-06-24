# #!/usr/bin/env python3
# """
# 主窗口界面 - 配置驱动版本
# """
# import time
# from PyQt6.QtWidgets import (
#     QMainWindow, QLabel, QMessageBox, QVBoxLayout,
#     QHBoxLayout, QGroupBox, QWidget, QStatusBar,QPushButton
# )
# from PyQt6.QtCore import Qt, pyqtSlot, QTimer
# from PyQt6.QtGui import QFont
# from MotorAsst.config.configui import UIConfig
# import logging
# class MainWindow(QMainWindow):
#     def __init__(self, ui_config: UIConfig):
#         super().__init__()
#         self._ui_config = ui_config
#         self._last_heartbeat_time = 0
#         self._init_ui()
#         self._setup_connections()
#         self._start_status_timer()

#     def _init_ui(self):
#         """初始化所有UI组件"""
#         self.setWindowTitle(self._ui_config.window_title)
#         self.resize(*self._ui_config.window_size)

#         # 主容器
#         self.central_widget = QWidget()
#         self.setCentralWidget(self.central_widget)
#         self.main_layout = QVBoxLayout(self.central_widget)

#         # 1. 状态显示组
#         self._init_status_group()

#         # 2. 里程计数据组
#         self._init_odometry_group()

#         # 3. 速度数据组
#         self._init_velocity_group()

#         # 状态栏
#         self._init_status_bar()

#         # 按钮
#         self._init_control_buttons()

#     def _init_status_group(self):
#         """初始化状态显示组件"""
#         self.status_group = QGroupBox("节点状态")
#         status_layout = QHBoxLayout()
        
#         self.node_status_label = QLabel("未连接")
#         self.node_mode_label = QLabel("模式: -")
#         self.node_health_label = QLabel("健康: -")
        
#         for widget in [self.node_status_label, self.node_mode_label, self.node_health_label]:
#             widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
#             widget.setStyleSheet(self._ui_config.label_style)
        
#         status_layout.addWidget(self.node_status_label)
#         status_layout.addWidget(self.node_mode_label)
#         status_layout.addWidget(self.node_health_label)
#         self.status_group.setLayout(status_layout)
#         self.main_layout.addWidget(self.status_group)

#     def _init_odometry_group(self):
#         """初始化里程计组件"""
#         self.odom_group = QGroupBox("里程计数据")
#         odom_layout = QHBoxLayout()
        
#         self.left_odom_label = self._create_data_label("-.---")
#         self.right_odom_label = self._create_data_label("-.---")
        
#         odom_layout.addWidget(QLabel("左轮里程:"))
#         odom_layout.addWidget(self.left_odom_label)
#         odom_layout.addSpacing(20)
#         odom_layout.addWidget(QLabel("右轮里程:"))
#         odom_layout.addWidget(self.right_odom_label)
#         self.odom_group.setLayout(odom_layout)
#         self.main_layout.addWidget(self.odom_group)

#     def _init_velocity_group(self):
#         """初始化速度组件"""
#         self.vel_group = QGroupBox("速度数据")
#         vel_layout = QHBoxLayout()
        
#         self.left_vel_label = self._create_data_label("-.---")
#         self.right_vel_label = self._create_data_label("-.---")
        
#         vel_layout.addWidget(QLabel("左轮速度:"))
#         vel_layout.addWidget(self.left_vel_label)
#         vel_layout.addSpacing(20)
#         vel_layout.addWidget(QLabel("右轮速度:"))
#         vel_layout.addWidget(self.right_vel_label)
#         self.vel_group.setLayout(vel_layout)
#         self.main_layout.addWidget(self.vel_group)
#         self.main_layout.addStretch()

#     def _init_status_bar(self):
#         """初始化状态栏"""
#         self.status_bar = QStatusBar()
#         self.setStatusBar(self.status_bar)
#         self.status_label = QLabel("就绪")
#         self.status_bar.addPermanentWidget(self.status_label)

#     def _init_control_buttons(self):
#         """初始化使能/失能控制按钮"""
#         self.control_group = QGroupBox("电机控制")
#         control_layout = QHBoxLayout()
        
#         # 使能按钮
#         self.enable_btn = QPushButton("使能 (ENABLE)")
#         self.enable_btn.setStyleSheet(
#             "background-color: #4CAF50; color: white; font-weight: bold;"  # 绿色
#         )
        
#         # 失能按钮
#         self.disable_btn = QPushButton("失能 (DISABLE)")
#         self.disable_btn.setStyleSheet(
#             "background-color: #F44336; color: white; font-weight: bold;"  # 红色
#         )
        
#         control_layout.addWidget(self.enable_btn)
#         control_layout.addWidget(self.disable_btn)
#         self.control_group.setLayout(control_layout)
#         self.main_layout.addWidget(self.control_group)

#     def _setup_connections(self):
#         """初始化信号连接"""
#         self.enable_btn.clicked.connect(self._on_enable)
#         self.disable_btn.clicked.connect(self._on_disable)

#     def _on_enable(self):
#         """使能按钮回调"""
#         if hasattr(self, '_controller'):
#             if self._controller.enable_motor():
#                 self.status_label.setText("电机已使能")
#                 return
        
#         QMessageBox.critical(
#             self,
#             "操作失败",
#             "无法使能电机",
#             buttons=QMessageBox.StandardButton.Ok
#         )

#     def _on_disable(self):
#         """失能按钮回调"""
#         if hasattr(self, '_controller'):
#             if self._controller.disable_motor():
#                 self.status_label.setText("电机已失能")
#                 return
        
#         QMessageBox.critical(
#             self,
#             "操作失败",
#             "无法失能电机",
#             buttons=QMessageBox.StandardButton.Ok
#         )

#     def _create_data_label(self, text: str) -> QLabel:
#         """创建统一风格的数据标签"""
#         label = QLabel(text)
#         font = QFont()
#         font.setPointSize(self._ui_config.data_label_font_size)
#         font.setBold(True)
#         label.setFont(font)
#         label.setAlignment(Qt.AlignmentFlag.AlignRight)
#         label.setMinimumWidth(self._ui_config.data_label_min_width)
#         return label

#     def _start_status_timer(self):
#         """启动状态检查定时器"""
#         self._status_timer = QTimer(self)
#         self._status_timer.timeout.connect(self._check_connection_status)
#         self._status_timer.start(1000)  # 每秒检查一次

#     def _check_connection_status(self):
#         """检查连接状态"""
#         current_time = time.time() * 1000  # 当前时间戳(ms)
#         if current_time - self._last_heartbeat_time > self._ui_config.heartbeat_timeout_ms:
#             self._show_disconnected_status()

#     def _show_disconnected_status(self):
#         """显示断开连接状态"""
#         self.node_status_label.setText("节点断开")
#         self.node_mode_label.setText("模式: 离线")
#         self.node_health_label.setText("健康: 故障")
#         self.node_health_label.setStyleSheet("color: red;")
#         self._clear_data_display()
#         self.status_label.setText("通信超时")

#     def _clear_data_display(self):
#         """清空数据展示"""
#         self.left_odom_label.setText("-.---")
#         self.right_odom_label.setText("-.---")
#         self.left_vel_label.setText("-.---")
#         self.right_vel_label.setText("-.---")

#     @pyqtSlot(dict)
#     def handle_heartbeat(self, data: dict):
#         """处理心跳数据（线程安全）"""
#         self._last_heartbeat_time = time.time() * 1000
        
#         health_text, health_color = self._ui_config.status_health_map.get(
#             data['health'], ("未知", "gray"))
        
#         self.node_status_label.setText(f"节点ID: {data['node_id']}")
#         self.node_mode_label.setText(
#             f"模式: {self._ui_config.status_mode_map.get(data['mode'], '未知')}")
#         self.node_health_label.setText(f"健康: {health_text}")
#         self.node_health_label.setStyleSheet(f"color: {health_color};")

#     @pyqtSlot(dict)
#     def handle_odometry(self, data: dict):
#         """处理里程计数据（线程安全）"""
#         fmt = f"{{:.{self._ui_config.decimal_precision}f}}"
#         self.left_odom_label.setText(fmt.format(data['left_odometry']))
#         self.right_odom_label.setText(fmt.format(data['right_odometry']))
#         self.left_vel_label.setText(fmt.format(data['left_velocity']))
#         self.right_vel_label.setText(fmt.format(data['right_velocity']))
#         self.status_label.setText(f"最后更新: {data['timestamp']}ms")

#     @pyqtSlot(str)
#     def handle_error(self, message: str):
#         """处理错误信息（线程安全）"""
#         QMessageBox.critical(self, "通信错误", message)
#         self.status_label.setText(f"错误: {message[:50]}...")
#         self._show_disconnected_status()

#     def closeEvent(self, event):
#         """窗口关闭事件处理"""
#         if hasattr(self, '_controller'):
#             try:
#                 self._controller.stop()  # 现在UIController有stop方法
#             except Exception as e:
#                 logging.error(f"Controller stop failed: {e}")
#         event.accept()

#     def set_controller(self, controller):
#         """注入控制器引用"""
#         self._controller = controller