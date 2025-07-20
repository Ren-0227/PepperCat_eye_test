#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
气泡菜单组件
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGraphicsOpacityEffect, QHBoxLayout
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from src.ui.pet_chat_dialog import PetChatDialog

class BubbleMenu(QWidget):
    """气泡菜单，支持动画弹出和自动消失"""
    def __init__(self, parent=None, actions=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMouseTracking(True)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(200)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_with_animation)
        self.pet_chat_dialog = None  # 懒加载
        self._setup_ui(actions or [])
    def _setup_ui(self, actions):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self.buttons = []
        # 分两列
        col1 = QVBoxLayout()
        col2 = QVBoxLayout()
        for i, (text, slot) in enumerate(actions):
            if text == "🤖 智能命令":
                # 替换为智能问答
                btn = QPushButton("💬 智能问答")
                btn.setStyleSheet('''
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e3f2fd, stop:1 #fff);
                        border: 2px solid #4CAF50;
                        border-radius: 22px;
                        padding: 10px 22px;
                        font-size: 18px;
                        color: #2d3a4b;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: #e6f7ff;
                        border: 2px solid #388E3C;
                        color: #388E3C;
                    }
                ''')
                btn.setFont(QFont("Arial", 15, QFont.Weight.Bold))
                btn.setFixedHeight(54)
                btn.clicked.connect(self.show_pet_chat_dialog)
            else:
                btn = QPushButton(text)
                btn.setStyleSheet('''
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fff, stop:1 #e0e0e0);
                        border: 2px solid #a0a0a0;
                        border-radius: 18px;
                        padding: 8px 18px;
                        font-size: 16px;
                        color: #333;
                    }
                    QPushButton:hover {
                        background: #f5f5f5;
                        border: 2px solid #4CAF50;
                        color: #4CAF50;
                    }
                ''')
                btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                btn.clicked.connect(slot)
            if i % 2 == 0:
                col1.addWidget(btn)
            else:
                col2.addWidget(btn)
            self.buttons.append(btn)
        layout.addLayout(col1)
        layout.addLayout(col2)
    def show_pet_chat_dialog(self):
        if self.pet_chat_dialog is None:
            self.pet_chat_dialog = PetChatDialog(self)
        self.pet_chat_dialog.show()
    def show_at(self, global_pos: QPoint):
        self.move(global_pos)
        self.show()
        self.raise_()
        self.opacity_anim.setDirection(QPropertyAnimation.Direction.Forward)
        self.opacity_anim.start()
        self.hide_timer.start(6000)  # 6秒后自动消失
    def hide_with_animation(self):
        self.opacity_anim.setDirection(QPropertyAnimation.Direction.Backward)
        self.opacity_anim.finished.connect(self.hide)
        self.opacity_anim.start()
    def mousePressEvent(self, event):
        # 点击菜单外部自动消失
        if not self.rect().contains(event.pos()):
            self.hide_with_animation()
        super().mousePressEvent(event)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        color = QColor(255, 255, 255, 230)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(180, 180, 180), 2))
        painter.drawRoundedRect(rect, 24, 24) 