#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火球攻击效果演示
"""

import sys
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygon, QPixmap
import os

class FireballDemo(QMainWindow):
    """火球演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("火球攻击效果演示")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建演示按钮
        fireball_btn = QPushButton("🔥 发射火球")
        fireball_btn.clicked.connect(self.shoot_fireball)
        layout.addWidget(fireball_btn)
        
        lightning_btn = QPushButton("⚡ 发射闪电")
        lightning_btn.clicked.connect(lambda: self.shoot_attack("lightning"))
        layout.addWidget(lightning_btn)
        
        ice_btn = QPushButton("❄️ 发射冰霜")
        ice_btn.clicked.connect(lambda: self.shoot_attack("ice"))
        layout.addWidget(ice_btn)
        
        arrow_btn = QPushButton("🏹 发射弓箭")
        arrow_btn.clicked.connect(lambda: self.shoot_attack("arrow"))
        layout.addWidget(arrow_btn)
        
        # 特效列表
        self.effects = []
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c3e50, stop:1 #34495e);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9);
                border: none;
                border-radius: 5px;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                margin: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5dade2, stop:1 #3498db);
            }
        """)
    
    def shoot_fireball(self):
        """发射火球"""
        self.shoot_attack("fireball")
    
    def shoot_attack(self, attack_type):
        """发射攻击"""
        if attack_type == "arrow":
            # 弓箭从上方发射到下方
            start_pos = (self.width() // 2, 50)
            end_pos = (self.width() // 2, self.height() - 50)
            
            # 创建弓箭特效
            sprite = "arrow.png"
        elif attack_type == "fireball":
            # 火球从右边发射到左边
            start_pos = (self.width() - 50, self.height() // 2)
            end_pos = (50, self.height() // 2)
            sprite = "fireball.png"
        elif attack_type == "ice":
            # 冰霜从右边发射到左边
            start_pos = (self.width() - 50, self.height() // 2)
            end_pos = (50, self.height() // 2)
            sprite = "iceball.png"
        elif attack_type == "lightning":
            # 闪电从右边发射到左边
            start_pos = (self.width() - 50, self.height() // 2)
            end_pos = (50, self.height() // 2)
            sprite = "lighting.png"
        else:
            return
        
        effect = AttackSpriteEffect(start_pos, end_pos, sprite, self)
        effect.show()
        self.effects.append(effect)
        
        # 创建受击特效
        hit_effect = HitEffect((self.width() // 2, self.height() - 100), attack_type, self)
        hit_effect.show()
        self.effects.append(hit_effect)

class AttackSpriteEffect(QWidget):
    """通用攻击动画特效（2帧PNG）"""
    def __init__(self, start_pos, end_pos, sprite_name, parent=None):
        super().__init__(parent)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = start_pos
        self.progress = 0.0
        self.frame_index = 0
        self.frames = []
        self.load_frames(sprite_name)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        if parent:
            self.setGeometry(parent.geometry())
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(80)  # 12.5fps
    def load_frames(self, sprite_name):
        asset_dir = os.path.join(os.path.dirname(__file__), 'src', 'ui', 'assets', 'peppercat')
        sheet_path = os.path.join(asset_dir, sprite_name)
        sheet = QPixmap(sheet_path)
        w = sheet.width() // 2
        h = sheet.height()
        self.frames = [sheet.copy(i * w, 0, w, h) for i in range(2)]
    def update_animation(self):
        self.progress += 0.04  # 控制飞行速度
        self.frame_index = (self.frame_index + 1) % 2
        if self.progress >= 1.0:
            self.timer.stop()
            self.deleteLater()
            return
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * self.progress
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * self.progress
        self.current_pos = (int(x), int(y))
        self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.frames:
            frame = self.frames[self.frame_index]
            fw, fh = frame.width(), frame.height()
            x = self.current_pos[0] - fw // 2
            y = self.current_pos[1] - fh // 2
            painter.drawPixmap(x, y, frame)

class HitEffect(QWidget):
    """受击特效"""
    
    def __init__(self, hit_pos, attack_type="fireball", parent=None):
        super().__init__(parent)
        self.hit_pos = hit_pos
        self.attack_type = attack_type
        self.scale = 0.1
        self.alpha = 255
        self.progress = 0.0
        self.setup_animation()
        
        # 设置透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # 设置覆盖整个屏幕
        if parent:
            self.setGeometry(parent.geometry())
    
    def setup_animation(self):
        """设置动画"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # 60fps
    
    def update_animation(self):
        """更新动画"""
        self.progress += 0.03  # 每帧增加3%
        if self.progress >= 1.0:
            self.timer.stop()
            self.deleteLater()
            return
        
        # 更新缩放和透明度
        self.scale = 0.1 + (2.0 - 0.1) * self.progress
        self.alpha = 255 - 255 * self.progress
        self.update()
    
    def paintEvent(self, event):
        """绘制受击特效"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 根据攻击类型选择颜色
        alpha_int = int(self.alpha)
        if self.attack_type == "fireball":
            color = QColor(255, 100, 0, alpha_int)
        elif self.attack_type == "lightning":
            color = QColor(100, 150, 255, alpha_int)
        elif self.attack_type == "ice":
            color = QColor(100, 200, 255, alpha_int)
        elif self.attack_type == "arrow":
            color = QColor(139, 69, 19, alpha_int)  # 棕色
        else:
            color = QColor(255, 100, 0, alpha_int)
        
        # 绘制爆炸效果
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # 绘制多个圆形形成爆炸效果
        for i in range(8):
            angle = i * 45
            radius = 20 * self.scale
            x = self.hit_pos[0] + radius * (i % 2) * (1 if i < 4 else -1)
            y = self.hit_pos[1] + radius * (i % 2) * (1 if i > 4 else -1)
            painter.drawEllipse(int(x - 8), int(y - 8), 16, 16)

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建演示窗口
    demo = FireballDemo()
    demo.show()
    
    print("火球攻击效果演示")
    print("点击按钮查看不同的攻击效果")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 