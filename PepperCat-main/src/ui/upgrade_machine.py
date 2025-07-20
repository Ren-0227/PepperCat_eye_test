#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强化学习升级装置界面
"""

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QFrame, QTextEdit, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QPoint, QPointF, QEvent
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPixmap, QDragEnterEvent, QDropEvent, QLinearGradient, QRadialGradient

from src.agent.rl_engine import RLEngine
import numpy as np
import math

class UpgradeMachine(QWidget):
    """强化学习升级装置"""

    training_started = pyqtSignal()  # 训练开始信号
    training_finished = pyqtSignal()  # 训练完成信号

    def __init__(self, pet_agent, parent=None):
        super().__init__(parent)
        self.pet_agent = pet_agent
        self.rl_engine = RLEngine()
        self.is_pet_in_machine = False
        self.training_timer = QTimer()
        self.training_timer.timeout.connect(self.update_training)
        self.training_progress = 0.0
        self.training_active = False
        self.glow_phase = 0.0
        self.glow_timer = QTimer(self)
        self.glow_timer.timeout.connect(self.update_glow)
        self.glow_timer.start(30)
        self.menu = None
        self.progress_bar = None
        self.stop_btn = None
        self.init_ui()

    def init_ui(self):
        # 调试用：加深色半透明背景和高亮边框
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumSize(320, 320)
        self.resize(320, 320)
        self.setStyleSheet("background: rgba(30,30,30,120); border: 2px solid #00ffe7;")
        # 调试用：加一个白色大号QLabel
        from PyQt6.QtWidgets import QLabel
        label = QLabel("升级装置", self)
        label.setStyleSheet("color: white; font-size: 24px;")
        label.move(20, 20)
        label.show()
        # 居中显示（在open_upgrade_machine里设置geometry）

    def update_glow(self):
        self.glow_phase += 0.04
        if self.glow_phase > 2*3.1415:
            self.glow_phase = 0.0
        self.update()

    # 注释掉/删除 create_drag_area, create_training_controls, create_training_status, create_log_area 及其调用和相关控件定义

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        # 1. 只绘制一个发光圆圈（能量环）
        ring_cx, ring_cy = w//2, h//2-20
        ring_r1, ring_r2 = 60, 80
        grad = QRadialGradient(QPointF(ring_cx, ring_cy), ring_r2)
        grad.setColorAt(0.7, QColor(0,255,255,180))
        grad.setColorAt(1.0, QColor(0,40,80,0))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(ring_cx, ring_cy), ring_r2, ring_r2)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0,255,255,220), 8))
        painter.drawEllipse(QPointF(ring_cx, ring_cy), ring_r1, ring_r1)
        # 2. 机械臂（极简）
        def draw_arm(base_x, base_y, flip):
            painter.save()
            painter.translate(base_x, base_y)
            if flip:
                painter.scale(-1, 1)
            # 臂1
            painter.setPen(QPen(QColor(180,180,200), 16, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(0, 0, 0, 60)
            # 关节1
            painter.setPen(QPen(QColor(120,220,255), 10))
            painter.drawPoint(0, 60)
            # 臂2
            painter.setPen(QPen(QColor(180,180,200), 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(0, 60, 30, 110)
            # 关节2
            painter.setPen(QPen(QColor(120,220,255), 8))
            painter.drawPoint(30, 110)
            # 夹爪
            painter.setPen(QPen(QColor(200,255,255), 6))
            painter.drawLine(30, 110, 40, 130)
            painter.drawLine(30, 110, 20, 130)
            painter.restore()
        draw_arm(ring_cx-90, ring_cy+30, False)
        draw_arm(ring_cx+90, ring_cy+30, True)
        # 3. 感应区高亮
        if getattr(self, '_highlight', False):
            painter.setBrush(QColor(0,255,255,60))
            painter.setPen(QPen(QColor(0,255,255,180), 4))
            painter.drawEllipse(QPointF(ring_cx, ring_cy+70), 50, 30)
    def mouseMoveEvent(self, event):
        # 检查鼠标是否在感应区
        ring_cx, ring_cy = self.width()//2, 80
        sense_rect = QRect(ring_cx-50, ring_cy+40, 100, 60)
        if sense_rect.contains(event.position().toPoint()):
            if not getattr(self, '_highlight', False):
                self._highlight = True
                self.show_upgrade_menu()
                self.update()
        else:
            if getattr(self, '_highlight', False):
                self._highlight = False
                self.hide_upgrade_menu()
                self.update()
        super().mouseMoveEvent(event)
    def leaveEvent(self, event):
        if getattr(self, '_highlight', False):
            self._highlight = False
            self.hide_upgrade_menu()
            self.update()
        super().leaveEvent(event)
    def eventFilter(self, obj, event):
        if obj == self.drag_frame:
            if event.type() == QEvent.Type.Enter:
                self.show_upgrade_menu()
            elif event.type() == QEvent.Type.Leave:
                self.hide_upgrade_menu()
        return super().eventFilter(obj, event)

    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.drag_label.setText("✅ 松开桌宠以升级")
            self.drag_frame.setStyleSheet("background: rgba(0,255,255,0.08);")
            self.show_upgrade_menu()

    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        if not self.is_pet_in_machine:
            self.drag_label.setText("🛸 拖拽桌宠到这里升级")
            self.drag_frame.setStyleSheet("background: transparent;")
            self.hide_upgrade_menu()

    def dropEvent(self, event):
        """拖拽释放事件"""
        if event.mimeData().hasText():
            self.is_pet_in_machine = True
            self.drag_label.setText("🤖 桌宠已进入升级核心")
            self.start_button.setEnabled(True)
            self.log_message("桌宠已成功放入升级装置！")
            self.show_upgrade_menu()

    def start_training(self):
        self.hide_upgrade_menu()
        self._highlight = False
        self.update()
        # 显示进度条并自动强化学习
        if not hasattr(self, 'progress_bar') or self.progress_bar is None:
            from PyQt6.QtWidgets import QProgressBar
            self.progress_bar = QProgressBar(self)
            self.progress_bar.setGeometry(self.width()//2-80, self.height()-60, 160, 24)
            self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.training_progress = 0
        self.training_active = True
        self.training_timer.start(100)
    def update_training(self):
        if not getattr(self, 'training_active', False):
            return
        self.training_progress += 2
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setValue(int(self.training_progress))
        if self.training_progress >= 100:
            self.training_active = False
            self.training_progress = 0
            if hasattr(self, 'progress_bar') and self.progress_bar:
                self.progress_bar.hide()
            self.update()
    def stop_training(self):
        self.training_active = False
        self.training_progress = 0
        if self.progress_bar:
            self.progress_bar.hide()
        if self.stop_btn:
            self.stop_btn.hide()
        self.update()

    def save_model(self):
        """保存模型"""
        self.rl_engine.save_q_table()
        self.log_message("💾 模型已保存到 q_table.json")
        QMessageBox.information(self, "成功", "强化学习模型已保存！")

    def update_training(self):
        """更新训练状态"""
        if not self.rl_engine.is_training:
            self.training_finished.emit()
            return

        # 执行一步训练
        reward = self.rl_engine.train_step(self.pet_agent)

        # 更新界面
        status = self.rl_engine.get_training_status()
        self.progress_bar.setValue(int(status["progress"] * 100))
        self.episodes_label.setText(f"{status['episodes']} / {status['max_episodes']}")
        self.qtable_label.setText(f"{status['q_table_size']} 个状态")

        # 获取当前最佳动作
        best_action = self.rl_engine.get_best_action(self.pet_agent)
        action_names = {
            "pet": "抚摸", "feed": "喂食", "play": "玩耍", "chat": "聊天",
            "sleep": "睡觉", "observe": "观察", "comfort": "安慰", "encourage": "鼓励"
        }
        self.action_label.setText(action_names.get(best_action, best_action))

        # 记录日志
        if status["episodes"] % 100 == 0:
            self.log_message(f"训练进度: {status['episodes']}/{status['max_episodes']} (奖励: {reward:.2f})")

        # 检查是否完成
        if status["progress"] >= 1.0:
            self.training_completed()

    def training_completed(self):
        """训练完成"""
        self.rl_engine.is_training = False
        self.training_timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log_message("🎉 强化学习训练完成！桌宠已升级！")
        QMessageBox.information(self, "完成", "强化学习训练完成！\n你的桌宠现在更智能了！")
        self.training_finished.emit()

    def log_message(self, message: str):
        """记录日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")

        # 自动滚动到底部
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def get_rl_engine(self) -> RLEngine:
        """获取强化学习引擎"""
        return self.rl_engine

    def cancel_upgrade(self):
        self.is_pet_in_machine = False
        self.drag_label.setText("🛸 拖拽桌宠到这里升级")
        self.start_button.setEnabled(False)
        self.log_message("已取消升级。")
        self.drag_frame.setStyleSheet("background: transparent;")

    def show_upgrade_menu(self):
        if hasattr(self, 'menu') and self.menu is not None and self.menu.isVisible():
            return
        from src.ui.bubble_menu import BubbleMenu
        actions = [
            ("🚀 升级", self.start_training)
        ]
        self.menu = BubbleMenu(actions=actions)
        ring_cx, ring_cy = self.width()//2, self.height()//2-20
        ring_r2 = 80
        menu_width = self.menu.sizeHint().width() if hasattr(self.menu, 'sizeHint') else 120
        menu_x = self.mapToGlobal(QPoint(ring_cx, 0)).x() - menu_width//2
        menu_y = self.mapToGlobal(QPoint(ring_cx, ring_cy+ring_r2+40)).y()
        self.menu.show_at(QPoint(menu_x, menu_y))
        # 不再自动隐藏菜单，只有离开感应区时才隐藏

    def hide_upgrade_menu(self):
        if hasattr(self, 'menu') and self.menu is not None:
            self.menu.hide_with_animation()
            self.menu = None

    def show_confirm_menu(self):
        if hasattr(self, 'menu') and self.menu is not None and self.menu.isVisible():
            return
        from src.ui.bubble_menu import BubbleMenu
        actions = [
            ("✅ 确认升级", self.start_training),
            ("❌ 取消", self.on_cancel_upgrade)
        ]
        self.menu = BubbleMenu(actions=actions)
        ring_cx, ring_cy = self.width()//2, self.height()//2-20
        ring_r2 = 80
        menu_width = self.menu.sizeHint().width() if hasattr(self.menu, 'sizeHint') else 120
        menu_x = self.mapToGlobal(QPoint(ring_cx, 0)).x() - menu_width//2
        menu_y = self.mapToGlobal(QPoint(ring_cx, ring_cy+ring_r2+40)).y()
        self.menu.show_at(QPoint(menu_x, menu_y))

    def on_cancel_upgrade(self):
        # 关闭菜单
        self.hide_upgrade_menu()
        # 停止训练/进度条
        self.training_active = False
        if self.progress_bar:
            self.progress_bar.hide()
        # 通知主窗口让宠物跑下来
        main_window = self.parent()
        if main_window and hasattr(main_window, 'cancel_pet_upgrade'):
            main_window.cancel_pet_upgrade()
        # 恢复升级机状态
        self.is_pet_in_machine = False
        if hasattr(self, 'drag_label'):
            self.drag_label.setText("🛸 拖拽桌宠到这里升级")
        if hasattr(self, 'start_button'):
            self.start_button.setEnabled(False)
        if hasattr(self, 'drag_frame'):
            self.drag_frame.setStyleSheet("background: transparent;")
        self.log_message("已取消升级。")

    def check_hover(self, global_pos):
        local = self.mapFromGlobal(global_pos)
        ring_cx, ring_cy = self.width()//2, self.height()//2-20
        sense_center = QPoint(ring_cx, ring_cy+70)
        sense_r = 90  # 放大感应区半径
        if (local - sense_center).manhattanLength() < sense_r:
            if not getattr(self, '_highlight', False) and not self.training_active:
                self._highlight = True
                self.show_upgrade_menu()
                self.update()
        else:
            if getattr(self, '_highlight', False):
                self._highlight = False
                self.hide_upgrade_menu()
                self.update() 