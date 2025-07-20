#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对战界面
显示在线玩家和攻击效果
"""

import uuid
import random
import math
import time
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QFrame, QProgressBar,
    QMessageBox, QInputDialog, QComboBox, QGridLayout, QSlider
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPixmap, QPolygon, QMouseEvent

from src.network.battle_client import BattleClient
from src.network.battle_server import BattleServer

# 战斗规则配置
BATTLE_RULES = {
    "fireball": {
        "damage": 25,
        "cooldown": 2.0,  # 2秒冷却时间
        "burn_duration": 3.0,  # 灼烧持续3秒
        "burn_damage": 5,  # 每秒灼烧伤害
        "description": "火球攻击，造成灼烧效果"
    },
    "arrow": {
        "damage": 35,
        "cooldown": 3.0,  # 3秒冷却时间
        "description": "弓箭攻击，高伤害"
    },
    "lightning": {
        "damage": 20,
        "cooldown": 1.5,  # 1.5秒冷却时间
        "shock_duration": 4.0,  # 电击持续4秒
        "shock_damage": 3,  # 每秒电击伤害
        "description": "闪电攻击，造成持续电击效果"
    },
    "ice": {
        "damage": 15,
        "cooldown": 4.0,  # 4秒冷却时间
        "slow_duration": 5.0,  # 缓速持续5秒
        "slow_factor": 0.5,  # 移动速度减半
        "description": "冰霜攻击，造成缓速效果"
    }
}

class StatusEffect:
    """状态效果类"""
    
    def __init__(self, effect_type: str, duration: float, damage: int = 0, slow_factor: float = 1.0):
        self.effect_type = effect_type
        self.duration = duration
        self.remaining_time = duration
        self.damage = damage
        self.slow_factor = slow_factor
        self.start_time = time.time()
    
    def update(self, delta_time: float):
        """更新状态效果"""
        self.remaining_time -= delta_time
        return self.remaining_time > 0
    
    def get_damage(self) -> int:
        """获取当前伤害"""
        if self.effect_type in ["burn", "shock"]:
            return self.damage
        return 0
    
    def get_slow_factor(self) -> float:
        """获取缓速因子"""
        if self.effect_type == "slow":
            return self.slow_factor
        return 1.0

class FireballEffect(QFrame):
    """火球特效"""
    
    def __init__(self, start_pos, end_pos, attack_type="fireball", parent=None):
        super().__init__(parent)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = start_pos
        self.attack_type = attack_type
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
        self.progress += 0.02  # 每帧增加2%
        if self.progress >= 1.0:
            self.timer.stop()
            self.deleteLater()
            return
        
        # 计算当前位置
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * self.progress
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * self.progress
        self.current_pos = (int(x), int(y))
        self.update()
    
    def paintEvent(self, event):
        """绘制火球"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 根据攻击类型选择颜色
        if self.attack_type == "fireball":
            main_color = QColor(255, 100, 0)
            glow_color = QColor(255, 200, 0)
        elif self.attack_type == "lightning":
            main_color = QColor(100, 150, 255)
            glow_color = QColor(200, 220, 255)
        elif self.attack_type == "ice":
            main_color = QColor(100, 200, 255)
            glow_color = QColor(200, 230, 255)
        else:
            main_color = QColor(255, 100, 0)
            glow_color = QColor(255, 200, 0)
        
        # 绘制火球主体
        painter.setBrush(QBrush(main_color))
        painter.setPen(QPen(glow_color, 3))
        painter.drawEllipse(self.current_pos[0] - 12, self.current_pos[1] - 12, 24, 24)
        
        # 绘制发光效果
        painter.setPen(QPen(glow_color, 1))
        painter.drawEllipse(self.current_pos[0] - 16, self.current_pos[1] - 16, 32, 32)
        
        # 绘制尾迹
        for i in range(8):
            offset = i * 4
            alpha = 255 - i * 30
            if alpha > 0:
                color = QColor(main_color.red(), main_color.green(), main_color.blue(), alpha)
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(
                    self.current_pos[0] - offset - 6, 
                    self.current_pos[1] - 6, 
                    12, 12
                )

