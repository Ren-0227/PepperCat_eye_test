#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口界面
"""

import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QLineEdit, QProgressBar,
    QFrame, QGridLayout, QMessageBox, QComboBox, QInputDialog, QApplication,
    QStackedLayout, QPushButton, QLabel, QWidget, QVBoxLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSize, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush

from src.agent.pet_agent import PetAgent
from src.ui.pet_widget import PetWidget
from src.ui.upgrade_machine import UpgradeMachine
from src.ui.bubble_menu import BubbleMenu
from src.ui.ai_command_dialog import AICommandDialog

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.pet_agent = PetAgent("PepperCat")
        self.upgrade_machine_widget = None  # 升级机器窗口实例
        self.upgrade_machine_visible = False
        self.follow_mouse_enabled = False  # 跟随鼠标开关
        self.follow_target_pos = None      # 跟随目标点
        self.init_ui()
        self.setup_timers()
        # 跟随鼠标定时器
        self.follow_timer = QTimer(self)
        self.follow_timer.timeout.connect(self.follow_mouse_step)
        self.follow_timer.start(30)
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("智能桌宠 - PepperCat")
        self.setGeometry(100, 100, 400, 400)
        self.setMinimumSize(200, 200)
        
        # 设置无边框和背景透明
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # 拖动相关
        self._drag_active = False
        self._drag_position = QPoint()
        
        # 只保留桌宠本体和点击事件，其他内容后续用气泡弹出
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCentralWidget(central_widget)
        self.stacked_layout = QStackedLayout(central_widget)

        # 登录界面
        login_widget = QWidget()
        login_layout = QVBoxLayout(login_widget)
        login_layout.setContentsMargins(0, 0, 0, 0)
        login_layout.setSpacing(0)
        login_layout.addSpacing(30)
        # 顶部PepperCat静态图片
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets', 'peppercat')
        sheet_path = os.path.join(asset_dir, 'walk.png')
        if os.path.exists(sheet_path):
            sheet = QPixmap(sheet_path)
            # 取第一帧
            frame = sheet.copy(0, 0, 160, 160)
        else:
            frame = QPixmap(160, 160)
        img_label = QLabel()
        img_label.setPixmap(frame)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setStyleSheet("background: rgba(255,255,255,0.15); border-radius: 32px;")
        img_label.setFixedSize(180, 180)
        login_layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignCenter)
        # 名字
        name_label = QLabel("PepperCat")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("font-size: 22px; color: #3a4a5a; font-weight: bold; margin-top: 8px;")
        login_layout.addWidget(name_label)
        # 欢迎语
        welcome_label = QLabel("欢迎来到peppercat的像素世界！")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 15px; color: #6a7a8a; margin-bottom: 12px;")
        login_layout.addWidget(welcome_label)
        login_layout.addSpacing(10)
        # 开始按钮
        start_btn = QPushButton("开始")
        start_btn.setStyleSheet("font-size:20px; padding:12px 32px; border-radius: 18px; background: #e6f7ff;")
        start_btn.clicked.connect(self.show_pet_only)
        login_layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        login_layout.addSpacing(30)
        self.stacked_layout.addWidget(login_widget)

        # 桌宠动图界面
        pet_widget_container = QWidget()
        pet_layout = QVBoxLayout(pet_widget_container)
        pet_layout.setContentsMargins(0, 0, 0, 0)
        pet_layout.setSpacing(0)
        self.pet_widget = PetWidget(self.pet_agent)
        self.pet_widget.setFixedSize(300, 300)
        self.pet_widget.setStyleSheet("background: rgba(255,255,255,0.15); border-radius: 32px;")
        pet_layout.addWidget(self.pet_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        self.stacked_layout.addWidget(pet_widget_container)

        # 加载PepperCat走路动画（spritesheet切割）
        self.pet_widget.set_spritesheet_animation(sheet_path, frame_width=160, frame_height=160, rows=2, cols=1)
        self.pet_widget.set_pet_name('PepperCat')
        self.pet_widget.doubleClicked.connect(self.on_pet_double_clicked)
        self.pet_widget.dragged.connect(self.move)
        self.pet_widget.dragged_global.connect(self.on_pet_dragged_global)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 已无exit_btn，无需处理
    
    def create_pet_area(self, parent_layout):
        """创建桌宠显示区域"""
        pet_frame = QFrame()
        pet_frame.setFrameStyle(QFrame.Shape.Box)
        pet_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
            }
        """)
        
        pet_layout = QVBoxLayout(pet_frame)
        
        # 桌宠显示组件
        self.pet_widget = PetWidget(self.pet_agent)
        pet_layout.addWidget(self.pet_widget)
        
        # 状态信息
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        status_layout = QGridLayout(status_frame)
        
        # 状态标签
        self.status_labels = {}
        status_items = [
            ("心情", "happiness"),
            ("精力", "energy"), 
            ("饥饿", "hunger"),
            ("健康", "health")
        ]
        
        for i, (label_text, key) in enumerate(status_items):
            label = QLabel(f"{label_text}:")
            label.setFont(QFont("Arial", 10))
            status_layout.addWidget(label, i, 0)
            
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(50)
            progress.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {self.get_progress_color(key)};
                }}
            """)
            status_layout.addWidget(progress, i, 1)
            
            self.status_labels[key] = progress
        
        pet_layout.addWidget(status_frame)
        parent_layout.addWidget(pet_frame, 2)
        
    def create_control_panel(self, parent_layout):
        """创建控制面板"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Shape.Box)
        control_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        control_layout = QVBoxLayout(control_frame)
        
        # 标题
        title = QLabel("互动控制")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(title)
        
        # 互动按钮
        self.create_interaction_buttons(control_layout)
        
        # 聊天区域
        self.create_chat_area(control_layout)
        
        # 移除信息显示区域（info area）
        # self.create_info_area(control_layout)
        
        parent_layout.addWidget(control_frame, 1)
        
    def create_interaction_buttons(self, parent_layout):
        """创建互动按钮"""
        button_frame = QFrame()
        button_layout = QGridLayout(button_frame)
        
        # 基础互动按钮
        buttons = [
            ("抚摸", self.pet_pet),
            ("玩耍", self.play_with_pet),
            ("睡觉", self.put_pet_to_sleep),
            ("喂食", self.feed_pet)
        ]
        
        for i, (text, slot) in enumerate(buttons):
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            button_layout.addWidget(btn, i // 2, i % 2)
        
        # 强化学习升级按钮
        upgrade_btn = QPushButton("🤖 强化学习升级")
        upgrade_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E55A2B;
            }
        """)
        upgrade_btn.clicked.connect(self.open_upgrade_machine)
        button_layout.addWidget(upgrade_btn, 2, 0, 1, 2)  # 跨越两列
        
        parent_layout.addWidget(button_frame)
        
    def create_chat_area(self, parent_layout):
        """创建聊天区域"""
        chat_frame = QFrame()
        chat_layout = QVBoxLayout(chat_frame)
        
        # 聊天输入
        chat_label = QLabel("和宠物聊天:")
        chat_layout.addWidget(chat_label)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("输入你想说的话...")
        self.chat_input.returnPressed.connect(self.send_chat)
        chat_layout.addWidget(self.chat_input)
        
        # 发送按钮
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(self.send_chat)
        chat_layout.addWidget(send_btn)
        
        parent_layout.addWidget(chat_frame)
        
    # 移除 create_info_area 方法及相关属性（info_display, insights_display, emotion_display）
    
    def setup_timers(self):
        """设置定时器"""
        # 更新宠物状态
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_pet_status)
        self.update_timer.start(1000)  # 每秒更新一次
        
    def update_pet_status(self):
        """更新宠物状态"""
        self.pet_agent.update()
        self.pet_agent.update_activity_info()
        
        # 检查是否需要主动互动
        active_message = self.pet_agent.check_activity_triggers()
        if active_message:
            self.add_info_message(active_message)
        
        self.pet_widget.update_animation()
        # self.update_activity_display()  # 移除活动监控显示
        self.update_insights_display()
        self.update_emotion_display()
    
    def get_progress_color(self, key, value=None):
        """获取进度条颜色"""
        if value is None:
            value = 0.5
            
        if key == "happiness":
            if value > 0.7:
                return "#28a745"  # 绿色
            elif value > 0.4:
                return "#ffc107"  # 黄色
            else:
                return "#dc3545"  # 红色
        elif key == "energy":
            if value > 0.6:
                return "#007bff"  # 蓝色
            elif value > 0.3:
                return "#ffc107"  # 黄色
            else:
                return "#dc3545"  # 红色
        elif key == "hunger":
            if value < 0.3:
                return "#28a745"  # 绿色
            elif value < 0.7:
                return "#ffc107"  # 黄色
            else:
                return "#dc3545"  # 红色
        elif key == "health":
            if value > 0.7:
                return "#28a745"  # 绿色
            elif value > 0.4:
                return "#ffc107"  # 黄色
            else:
                return "#dc3545"  # 红色
        else:
            return "#6c757d"  # 灰色
    
    def update_insights_display(self):
        """更新用户习惯洞察显示（已弃用，全部通过气泡菜单展示）"""
        pass
    def update_emotion_display(self):
        """更新情感分析显示（已弃用，全部通过气泡菜单展示）"""
        pass
    def add_info_message(self, message):
        """添加信息消息（已弃用，全部通过气泡菜单展示）"""
        pass
    
    def pet_pet(self):
        """抚摸宠物"""
        self.pet_widget.trigger_interaction('pet')
        response = self.pet_agent.interact("pet")
        self.add_info_message(response)
        
    def play_with_pet(self):
        """和宠物玩耍"""
        self.pet_widget.trigger_interaction('excited')
        response = self.pet_agent.interact("play")
        self.add_info_message(response)
        
    def put_pet_to_sleep(self):
        """让宠物睡觉"""
        self.pet_widget.trigger_interaction('sleep')
        response = self.pet_agent.interact("sleep")
        self.add_info_message(response)
        
    def feed_pet(self):
        """喂食宠物"""
        self.pet_widget.trigger_interaction('hungry')
        foods = ["苹果", "胡萝卜", "鱼", "鸡肉", "狗粮", "猫粮", "面包", "牛奶"]
        food, ok = QInputDialog.getItem(
            self, "选择食物", "请选择要喂的食物:", foods, 0, False
        )
        if ok and food:
            response = self.pet_agent.interact("feed", food=food)
            self.add_info_message(response)
    
    def send_chat(self):
        """发送聊天消息"""
        message = self.chat_input.text().strip()
        if message:
            response = self.pet_agent.interact("chat", message=message)
            self.add_info_message(f"你说: {message}")
            self.add_info_message(response)
            self.chat_input.clear() 

    def open_upgrade_machine(self):
        print("打开升级装置窗口")
        """打开强化学习升级装置"""
        if not hasattr(self, 'upgrade_machine'):
            self.upgrade_machine = UpgradeMachine(self.pet_agent, parent=self)
            self.upgrade_machine.training_started.connect(self.on_training_started)
            self.upgrade_machine.training_finished.connect(self.on_training_finished)
        # 恢复右上角定位
        screen = self.screen()
        if screen is not None:
            geo = screen.geometry()
            w, h = 320, 320
            self.upgrade_machine.setGeometry(geo.right()-w-20, geo.top()+20, w, h)
            print(f"屏幕geometry: {geo}")
            print(f"升级装置geometry: {self.upgrade_machine.geometry()}")
        self.upgrade_machine.show()
        self.upgrade_machine.raise_()
        self.upgrade_machine.activateWindow()
    
    def on_training_started(self):
        """训练开始回调"""
        self.add_info_message("🤖 桌宠开始强化学习训练...")
    
    def on_training_finished(self):
        """训练完成回调"""
        self.add_info_message("🎉 桌宠强化学习训练完成！现在更智能了！")
        # 获取训练后的RL引擎
        rl_engine = self.upgrade_machine.get_rl_engine()
        # 应用训练结果到桌宠
        self.pet_agent.set_rl_engine(rl_engine)
        self.add_info_message("🤖 桌宠已应用强化学习模型，行为更加智能！") 

    def on_pet_double_clicked(self, event):
        # 右键点击直接切换跟随状态
        if event.button() == Qt.MouseButton.RightButton:
            self.toggle_follow_mouse()
            return
            
        # 左键双击弹出气泡菜单
        if hasattr(self, 'bubble_menu') and self.bubble_menu.isVisible():
            self.bubble_menu.hide_with_animation()
            return
        window_title = self.pet_agent.current_window_title
        activity_info = f"窗口: {window_title}"
        from PyQt6.QtWidgets import QApplication
        from src.ui.ai_command_dialog import AICommandDialog
        
        actions = [
            ("抚摸", self.pet_pet),
            ("喂食", self.feed_pet),
            ("玩耍", self.play_with_pet),
            ("睡觉", self.put_pet_to_sleep),
            ("查看属性", self.show_pet_stats),
            ("升级", self.open_upgrade_machine),
            ("⚔️ 对战模式", self.open_battle_dialog),
            ("🐾 跟随鼠标" + ("（已开启）" if self.follow_mouse_enabled else ""), self.toggle_follow_mouse),
            ("🤖 智能命令", lambda: AICommandDialog(self).exec()),
            ("❌ 退出", lambda: QApplication.instance().quit() if QApplication.instance() is not None else None)
        ]
        def dummy(): pass
        actions = [(activity_info, dummy)] + actions
        self.bubble_menu = BubbleMenu(actions=actions)
        pet_center = self.pet_widget.mapToGlobal(self.pet_widget.rect().center())
        menu_x = pet_center.x() + 60
        menu_y = pet_center.y() - 40
        self.bubble_menu.show_at(QPoint(menu_x, menu_y))
    
    def toggle_follow_mouse(self):
        """切换跟随鼠标状态"""
        self.follow_mouse_enabled = not self.follow_mouse_enabled
        if self.follow_mouse_enabled:
            self.follow_timer.start(20)  # 50fps
            # 显示跟随状态提示
            self.show_follow_status("跟随已开启")
        else:
            self.follow_timer.stop()
            # 显示跟随状态提示
            self.show_follow_status("跟随已关闭")
    
    def show_follow_status(self, message):
        """显示跟随状态提示"""
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtCore import QTimer
        
        # 创建状态提示标签
        status_label = QLabel(message, self)
        status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 8px 16px;
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        status_label.adjustSize()
        
        # 定位到桌宠中心上方
        pet_center = self.pet_widget.mapToGlobal(self.pet_widget.rect().center())
        local_center = self.mapFromGlobal(pet_center)
        status_label.move(local_center.x() - status_label.width() // 2, 
                         local_center.y() - status_label.height() - 60)
        
        status_label.show()
        
        # 2秒后自动隐藏
        timer = QTimer(self)
        timer.timeout.connect(status_label.deleteLater)
        timer.timeout.connect(timer.deleteLater)
        timer.start(2000)

    def toggle_upgrade_machine_widget(self):
        if self.upgrade_machine_widget is None:
            self.upgrade_machine_widget = UpgradeMachine(self.pet_agent)
            # 右上角定位
            screen = self.screen()
            if screen is not None:
                geo = screen.geometry()
                w, h = 320, 220
                self.upgrade_machine_widget.setGeometry(geo.right()-w-20, geo.top()+20, w, h)
        self.upgrade_machine_visible = not self.upgrade_machine_visible
        if self.upgrade_machine_visible:
            self.upgrade_machine_widget.show()
            self.upgrade_machine_widget.raise_()
        else:
            self.upgrade_machine_widget.hide() 

    def on_pet_dragged_global(self, _):
        if self.upgrade_machine_widget and self.upgrade_machine_widget.isVisible():
            # 获取桌宠主窗口中心点的全局坐标
            center = self.geometry().center()
            global_center = self.mapToGlobal(center)
            self.upgrade_machine_widget.check_hover(global_center) 

    def start_pet_upgrade(self):
        self.open_upgrade_machine()
        # 计算升级装置圆环中心的全局坐标
        ring_cx = self.upgrade_machine.width() // 2
        ring_cy = self.upgrade_machine.height() // 2 - 20
        global_target = self.upgrade_machine.mapToGlobal(QPoint(ring_cx, ring_cy+20))
        # 平滑动画移动主窗口到该位置
        win_rect = self.geometry()
        new_rect = QRect(win_rect)
        new_rect.moveCenter(global_target)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(800)
        self.anim.setStartValue(win_rect)
        self.anim.setEndValue(new_rect)
        self.anim.start()

    def cancel_pet_upgrade(self):
        # 让宠物窗口平滑移动到升级机下方
        from PyQt6.QtCore import QPropertyAnimation, QRect, QPoint
        win_rect = self.geometry()
        # 目标点：升级机下方偏移
        if self.upgrade_machine_widget:
            machine_geo = self.upgrade_machine_widget.geometry()
            target = QPoint(machine_geo.center().x(), machine_geo.bottom() + 100)
        else:
            target = QPoint(win_rect.center().x(), win_rect.bottom() + 100)
        new_rect = QRect(win_rect)
        new_rect.moveCenter(target)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(800)
        self.anim.setStartValue(win_rect)
        self.anim.setEndValue(new_rect)
        self.anim.start()

    def show_pet_stats(self):
        from PyQt6.QtWidgets import QMessageBox
        stats = self.pet_agent.get_stats_summary()
        QMessageBox.information(self, "宠物属性", stats)
    
    def open_battle_dialog(self):
        """打开对战对话框"""
        from src.ui.battle_dialog import BattleDialog
        battle_dialog = BattleDialog(pet_name=self.pet_agent.name, parent=self)
        battle_dialog.exec() 

    def follow_mouse_step(self):
        """让宠物跟随鼠标移动，并播放走路动画"""
        if not self.follow_mouse_enabled or not self.pet_widget.isVisible():
            return
        from PyQt6.QtGui import QCursor
        mouse_pos = QCursor.pos()
        win = self.windowHandle()
        if win:
            geo = win.geometry()
            pet_center = geo.center()
            dx = mouse_pos.x() - pet_center.x()
            dy = mouse_pos.y() - pet_center.y()
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist > 10:
                nx = geo.x() + int(dx * 0.1)
                ny = geo.y() + int(dy * 0.1)
                self.move(nx, ny)
                self.pet_widget.play_png_animation(dx=dx)
            else:
                self.pet_widget.stop_png_animation()

    def upload_voice(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import shutil
        file, _ = QFileDialog.getOpenFileName(self, "选择语音文件", "", "音频文件 (*.wav *.mp3)")
        if file:
            try:
                shutil.copy(file, "user_voice.wav")
                QMessageBox.information(self, "成功", "语音样本已上传！后续桌宠语音将尝试模仿您的音色。")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"上传失败: {e}") 

    def record_voice_dialog(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
        import threading
        class RecordDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("录制语音样本")
                self.setFixedSize(320, 180)
                layout = QVBoxLayout(self)
                self.label = QLabel("点击下方按钮开始录音\n建议录制10秒以上清晰语音")
                layout.addWidget(self.label)
                self.record_btn = QPushButton("开始录音")
                self.stop_btn = QPushButton("停止并保存")
                self.stop_btn.setEnabled(False)
                layout.addWidget(self.record_btn)
                layout.addWidget(self.stop_btn)
                self.record_btn.clicked.connect(self.start_record)
                self.stop_btn.clicked.connect(self.stop_record)
                self.is_recording = False
                self.audio = None
                self.fs = 16000
            def start_record(self):
                import sounddevice as sd
                self.is_recording = True
                self.label.setText("录音中...点击停止保存")
                self.record_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.audio = []
                def callback(indata, frames, time, status):
                    if self.is_recording:
                        self.audio.append(indata.copy())
                self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=callback)
                self.stream.start()
            def stop_record(self):
                import numpy as np
                from scipy.io.wavfile import write
                self.is_recording = False
                self.stream.stop()
                self.stream.close()
                audio_np = np.concatenate(self.audio, axis=0)
                write("user_voice.wav", self.fs, (audio_np * 32767).astype(np.int16))
                self.label.setText("录音已保存为user_voice.wav")
                self.record_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                QMessageBox.information(self, "成功", "录音已保存！后续桌宠语音将尝试模仿您的音色。")
                self.accept()
        dlg = RecordDialog(self)
        dlg.exec() 

    def show_pet_only(self):
        self.stacked_layout.setCurrentIndex(1)
        self.follow_mouse_enabled = True
        self.follow_timer.start(30) 

    def showEvent(self, event):
        super().showEvent(event)
        # 居中显示窗口
        screen = self.screen() if hasattr(self, 'screen') else None
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is not None:
            screen_geo = screen.geometry()
            win_geo = self.frameGeometry()
            center_point = screen_geo.center()
            win_geo.moveCenter(center_point)
            self.move(win_geo.topLeft()) 

    def keyPressEvent(self, event):
        key = event.key()
        if hasattr(self, 'pet_widget') and self.pet_widget.isVisible():
            self.pet_widget.handle_key_event(key)
        super().keyPressEvent(event) 