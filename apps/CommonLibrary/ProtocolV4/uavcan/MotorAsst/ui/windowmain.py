from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtCore import QTimer, pyqtSlot, pyqtSignal
from MotorAsst.ui.uimain import Ui_MainWindow
from collections import deque
import time

class MainWindow(QMainWindow):
    """
    主窗口类 - 电机监控系统UI主界面
    功能：
    1. 实时显示各类传感器数据（高频/中频/低频）
    2. 提供电机控制接口
    3. 数据记录功能
    """
    
    # ==================== 信号定义 ====================
    operationModeChanged = pyqtSignal(str)    # 操作模式变更信号
    targetValueRequested = pyqtSignal(dict)   # 目标值设置信号 
    targetClearRequested = pyqtSignal()      # 目标值清除信号
    pidParamsRequested = pyqtSignal(dict)  # 新增PID参数信号
    controlModeChanged = pyqtSignal(str)  # 新增控制模式信号

    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # ---------- UI初始化 ----------
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("电机监控系统")
        
        # ---------- 数据缓冲区初始化 ----------
        self._high_freq_buffer = deque(maxlen=200)  # 高频数据缓冲区(100Hz, 保留2秒)
        self._mid_freq_buffer = deque(maxlen=100)   # 中频数据缓冲区(50Hz, 保留2秒)
        self._last_update_time = {}                # 最后更新时间记录
        
        # ---------- 初始化各组件 ----------
        self._init_status_group()      # 状态显示组件
        self._init_timers()            # 多级刷新定时器
        self._setup_button_connections()  # 按钮信号连接
        
        # 设置互斥组
        self.ui.radioButton_4.setAutoExclusive(True)
        self.ui.radioButton_5.setAutoExclusive(True)

       # 连接信号 - 使用下划线命名
        self.ui.radioButton_4.toggled.connect(
            lambda checked: self._on_operation_mode_changed(checked, "start"))
        self.ui.radioButton_5.toggled.connect(
            lambda checked: self._on_operation_mode_changed(checked, "stop"))
        # 连接刹车控制信号
        self.ui.radioButton_6.toggled.connect(
            lambda checked: self._on_operation_mode_changed(checked, "brake_lock"))
        self.ui.radioButton_7.toggled.connect(
            lambda checked: self._on_operation_mode_changed(checked, "brake_unlock"))                
        # 连接控制模式信号
        self.ui.radioButton.toggled.connect(
            lambda checked: self._on_control_mode_changed(checked, "open_loop"))
        self.ui.radioButton_2.toggled.connect(
            lambda checked: self._on_control_mode_changed(checked, "velocity"))
        self.ui.radioButton_3.toggled.connect(
            lambda checked: self._on_control_mode_changed(checked, "position"))

    # ==================== 初始化方法 ====================
    def _init_status_group(self):
        """初始化状态显示组件"""
        self.ui.lineEdit_5_1.setReadOnly(True)  # 节点ID显示框设为只读
        self.ui.radioButton_5.setChecked(True)  # 默认选择"停止"模式
    # ==== 关键修改：设置显示宽度和范围 ====
    # 获取所有 doubleSpinBox 组件
        spin_boxes = [
            self.ui.doubleSpinBox, 
            self.ui.doubleSpinBox_2, 
            self.ui.doubleSpinBox_3
        ]
        
        for spin_box in spin_boxes:
            # 设置小数位数和步进值
            spin_box.setDecimals(6)
            spin_box.setSingleStep(0.000001)
            
            # 移除数值范围限制
            spin_box.setMinimum(-float('inf'))
            spin_box.setMaximum(float('inf'))
            
            # 设置最小宽度以确保显示完整数值
            spin_box.setMinimumWidth(100)  # 可根据需要调整

    def _init_timers(self):
        """
        初始化多级刷新定时器
        采用三级刷新机制：
        1. 高频数据(100Hz)：里程计等快速变化数据
        2. 中频数据(50Hz)：状态信息等中等速度数据
        3. 低频数据(1Hz)：心跳等慢速数据
        """
        # 高频定时器 (≈100Hz)
        self._high_freq_timer = QTimer()
        self._high_freq_timer.timeout.connect(self._update_high_freq_ui)
        self._high_freq_timer.start(10)  
        
        # 中频定时器 (≈50Hz)
        self._mid_freq_timer = QTimer()
        self._mid_freq_timer.timeout.connect(self._update_mid_freq_ui)
        self._mid_freq_timer.start(20)  
        
        # 低频定时器 (1Hz)
        self._low_freq_timer = QTimer()
        self._low_freq_timer.timeout.connect(self._check_heartbeat)
        self._low_freq_timer.start(1000)

    # ==================== 数据接收与处理 ====================
    @pyqtSlot(str, object, int)
    def on_raw_data(self, name, raw_data, priority):
        """
        数据接收槽函数
        参数:
            name: 数据类型名称
            raw_data: 原始数据 (msg, transfer)
            priority: 数据优先级 (0:高频, 1:中频, 2:低频)
        """
        now = time.time()
        self._last_update_time[name] = now  # 记录最后更新时间
        
        # 根据优先级分类存储
        if priority == 2:
            self._update_low_freq_ui(name, raw_data)  # 低频直接处理
        elif priority == 1:
            self._mid_freq_buffer.append({          # 中频存入缓冲区
                "name": name,
                "data": raw_data,
                "timestamp": now
            })
        else:
            self._high_freq_buffer.append({           # 高频存入缓冲区
                "name": name,
                "data": raw_data,
                "timestamp": now
            })

    # ==================== UI更新方法 ====================
    def _update_high_freq_ui(self):
        """处理并更新高频数据UI"""
        if not self._high_freq_buffer:
            return

        # 获取最新数据
        latest_data = {}
        for item in reversed(self._high_freq_buffer):
            name_lower = item["name"].lower()
            if name_lower not in latest_data:
                latest_data[name_lower] = item["data"]

        # 分类处理
        for data_type, raw_data in latest_data.items():
            if data_type == "odometry":
                self._handle_odometry(raw_data)

    def _update_mid_freq_ui(self):
        """处理并更新中频数据UI"""
        if not self._mid_freq_buffer:
            return

        for item in self._mid_freq_buffer:
            name_lower = item["name"].lower()
            if name_lower == "binarysignal":
                self._handle_binary_signal(item["data"])
            elif name_lower == "motorstatus":
                self._handle_motor_status(item["data"])

    def _update_low_freq_ui(self, name, raw_data):
        """处理并更新低频数据UI"""
        try:
            if name.lower() == "heartbeat":
                msg, transfer = raw_data
                self.ui.lineEdit_5_1.setText(str(transfer.source_node_id))
                self.ui.lineEdit_5_2.setText(str(msg.mode.value))
                self._last_update_time["heartbeat"] = time.time()
        except Exception as e:
            print(f"低频数据处理异常 ({name}): {e}")

    # ==================== 数据处理器 ====================
    def _handle_odometry(self, raw_data):
        """里程计数据处理"""
        try:
            msg, _ = raw_data
            timestamp = time.time()

            # 更新UI
            self.ui.lineEdit_6_1.setText(f"{msg.current_velocity[0].meter_per_second:.3f}")
            self.ui.lineEdit_6_2.setText(f"{msg.current_velocity[1].meter_per_second:.3f}")
            self.ui.lineEdit_7_1.setText(f"{msg.odometry[0].meter:.3f}")
            self.ui.lineEdit_7_2.setText(f"{msg.odometry[1].meter:.3f}")

            # 记录数据
            csv_line = (
                f"timestamp:{timestamp:.6f},"
                f"v_l:{msg.current_velocity[0].meter_per_second:.3f},"
                f"v_r:{msg.current_velocity[1].meter_per_second:.3f},"
                f"o_l:{msg.odometry[0].meter:.3f},"
                f"o_r:{msg.odometry[1].meter:.3f}\n"
            )
            with open("./MotorAsst/output/odom.csv", "a") as f:
                f.write(csv_line)
        except Exception as e:
            print(f"里程计处理异常: {e}")

    def _handle_binary_signal(self, raw_data):
        """二进制信号处理"""
        msg, _ = raw_data
        device_name = bytes(msg.name.value.tobytes()).decode('utf-8').rstrip('\x00')
        # print(f"[高频] 二进制信号 - 设备: {device_name}, 状态: {msg.state}")
        if msg.state == 0:
            self.ui.lineEdit_3.setText("抱闸中")
        elif msg.state == 1:
            self.ui.lineEdit_3.setText("抱闸解除")
        else:
            self.ui.lineEdit_3.setText("未知状态")  # 异常状态处理
            
    def _handle_motor_status(self, raw_data):
        """电机状态处理"""
        try:
            msg, _ = raw_data
            # print(f"{msg.driver_input_current.ampere:.3f}A")
            # print(f"{msg.voltage.volt:.3f}V")
            # print(f"{msg.driver_max_temperature.kelvin:.1f}K")
            # print(f"Mode: {msg.mode}")
            # print(f"Status: {msg.status}")
            if msg.status == 0:
                self.ui.lineEdit_2.setText("初始化")
            elif msg.status == 1:
                self.ui.lineEdit_2.setText("停止")
            elif msg.status == 2:
                self.ui.lineEdit_2.setText("运行")
            elif msg.status == 3:
                self.ui.lineEdit_2.setText("抱闸")
            else:
                self.ui.lineEdit_2.setText("未知状态")

        except Exception as e:
            print(f"电机状态处理异常: {e}")

    # ==================== 其他功能方法 ====================
    def _check_heartbeat(self):
        """心跳检测"""
        if time.time() - self._last_update_time.get("heartbeat", 0) > 2.0:
            self.ui.lineEdit_5_1.setText("×××")
            self.ui.lineEdit_5_2.setText("断线")

    def _setup_button_connections(self):
        """设置按钮信号连接"""
        self.ui.pushButton.clicked.connect(self._on_target_set_clicked)
        self.ui.pushButton_3.clicked.connect(self._on_target_clear_clicked)
        self.ui.pushButton_2.clicked.connect(self._on_pid_set_clicked)  # 新增PID设置按钮连接

    # ==================== 事件处理器 ====================
    def _on_pid_set_clicked(self):
        """PID参数设置事件"""
        try:
            params = {
                "kp": self.ui.doubleSpinBox.value(),
                "ki": self.ui.doubleSpinBox_2.value(), 
                "kd": self.ui.doubleSpinBox_3.value()
            }
            self.pidParamsRequested.emit(params)  # 发射信号
        except Exception as e:
            print(f"获取PID参数错误: {e}")

    def _on_target_set_clicked(self):
        """目标值设置事件"""
        try:
            left_val = float(self.ui.lineEdit.text())
            right_val = float(self.ui.lineEdit.text())  # 假设使用同一个文本框值
            values = {
                "left": left_val,
                "right": right_val
            }
            self.targetValueRequested.emit(values)
        except ValueError as e:
            print(f"目标值设置错误: {e}")

    def _on_target_clear_clicked(self):
        """目标值清除事件"""
        self.targetClearRequested.emit()

    def _on_operation_mode_changed(self, checked, mode):
        """操作模式变更事件"""
        if checked:
            self.operationModeChanged.emit(mode)
            # self.ui.lineEdit_5_3.setText(mode.capitalize())
    def _on_control_mode_changed(self, checked, mode):
        """控制模式变更事件"""
        if checked:
            self.controlModeChanged.emit(mode)            