class ArrowEffect(QFrame):
    """弓箭特效"""
    
    def __init__(self, start_pos, end_pos, attack_type="arrow", angle=75, parent=None):
        super().__init__(parent)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = start_pos
        self.attack_type = attack_type
        self.angle = angle  # 发射角度（度）
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
        self.progress += 0.015  # 每帧增加1.5%，弓箭稍慢
        if self.progress >= 1.0:
            self.timer.stop()
            self.deleteLater()
            return
        
        # 计算当前位置（抛物线轨迹，考虑角度）
        angle_rad = math.radians(self.angle)
        distance = math.sqrt((self.end_pos[0] - self.start_pos[0])**2 + (self.end_pos[1] - self.start_pos[1])**2)
        
        # 水平距离
        x = self.start_pos[0] + distance * self.progress * math.cos(angle_rad)
        # 垂直距离（抛物线）
        height = 150  # 抛物线高度
        y = self.start_pos[1] - distance * self.progress * math.sin(angle_rad) + \
            math.sin(self.progress * math.pi) * height
        
        self.current_pos = (int(x), int(y))
        self.update()
    
    def paintEvent(self, event):
        """绘制弓箭"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 弓箭颜色
        arrow_color = QColor(139, 69, 19)  # 棕色
        tip_color = QColor(255, 215, 0)    # 金色箭头
        feather_color = QColor(255, 255, 255)  # 白色羽毛
        
        # 计算弓箭角度（指向目标）
        dx = self.end_pos[0] - self.start_pos[0]
        dy = self.end_pos[1] - self.start_pos[1]
        angle = math.atan2(dy, dx) * 180 / math.pi
        
        # 保存当前状态
        painter.save()
        painter.translate(self.current_pos[0], self.current_pos[1])
        painter.rotate(angle)
        
        # 绘制箭杆
        painter.setPen(QPen(arrow_color, 3))
        painter.drawLine(0, 0, 20, 0)
        
        # 绘制箭头
        painter.setBrush(QBrush(tip_color))
        painter.setPen(QPen(tip_color, 1))
        arrow_tip = QPoint(25, 0)
        arrow_points = QPolygon([
            QPoint(20, 0),
            QPoint(15, -3),
            QPoint(15, 3)
        ])
        painter.drawPolygon(arrow_points)
        
        # 绘制羽毛
        painter.setBrush(QBrush(feather_color))
        painter.setPen(QPen(feather_color, 1))
        painter.drawEllipse(-5, -2, 4, 4)
        painter.drawEllipse(-5, -6, 4, 4)
        painter.drawEllipse(-5, 2, 4, 4)
        painter.drawEllipse(-5, 6, 4, 4)
        
        # 恢复状态
        painter.restore()
        
        # 绘制尾迹（羽毛飘落效果）
        for i in range(5):
            offset = i * 3
            alpha = 255 - i * 50
            if alpha > 0:
                color = QColor(feather_color.red(), feather_color.green(), feather_color.blue(), alpha)
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(
                    self.current_pos[0] - offset - 2, 
                    self.current_pos[1] - 2, 
                    4, 4
                )

class HitEffect(QFrame):
    """受击特效"""
    
    def __init__(self, hit_pos, attack_type="fireball", parent=None):
        super().__init__(parent)
        self.hit_pos = hit_pos
        self.attack_type = attack_type
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
        self.progress += 0.05  # 每帧增加5%
        if self.progress >= 1.0:
            self.timer.stop()
            self.deleteLater()
            return
        self.update()
    
    def paintEvent(self, event):
        """绘制受击效果"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 根据攻击类型选择效果
        if self.attack_type == "fireball":
            # 火焰爆炸效果
            color = QColor(255, 100, 0, int(255 * (1 - self.progress)))
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            size = int(50 * (1 - self.progress * 0.5))
            painter.drawEllipse(self.hit_pos[0] - size//2, self.hit_pos[1] - size//2, size, size)
            
        elif self.attack_type == "lightning":
            # 闪电效果
            color = QColor(100, 150, 255, int(255 * (1 - self.progress)))
            painter.setPen(QPen(color, 3))
            for i in range(5):
                x = self.hit_pos[0] + random.randint(-20, 20)
                y = self.hit_pos[1] + random.randint(-20, 20)
                painter.drawLine(self.hit_pos[0], self.hit_pos[1], x, y)
                
        elif self.attack_type == "ice":
            # 冰霜效果
            color = QColor(100, 200, 255, int(255 * (1 - self.progress)))
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            size = int(40 * (1 - self.progress * 0.5))
            painter.drawEllipse(self.hit_pos[0] - size//2, self.hit_pos[1] - size//2, size, size)

class AttackSpriteEffect(QFrame):
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
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets', 'peppercat')
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

class BattleDialog(QDialog):
    """对战对话框"""
    
    def __init__(self, pet_name="小宠物", parent=None):
        super().__init__(parent)
        self.pet_name = pet_name
        self.player_id = str(uuid.uuid4())
        self.player_name = f"玩家_{random.randint(1000, 9999)}"
        
        # 网络组件
        self.battle_client = None
        self.battle_server = None
        
        # 玩家状态
        self.players = {}  # {player_id: {'name': str, 'health': int, 'position': tuple}}
        self.selected_target = None
        self.my_health = 100
        self.my_position = (400, 300)  # 我的位置
        
        # 攻击相关
        self.attack_angle = 75  # 弓箭角度
        self.attack_y_offset = 0  # 火球Y轴偏移
        
        # 移动相关
        self.moving_to_position = None
        self.move_animation = None
        self.move_progress = 0.0
        
        # 战斗规则相关
        self.attack_cooldowns = {}  # 攻击冷却时间
        self.status_effects = []  # 状态效果列表
        self.last_attack_time = {}  # 上次攻击时间
        
        # 初始化攻击冷却
        for attack_type in BATTLE_RULES:
            self.attack_cooldowns[attack_type] = 0.0
            self.last_attack_time[attack_type] = 0.0
        
        # 状态效果更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_effects)
        self.status_timer.start(100)  # 每100ms更新一次状态效果
        
        self.mode = 'ranged'  # 新增：模式，'ranged'或'melee'
        self.opponent_pet_state = None  # 新增：对方桌宠状态
        self.melee_attack_cooldown = 1.0  # 近战攻击冷却1秒
        self.last_melee_attack_time = 0.0
        self.melee_invincible = False
        self.melee_invincible_timer = QTimer()
        self.melee_invincible_timer.setSingleShot(True)
        self.melee_invincible_timer.timeout.connect(self.end_melee_invincible)
        self.melee_health = 100
        self.opponent_melee_health = 100
        self.melee_hit_log = []
        self.init_ui()
        self.setup_network()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("对战系统")
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(f"对战系统 - {self.pet_name}")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 网络控制
        network_frame = QFrame()
        network_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        network_layout = QHBoxLayout()
        
        self.create_room_btn = QPushButton("创建房间")
        self.create_room_btn.clicked.connect(self.create_room)
        network_layout.addWidget(self.create_room_btn)
        
        self.join_room_btn = QPushButton("加入房间")
        self.join_room_btn.clicked.connect(self.join_room)
        network_layout.addWidget(self.join_room_btn)
        
        self.status_label = QLabel("未连接")
        self.status_label.setStyleSheet("color: gray;")
        network_layout.addWidget(self.status_label)
        
        network_frame.setLayout(network_layout)
        layout.addWidget(network_frame)
        
        # 模式切换按钮
        mode_frame = QFrame()
        mode_layout = QHBoxLayout()
        self.mode_btn = QPushButton("切换为近战模式")
        self.mode_btn.clicked.connect(self.switch_mode)
        mode_layout.addWidget(self.mode_btn)
        self.melee_hint_label = QLabel("")
        mode_layout.addWidget(self.melee_hint_label)
        mode_frame.setLayout(mode_layout)
        layout.insertWidget(1, mode_frame)  # 插入到顶部
        
        # 玩家信息
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        info_layout = QHBoxLayout()
        
        # 我的信息
        my_info = QVBoxLayout()
        my_info.addWidget(QLabel(f"我: {self.player_name}"))
        self.my_health_bar = QProgressBar()
        self.my_health_bar.setRange(0, 100)
        self.my_health_bar.setValue(self.my_health)
        self.my_health_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        my_info.addWidget(self.my_health_bar)
        info_layout.addLayout(my_info)
        
        # 我的位置
        position_layout = QVBoxLayout()
        position_layout.addWidget(QLabel("我的位置:"))
        self.position_label = QLabel(f"({self.my_position[0]}, {self.my_position[1]})")
        position_layout.addWidget(self.position_label)
        info_layout.addLayout(position_layout)
        
        # 状态效果显示
        status_effects_layout = QVBoxLayout()
        status_effects_layout.addWidget(QLabel("状态效果:"))
        self.status_effects_label = QLabel("无")
        self.status_effects_label.setStyleSheet("color: #666; font-size: 12px;")
        status_effects_layout.addWidget(self.status_effects_label)
        info_layout.addLayout(status_effects_layout)
        
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        # 攻击控制
        attack_frame = QFrame()
        attack_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        attack_layout = QVBoxLayout()
        
        attack_layout.addWidget(QLabel("攻击控制:"))
        
        # 攻击按钮
        attack_buttons_layout = QHBoxLayout()
        
        self.fireball_btn = QPushButton("火球攻击")
        self.fireball_btn.clicked.connect(lambda: self.send_attack("fireball"))
        self.fireball_btn.setEnabled(False)
        attack_buttons_layout.addWidget(self.fireball_btn)
        
        self.arrow_btn = QPushButton("弓箭攻击")
        self.arrow_btn.clicked.connect(lambda: self.send_attack("arrow"))
        self.arrow_btn.setEnabled(False)
        attack_buttons_layout.addWidget(self.arrow_btn)
        
        self.lightning_btn = QPushButton("闪电攻击")
        self.lightning_btn.clicked.connect(lambda: self.send_attack("lightning"))
        self.lightning_btn.setEnabled(False)
        attack_buttons_layout.addWidget(self.lightning_btn)
        
        self.ice_btn = QPushButton("冰霜攻击")
        self.ice_btn.clicked.connect(lambda: self.send_attack("ice"))
        self.ice_btn.setEnabled(False)
        attack_buttons_layout.addWidget(self.ice_btn)
        
        attack_layout.addLayout(attack_buttons_layout)
        
        # 攻击参数控制
        params_layout = QHBoxLayout()
        
        # 火球Y轴偏移
        params_layout.addWidget(QLabel("火球Y轴偏移:"))
        self.y_offset_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_offset_slider.setRange(-100, 100)
        self.y_offset_slider.setValue(0)
        self.y_offset_slider.valueChanged.connect(self.on_y_offset_changed)
        params_layout.addWidget(self.y_offset_slider)
        self.y_offset_label = QLabel("0")
        params_layout.addWidget(self.y_offset_label)
        
        # 弓箭角度
        params_layout.addWidget(QLabel("弓箭角度:"))
        self.angle_slider = QSlider(Qt.Orientation.Horizontal)
        self.angle_slider.setRange(30, 90)
        self.angle_slider.setValue(75)
        self.angle_slider.valueChanged.connect(self.on_angle_changed)
        params_layout.addWidget(self.angle_slider)
        self.angle_label = QLabel("75°")
        params_layout.addWidget(self.angle_label)
        
        attack_layout.addLayout(params_layout)
        
        attack_frame.setLayout(attack_layout)
        layout.addWidget(attack_frame)
        
        # 移动控制
        move_frame = QFrame()
        move_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        move_layout = QVBoxLayout()
        
        move_layout.addWidget(QLabel("移动控制:"))
        move_layout.addWidget(QLabel("点击屏幕任意位置移动桌宠"))
        
        # 移动按钮
        move_buttons_layout = QHBoxLayout()
        
        self.move_to_center_btn = QPushButton("移动到中心")
        self.move_to_center_btn.clicked.connect(self.move_to_center)
        move_buttons_layout.addWidget(self.move_to_center_btn)
        
        self.move_to_corner_btn = QPushButton("移动到角落")
        self.move_to_corner_btn.clicked.connect(self.move_to_corner)
        move_buttons_layout.addWidget(self.move_to_corner_btn)
        
        move_layout.addLayout(move_buttons_layout)
        
        move_frame.setLayout(move_layout)
        layout.addWidget(move_frame)
        
        # 玩家列表
        players_frame = QFrame()
        players_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        players_layout = QVBoxLayout()
        
        players_layout.addWidget(QLabel("在线玩家:"))
        self.player_list = QListWidget()
        self.player_list.itemClicked.connect(self.on_player_selected)
        players_layout.addWidget(self.player_list)
        
        players_frame.setLayout(players_layout)
        layout.addWidget(players_frame)
        
        # 战斗日志
        log_frame = QFrame()
        log_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        log_layout = QVBoxLayout()
        
        log_layout.addWidget(QLabel("战斗日志:"))
        self.battle_log = QListWidget()
        self.battle_log.setMaximumHeight(150)
        log_layout.addWidget(self.battle_log)
        
        log_frame.setLayout(log_layout)
        layout.addWidget(log_frame)
        
        # 近战血条区
        self.melee_health_frame = QFrame()
        self.melee_health_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        melee_health_layout = QHBoxLayout()
        self.my_melee_health_bar = QProgressBar()
        self.my_melee_health_bar.setRange(0, 100)
        self.my_melee_health_bar.setValue(100)
        self.my_melee_health_bar.setFormat("我方血量: %v/%m")
        self.my_melee_health_bar.setStyleSheet("QProgressBar::chunk {background-color: #4CAF50;}")
        melee_health_layout.addWidget(self.my_melee_health_bar)
        self.opponent_melee_health_bar = QProgressBar()
        self.opponent_melee_health_bar.setRange(0, 100)
        self.opponent_melee_health_bar.setValue(100)
        self.opponent_melee_health_bar.setFormat("对方血量: %v/%m")
        self.opponent_melee_health_bar.setStyleSheet("QProgressBar::chunk {background-color: #e74c3c;}")
        melee_health_layout.addWidget(self.opponent_melee_health_bar)
        self.melee_health_frame.setLayout(melee_health_layout)
        self.melee_health_frame.setVisible(False)
        layout.insertWidget(2, self.melee_health_frame)
        
        self.setLayout(layout)
        
        # 设置鼠标事件
        self.setMouseTracking(True)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 获取点击位置
            pos = event.pos()
            self.move_pet_to_position(pos.x(), pos.y())
    
    def move_pet_to_position(self, x: int, y: int):
        """移动桌宠到指定位置"""
        target_pos = (x, y)
        self.moving_to_position = target_pos
        self.move_progress = 0.0
        
        # 发送移动消息
        if self.battle_client:
            self.battle_client.send_move(target_pos)
        
        # 开始移动动画
        self.start_move_animation()
        
        self.add_battle_log(f"移动到位置 ({x}, {y})")
    
    def start_move_animation(self):
        """开始移动动画"""
        if hasattr(self, 'move_animation') and self.move_animation is not None:
            self.move_animation.stop()
        
        self.move_animation = QTimer()
        self.move_animation.timeout.connect(self.update_move_animation)
        self.move_animation.start(16)  # 60fps
    
    def update_move_animation(self):
        """更新移动动画"""
        if not self.moving_to_position:
            return
        
        self.move_progress += 0.02  # 每帧移动2%
        
        if self.move_progress >= 1.0:
            # 移动完成
            self.my_position = self.moving_to_position
            self.moving_to_position = None
            self.move_animation.stop()
            self.position_label.setText(f"({self.my_position[0]}, {self.my_position[1]})")
            return
        
        # 计算当前位置
        start_x, start_y = self.my_position
        end_x, end_y = self.moving_to_position
        
        current_x = start_x + (end_x - start_x) * self.move_progress
        current_y = start_y + (end_y - start_y) * self.move_progress
        
        self.my_position = (int(current_x), int(current_y))
        self.position_label.setText(f"({self.my_position[0]}, {self.my_position[1]})")
    
    def move_to_center(self):
        """移动到屏幕中心"""
        center_x = self.width() // 2
        center_y = self.height() // 2
        self.move_pet_to_position(center_x, center_y)
    
    def move_to_corner(self):
        """移动到屏幕角落"""
        corner_x = self.width() - 100
        corner_y = self.height() - 100
        self.move_pet_to_position(corner_x, corner_y)
    
    def on_y_offset_changed(self, value):
        """Y轴偏移改变"""
        self.attack_y_offset = value
        self.y_offset_label.setText(str(value))
    
    def on_angle_changed(self, value):
        """角度改变"""
        self.attack_angle = value
        self.angle_label.setText(f"{value}°")
    
    def update_status_effects(self):
        """更新状态效果"""
        current_time = time.time()
        delta_time = 0.1  # 100ms
        
        # 更新状态效果
        active_effects = []
        total_damage = 0
        
        for effect in self.status_effects[:]:
            if not effect.update(delta_time):
                # 效果结束
                self.status_effects.remove(effect)
                self.add_battle_log(f"{effect.effect_type}效果结束")
            else:
                active_effects.append(effect)
                total_damage += effect.get_damage()
        
        # 应用持续伤害
        if total_damage > 0:
            self.my_health = max(0, self.my_health - total_damage)
            self.my_health_bar.setValue(self.my_health)
            self.add_battle_log(f"受到持续伤害: {total_damage}")
        
        # 更新状态效果显示
        if active_effects:
            effect_texts = []
            for effect in active_effects:
                remaining = effect.remaining_time
                if effect.effect_type == "burn":
                    effect_texts.append(f"灼烧({remaining:.1f}s)")
                elif effect.effect_type == "shock":
                    effect_texts.append(f"电击({remaining:.1f}s)")
                elif effect.effect_type == "slow":
                    effect_texts.append(f"缓速({remaining:.1f}s)")
            self.status_effects_label.setText(", ".join(effect_texts))
        else:
            self.status_effects_label.setText("无")
        
        # 更新攻击按钮冷却状态
        self.update_attack_buttons()
    
    def update_attack_buttons(self):
        """更新攻击按钮状态"""
        current_time = time.time()
        
        for attack_type, rules in BATTLE_RULES.items():
            cooldown_remaining = max(0, rules['cooldown'] - (current_time - self.last_attack_time.get(attack_type, 0)))
            
            if attack_type == "fireball":
                btn = self.fireball_btn
            elif attack_type == "arrow":
                btn = self.arrow_btn
            elif attack_type == "lightning":
                btn = self.lightning_btn
            elif attack_type == "ice":
                btn = self.ice_btn
            else:
                continue
            
            if cooldown_remaining > 0:
                btn.setText(f"{attack_type.title()}({cooldown_remaining:.1f}s)")
                btn.setEnabled(False)
            else:
                btn.setText(f"{attack_type.title()}")
                btn.setEnabled(True)

    def setup_network(self):
        """设置网络连接"""
        # 连接信号
        if self.battle_client:
            self.battle_client.player_joined.connect(self.on_player_joined)
            self.battle_client.player_left.connect(self.on_player_left)
            self.battle_client.attack_received.connect(self.on_attack_received)
            self.battle_client.server_disconnected.connect(self.on_server_disconnected)
            self.battle_client.opponent_melee_move.connect(self.on_opponent_melee_move)
            self.battle_client.opponent_melee_attack.connect(self.on_opponent_melee_attack)
            self.battle_client.melee_hit_feedback.connect(self.on_melee_hit_feedback)
    
    def create_room(self):
        """创建房间（启动服务器）"""
        try:
            # 启动服务器
            self.battle_server = BattleServer(port=8888)
            if self.battle_server.start():
                self.status_label.setText("房间创建成功，等待玩家加入...")
                self.create_room_btn.setEnabled(False)
                self.join_room_btn.setEnabled(False)
                
                # 启动客户端连接到自己的服务器
                self.start_client("127.0.0.1", 8888)
            else:
                QMessageBox.warning(self, "错误", "创建房间失败，请检查端口是否被占用")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"创建房间失败: {e}")
    
    def join_room(self):
        """加入房间"""
        try:
            server_ip, ok = QInputDialog.getText(self, "加入房间", "请输入服务器IP地址:", text="127.0.0.1")
            if ok and server_ip:
                self.start_client(server_ip, 8888)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加入房间失败: {e}")
    
    def start_client(self, server_ip: str, server_port: int):
        """启动客户端"""
        try:
            self.battle_client = BattleClient(
                player_id=self.player_id,
                player_name=self.player_name,
                pet_name=self.pet_name,
                server_ip=server_ip,
                server_port=server_port
            )
            
            # 连接信号
            self.battle_client.player_joined.connect(self.on_player_joined)
            self.battle_client.player_left.connect(self.on_player_left)
            self.battle_client.attack_received.connect(self.on_attack_received)
            self.battle_client.player_moved.connect(self.on_player_moved)
            self.battle_client.server_disconnected.connect(self.on_server_disconnected)
            self.battle_client.opponent_melee_move.connect(self.on_opponent_melee_move)
            self.battle_client.opponent_melee_attack.connect(self.on_opponent_melee_attack)
            self.battle_client.melee_hit_feedback.connect(self.on_melee_hit_feedback)
            
            if self.battle_client.start():
                self.status_label.setText(f"已连接到 {server_ip}:{server_port}")
                self.add_battle_log("成功连接到对战服务器")
            else:
                QMessageBox.warning(self, "错误", "连接服务器失败")
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"启动客户端失败: {e}")
    
    def on_player_joined(self, player_id: str, player_name: str):
        """玩家加入"""
        self.players[player_id] = {'name': player_name, 'health': 100, 'position': (random.randint(100, 700), random.randint(100, 500))}
        self.update_player_list()
        self.add_battle_log(f"玩家 {player_name} 加入了战斗")
    
    def on_player_left(self, player_id: str):
        """玩家离开"""
        if player_id in self.players:
            player_name = self.players[player_id]['name']
            del self.players[player_id]
            self.update_player_list()
            self.add_battle_log(f"玩家 {player_name} 离开了战斗")
            
            # 如果离开的是当前选中的目标，清除选择
            if self.selected_target == player_id:
                self.selected_target = None
                self.disable_attack_buttons()
    
    def on_attack_received(self, attacker_id: str, target_id: str, attack_data: dict):
        """收到攻击"""
        if target_id == self.player_id:
            # 我受到攻击
            attack_type = attack_data.get('attack_type', 'fireball')
            damage = attack_data.get('damage', 20)
            
            # 应用基础伤害
            self.my_health = max(0, self.my_health - damage)
            self.my_health_bar.setValue(self.my_health)
            
            # 应用特殊效果
            if attack_type == "fireball":
                # 灼烧效果
                burn_duration = attack_data.get('burn_duration', 3.0)
                burn_damage = attack_data.get('burn_damage', 5)
                self.status_effects.append(StatusEffect("burn", burn_duration, burn_damage))
                self.add_battle_log(f"受到灼烧效果，持续{burn_duration}秒")
                
            elif attack_type == "lightning":
                # 电击效果
                shock_duration = attack_data.get('shock_duration', 4.0)
                shock_damage = attack_data.get('shock_damage', 3)
                self.status_effects.append(StatusEffect("shock", shock_duration, shock_damage))
                self.add_battle_log(f"受到电击效果，持续{shock_duration}秒")
                
            elif attack_type == "ice":
                # 缓速效果
                slow_duration = attack_data.get('slow_duration', 5.0)
                slow_factor = attack_data.get('slow_factor', 0.5)
                self.status_effects.append(StatusEffect("slow", slow_duration, slow_factor=slow_factor))
                self.add_battle_log(f"受到缓速效果，移动速度减半，持续{slow_duration}秒")
            
            # 播放受击动画
            self.play_hit_animation(attack_type)
            
            attacker_name = self.players.get(attacker_id, {}).get('name', '未知')
            self.add_battle_log(f"受到 {attacker_name} 的 {attack_type} 攻击，损失 {damage} 点生命值")
            
            if self.my_health <= 0:
                self.add_battle_log("你被击败了！")
        else:
            # 其他玩家受到攻击
            attacker_name = self.players.get(attacker_id, {}).get('name', '未知')
            target_name = self.players.get(target_id, {}).get('name', '未知')
            attack_type = attack_data.get('attack_type', 'fireball')
            damage = attack_data.get('damage', 20)
            
            self.add_battle_log(f"{attacker_name} 向 {target_name} 发动 {attack_type} 攻击，造成 {damage} 点伤害")
    
    def on_player_moved(self, player_id: str, position: tuple):
        """玩家移动"""
        if player_id in self.players:
            self.players[player_id]['position'] = position
            player_name = self.players[player_id]['name']
            self.add_battle_log(f"{player_name} 移动到位置 {position}")
    
    def on_server_disconnected(self):
        """服务器断开连接"""
        self.status_label.setText("与服务器断开连接")
        self.add_battle_log("与服务器断开连接")
    
    def update_player_list(self):
        """更新玩家列表"""
        self.player_list.clear()
        for player_id, player_info in self.players.items():
            if player_id != self.player_id:  # 不显示自己
                item = QListWidgetItem(f"🎮 {player_info['name']}")
                item.setData(Qt.ItemDataRole.UserRole, player_id)
                self.player_list.addItem(item)
    
    def on_player_selected(self, item):
        """玩家被选中"""
        player_id = item.data(Qt.ItemDataRole.UserRole)
        player_name = self.players.get(player_id, {}).get('name', "未知玩家")
        
        self.selected_target = player_id
        self.enable_attack_buttons()
    
    def enable_attack_buttons(self):
        """启用攻击按钮"""
        self.fireball_btn.setEnabled(True)
        self.lightning_btn.setEnabled(True)
        self.arrow_btn.setEnabled(True)
        self.ice_btn.setEnabled(True) # 启用冰霜攻击按钮
    
    def disable_attack_buttons(self):
        """禁用攻击按钮"""
        self.fireball_btn.setEnabled(False)
        self.lightning_btn.setEnabled(False)
        self.arrow_btn.setEnabled(False)
        self.ice_btn.setEnabled(False) # 禁用冰霜攻击按钮
    
    def send_attack(self, attack_type: str):
        """发送攻击"""
        if not self.selected_target or not self.battle_client:
            return
        
        # 检查冷却时间
        current_time = time.time()
        rules = BATTLE_RULES.get(attack_type)
        if not rules:
            return
        
        cooldown_remaining = rules['cooldown'] - (current_time - self.last_attack_time.get(attack_type, 0))
        if cooldown_remaining > 0:
            self.add_battle_log(f"{attack_type}攻击还在冷却中，剩余{cooldown_remaining:.1f}秒")
            return
        
        # 更新攻击时间
        self.last_attack_time[attack_type] = current_time
        
        # 计算攻击参数
        attack_data = {
            'target_id': self.selected_target,
            'attack_type': attack_type,
            'damage': rules['damage'],
            'start_position': self.my_position,
            'y_offset': self.attack_y_offset,
            'angle': self.attack_angle
        }
        
        # 添加特殊效果信息
        if attack_type == "fireball":
            attack_data['burn_duration'] = rules['burn_duration']
            attack_data['burn_damage'] = rules['burn_damage']
        elif attack_type == "lightning":
            attack_data['shock_duration'] = rules['shock_duration']
            attack_data['shock_damage'] = rules['shock_damage']
        elif attack_type == "ice":
            attack_data['slow_duration'] = rules['slow_duration']
            attack_data['slow_factor'] = rules['slow_factor']
        
        # 准备特殊效果数据
        special_effects = {}
        if attack_type == "fireball":
            special_effects['burn_duration'] = rules['burn_duration']
            special_effects['burn_damage'] = rules['burn_damage']
        elif attack_type == "lightning":
            special_effects['shock_duration'] = rules['shock_duration']
            special_effects['shock_damage'] = rules['shock_damage']
        elif attack_type == "ice":
            special_effects['slow_duration'] = rules['slow_duration']
            special_effects['slow_factor'] = rules['slow_factor']
        
        self.battle_client.send_attack(self.selected_target, attack_type, attack_data['damage'], special_effects)
        
        # 播放攻击动画
        self.play_attack_animation(attack_type)
        
        self.add_battle_log(f"向 {self.players.get(self.selected_target, {}).get('name', '未知')} 发动 {attack_type} 攻击")
    
    def play_attack_animation(self, attack_type: str):
        """播放攻击动画"""
        if not self.selected_target:
            return
        # 获取目标位置
        target_pos = self.players.get(self.selected_target, {}).get('position', (600, 300))
        # 计算起始位置（考虑Y轴偏移）
        start_x, start_y = self.my_position
        start_y += self.attack_y_offset
        if attack_type == "arrow":
            sprite = "arrow.png"
        elif attack_type == "fireball":
            sprite = "fireball.png"
        elif attack_type == "ice":
            sprite = "iceball.png"
        elif attack_type == "lightning":
            sprite = "lighting.png"
        else:
            sprite = None
        if sprite:
            effect = AttackSpriteEffect((start_x, start_y), target_pos, sprite, self)
            effect.show()
    
    def play_hit_animation(self, attack_type: str):
        """播放受击动画"""
        # 获取屏幕尺寸
        screen = self.screen()
        if screen:
            screen_rect = screen.geometry()
            
            if attack_type == "arrow":
                # 弓箭受击效果在屏幕下方
                hit_pos = (screen_rect.width() // 2, screen_rect.height() - 100)
            else:
                # 其他攻击受击效果在屏幕左侧
                hit_pos = (100, screen_rect.height() // 2)
            
            # 创建受击特效
            hit_effect = HitEffect(hit_pos, attack_type, self)
            hit_effect.show()
    
    def add_battle_log(self, message: str):
        """添加对战日志"""
        self.battle_log.addItem(f"[{self.get_time_str()}] {message}")
        self.battle_log.scrollToBottom()
    
    def get_time_str(self):
        """获取时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.battle_client:
            self.battle_client.stop()
        if self.battle_server:
            self.battle_server.stop()
        event.accept() 

    def switch_mode(self):
        if self.mode == 'ranged':
            self.mode = 'melee'
            self.mode_btn.setText("切换为远程模式")
            self.melee_hint_label.setText("近战模式：WASD/方向键移动，空格跳跃，J攻击")
            self.melee_health_frame.setVisible(True)
        else:
            self.mode = 'ranged'
            self.mode_btn.setText("切换为近战模式")
            self.melee_hint_label.setText("")
            self.melee_health_frame.setVisible(False)
        self.update()

    def keyPressEvent(self, event):
        if self.mode == 'melee':
            key = event.key()
            if key in (Qt.Key.Key_W, Qt.Key.Key_Up):
                self.handle_melee_move('up')
            elif key in (Qt.Key.Key_S, Qt.Key.Key_Down):
                self.handle_melee_move('down')
            elif key in (Qt.Key.Key_A, Qt.Key.Key_Left):
                self.handle_melee_move('left')
            elif key in (Qt.Key.Key_D, Qt.Key.Key_Right):
                self.handle_melee_move('right')
            elif key == Qt.Key.Key_Space:
                self.handle_melee_move('jump')
            elif key == Qt.Key.Key_J:
                self.handle_melee_attack()
        else:
            super().keyPressEvent(event)

    def handle_melee_move(self, direction):
        # 本地桌宠移动逻辑（可扩展动画）
        # 这里只做简单位置变更，实际可加速度/跳跃等
        if not hasattr(self, 'melee_pos'):
            self.melee_pos = [self.my_position[0], self.my_position[1]]
        step = 20
        if direction == 'up':
            self.melee_pos[1] -= step
        elif direction == 'down':
            self.melee_pos[1] += step
        elif direction == 'left':
            self.melee_pos[0] -= step
        elif direction == 'right':
            self.melee_pos[0] += step
        elif direction == 'jump':
            self.melee_pos[1] -= 60  # 跳跃高度
        # 发送到网络
        if self.battle_client:
            self.battle_client.send_melee_move(tuple(self.melee_pos))
        self.update()

    def handle_melee_attack(self):
        now = time.time()
        if now - self.last_melee_attack_time < self.melee_attack_cooldown:
            self.add_battle_log("近战攻击冷却中...")
            return
        self.last_melee_attack_time = now
        # 暴击判定
        is_crit = random.random() < 0.1
        damage = 40 if is_crit else 20
        # 攻击动画：变大+变色
        self.play_melee_attack_anim()
        if self.battle_client:
            self.battle_client.send_melee_attack(tuple(getattr(self, 'melee_pos', self.my_position)), damage, is_crit)
        log = "你发起了近战攻击！"
        if is_crit:
            log += " [暴击!]"
        self.add_battle_log(log)
        self.update()

    def play_melee_attack_anim(self):
        # 攻击动画：变大+变色
        self._melee_attack_anim_progress = 0
        if not hasattr(self, '_melee_attack_anim_timer'):
            self._melee_attack_anim_timer = QTimer(self)
            self._melee_attack_anim_timer.timeout.connect(self.update_melee_attack_anim)
        self._melee_attack_anim_timer.start(30)

    def update_melee_attack_anim(self):
        self._melee_attack_anim_progress += 1
        if self._melee_attack_anim_progress > 8:
            self._melee_attack_anim_timer.stop()
            self._melee_attack_anim_progress = 0
        self.update()

    def on_opponent_melee_move(self, player_id, pos):
        # 接收对方桌宠移动
        self.opponent_pet_state = {'pos': pos}
        self.update()

    def on_opponent_melee_attack(self, player_id, data):
        # data: (pos, damage, is_crit)
        pos, damage, is_crit = data if isinstance(data, tuple) and len(data) == 3 else (data, 20, False)
        if not hasattr(self, 'melee_pos'):
            self.melee_pos = [self.my_position[0], self.my_position[1]]
        my_pos = tuple(self.melee_pos)
        opp_pos = pos
        dist = ((my_pos[0]-opp_pos[0])**2 + (my_pos[1]-opp_pos[1])**2) ** 0.5
        hit_range = 50
        if dist <= hit_range and not self.melee_invincible:
            self.melee_health = max(0, self.melee_health - damage)
            self.my_melee_health_bar.setValue(self.melee_health)
            self.melee_invincible = True
            self.melee_invincible_timer.start(500)
            log = f"被对方近战命中！{'[暴击!]' if is_crit else ''} 生命值：{self.melee_health}"
            self.add_battle_log(log)
            self.play_melee_hit_effect(my_pos)
            if self.battle_client:
                self.battle_client.send_melee_hit_feedback(player_id, my_pos, damage, is_crit)
        else:
            self.add_battle_log("对方近战攻击未命中")
        self.opponent_pet_state = {'pos': pos, 'attacking': True}
        self.update()

    def play_melee_hit_effect(self, pos):
        # 受击动画：闪烁+红色高亮
        effect = HitEffect(pos, 'melee', self)
        effect.show()
        # 播放击退动画
        self.play_melee_knockback(pos)

    def play_melee_knockback(self, attacker_pos):
        # 计算击退方向
        if not hasattr(self, 'melee_pos'):
            self.melee_pos = [self.my_position[0], self.my_position[1]]
        my_x, my_y = self.melee_pos
        atk_x, atk_y = attacker_pos
        dx = my_x - atk_x
        dy = my_y - atk_y
        dist = (dx**2 + dy**2) ** 0.5
        if dist == 0:
            dx, dy = 1, 0
            dist = 1
        dx /= dist
        dy /= dist
        knockback_dist = 30
        self.melee_pos[0] += int(dx * knockback_dist)
        self.melee_pos[1] += int(dy * knockback_dist)
        self.update()

    def end_melee_invincible(self):
        self.melee_invincible = False

    def on_melee_hit_feedback(self, player_id, data):
        # data: (pos, damage, is_crit)
        pos, damage, is_crit = data if isinstance(data, tuple) and len(data) == 3 else (data, 20, False)
        self.opponent_melee_health = max(0, self.opponent_melee_health - damage)
        self.opponent_melee_health_bar.setValue(self.opponent_melee_health)
        log = f"你近战命中了对方！{'[暴击!]' if is_crit else ''} 对方生命值：{self.opponent_melee_health}"
        self.add_battle_log(log)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        # 近战模式下渲染对方桌宠
        if self.mode == 'melee' and self.opponent_pet_state:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pos = self.opponent_pet_state['pos']
            # 简单画个圆代表对方桌宠
            painter.setBrush(QBrush(QColor(255, 100, 200, 180)))
            painter.setPen(QPen(QColor(120, 0, 120), 2))
            painter.drawEllipse(pos[0]-20, pos[1]-20, 40, 40)
            if self.opponent_pet_state.get('attacking'):
                painter.setPen(QPen(QColor(255,0,0), 3))
                painter.drawEllipse(pos[0]-30, pos[1]-30, 60, 60)
        # 近战模式下渲染本地桌宠动画
        if self.mode == 'melee' and hasattr(self, 'melee_pos'):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            x, y = self.melee_pos
            # 攻击动画：变大+变色
            scale = 1.0
            color = QColor(100, 200, 255, 180)
            if hasattr(self, '_melee_attack_anim_progress') and self._melee_attack_anim_progress > 0:
                scale = 1.2
                color = QColor(255, 200, 100, 220)
            # 受击动画：闪烁+红色高亮
            if self.melee_invincible and (int(time.time()*10)%2==0):
                color = QColor(255, 50, 50, 220)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(0, 120, 120), 2))
            painter.drawEllipse(int(x-20*scale), int(y-20*scale), int(40*scale), int(40*scale)) 