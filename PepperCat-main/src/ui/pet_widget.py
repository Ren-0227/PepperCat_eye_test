#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌宠显示组件
"""

import math
import random
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPolygonF, QPixmap, QGuiApplication
import os

class FireballSprite(QFrame):
    def __init__(self, start_pos, direction_right, parent=None):
        super().__init__(None)  # 关键：parent 设为 None
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.resize(80, 80)  # 火球窗口尺寸，足够包住火球
        self.fx, self.fy = int(start_pos[0]), int(start_pos[1])
        self.direction_right = direction_right
        self.speed = 16  # 每帧移动速度
        self.frame_index = 0
        self.frames = []
        self.scale = 0.5  # 火球缩小为原来一半
        self.bounced = False  # 是否已经反弹过
        self.load_frames()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        # 获取物理屏幕边界
        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            self.screen_left = geo.left()
            self.screen_right = geo.right()
        else:
            self.screen_left = 0
            self.screen_right = 1920  # fallback
        self.show()
        self.timer.start(60)

    def load_frames(self):
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets', 'peppercat')
        sheet_path = os.path.join(asset_dir, 'fireball.png')
        sheet = QPixmap(sheet_path)
        w = sheet.width()
        h = sheet.height() // 2
        self.frames = [sheet.copy(0, i * h, w, h) for i in range(2)]

    def update_animation(self):
        # 移动
        if self.direction_right:
            self.fx += self.speed
        else:
            self.fx -= self.speed
        # 切换帧
        self.frame_index = (self.frame_index + 1) % 2
        # 判断是否碰到物理屏幕边缘
        if not self.bounced:
            if self.fx < self.screen_left:
                self.fx = self.screen_left
                self.direction_right = True
                self.bounced = True
            elif self.fx > self.screen_right:
                self.fx = self.screen_right
                self.direction_right = False
                self.bounced = True
        else:
            if self.fx < self.screen_left or self.fx > self.screen_right:
                self.timer.stop()
                self.deleteLater()
                return
        # 关键：用 move() 把窗口移动到 fx, fy 的全局坐标
        self.move(int(self.fx - self.width() // 2), int(self.fy - self.height() // 2))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        frame = self.frames[self.frame_index]
        fw, fh = frame.width(), frame.height()
        x = (self.width() - fw * self.scale) // 2
        y = (self.height() - fh * self.scale) // 2
        painter.save()
        if self.direction_right:
            painter.translate(x + fw * self.scale, y)
            painter.scale(-self.scale, self.scale)
        else:
            painter.translate(x, y)
            painter.scale(self.scale, self.scale)
        painter.drawPixmap(0, 0, frame)
        painter.restore()

class IceballSprite(FireballSprite):
    def load_frames(self):
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets', 'peppercat')
        sheet_path = os.path.join(asset_dir, 'iceball.png')
        sheet = QPixmap(sheet_path)
        w = sheet.width()
        h = sheet.height() // 2
        self.frames = [sheet.copy(0, i * h, w, h) for i in range(2)]

class LightningSprite(FireballSprite):
    def load_frames(self):
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets', 'peppercat')
        sheet_path = os.path.join(asset_dir, 'lighting.png')
        sheet = QPixmap(sheet_path)
        w = sheet.width()
        h = sheet.height() // 2
        self.frames = [sheet.copy(0, i * h, w, h) for i in range(2)]

class PetWidget(QWidget):
    """桌宠显示组件"""
    dragged = pyqtSignal(QPoint)  # 拖动信号，传递窗口新位置
    dragged_global = pyqtSignal(QPoint)  # 新增：拖动时发射全局坐标
    doubleClicked = pyqtSignal(object)  # 新增：双击信号，传递事件对象
    
    def __init__(self, pet_agent):
        super().__init__()
        self.pet_agent = pet_agent
        self.animation_state = "idle"
        self.animation_frame = 0
        self.bounce_offset = 0
        self.eye_blink = False
        self.tail_wag = 0
        self._drag_active = False
        self._drag_position = QPoint()
        self.trail_points = []  # 拖尾点
        self.pixel_pet_pixels = None  # 兼容单一像素桌宠
        self.pixel_pet_animation = None  # 动画数据
        self.pixel_pet_anim_time = 0
        self.pixel_pet_anim_state = "idle"
        self.pixel_pet_anim_timer = None
        
        # 新增：PNG帧动画相关
        self.png_animation_frames = []
        self.png_animation_index = 0
        self.png_animation_timer = QTimer(self)
        self.png_animation_timer.timeout.connect(self._next_png_frame)
        self.png_animation_playing = False
        self.pet_name = ""
        self.facing_right = True  # 新增：朝向，True为右，False为左
        self.battle_mode = False  # 战斗模式
        self.anim_state = 'idle'  # idle, walk, fightwalk, attack_fireball, attack_iceball, attack_lighting, attack_sword
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._next_anim_frame)
        self.anim_frames = []
        self.anim_index = 0
        self.anim_playing = False
        
        # 设置组件属性
        self.setMinimumSize(300, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
        # 设置动画定时器
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(100)  # 每100ms更新一次动画
        
        # 眨眼定时器
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_blink)
        self.blink_timer.start(random.randint(2000, 5000))  # 随机眨眼
        
        self.active_fireballs = []  # 保存活跃的火球实例，防止被GC
    
    def update_animation(self):
        """更新动画状态"""
        self.animation_frame += 1
        if self.animation_frame > 60:  # 重置动画帧
            self.animation_frame = 0
        
        # 更新动画状态
        new_animation = self.pet_agent.get_current_animation()
        if new_animation != self.animation_state:
            self.animation_state = new_animation
            self.animation_frame = 0
        
        # 更新各种动画效果
        self.bounce_offset = math.sin(self.animation_frame * 0.1) * 5
        self.tail_wag = math.sin(self.animation_frame * 0.2) * 10
        
        self.update()  # 重绘组件
        
    def toggle_blink(self):
        """切换眨眼状态"""
        self.eye_blink = not self.eye_blink
        self.update()
        
        # 设置下次眨眼时间
        if self.eye_blink:
            self.blink_timer.setInterval(150)  # 眨眼持续150ms
        else:
            self.blink_timer.setInterval(random.randint(2000, 5000))  # 随机眨眼间隔
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            win = self.window()
            if win is not None:
                self._drag_offset = event.globalPosition().toPoint() - win.frameGeometry().topLeft()
            else:
                self._drag_offset = event.globalPosition().toPoint()
            event.accept()
        else:
            super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
            global_pos = event.globalPosition().toPoint()
            # 计算窗口新位置
            new_pos = global_pos - self._drag_offset
            self.dragged.emit(new_pos)
            self.dragged_global.emit(global_pos)
            self.add_trail_point(global_pos) # 添加拖尾点
            event.accept()
        else:
            super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        self._drag_active = False
        event.accept()
    
    def mouseDoubleClickEvent(self, event):
        # 修正：区分左右键双击
        self.doubleClicked.emit(event)
        super().mouseDoubleClickEvent(event)
    
    def add_trail_point(self, pt: QPoint):
        self.trail_points.append(pt)
        if len(self.trail_points) > 15:
            self.trail_points.pop(0)
        self.update()
    
    def set_pixel_pet(self, pixels):
        self.pixel_pet_pixels = pixels
        self.update()
    
    def set_pixel_pet_animation(self, animation_data):
        self.pixel_pet_animation = animation_data
        self.pixel_pet_anim_state = "idle"
        self.pixel_pet_anim_time = 0
        if self.pixel_pet_anim_timer:
            self.pixel_pet_anim_timer.stop()
        self.pixel_pet_anim_timer = QTimer(self)
        self.pixel_pet_anim_timer.timeout.connect(self._pixel_pet_anim_tick)
        self.pixel_pet_anim_timer.start(50)
        self.update()
    def _pixel_pet_anim_tick(self):
        self.pixel_pet_anim_time += 0.05
        self.update()
    def play_animation(self, state_name):
        if self.pixel_pet_animation and state_name in self.pixel_pet_animation:
            self.pixel_pet_anim_state = state_name
            self.pixel_pet_anim_time = 0
            self.update()
    def trigger_interaction(self, action):
        # 可根据action切换动画
        if action == 'pet':
            self.play_animation('excited')
        elif action == 'sleep':
            self.play_animation('sleeping')
        elif action == 'hungry':
            self.play_animation('hungry')
        elif action == 'sad':
            self.play_animation('sad')
        else:
            self.play_animation('idle')
        self.update()
    
    def set_png_animation_frames(self, frame_paths):
        """设置PNG帧动画资源"""
        from PyQt6.QtGui import QPixmap
        self.png_animation_frames = [QPixmap(f) for f in frame_paths]
        self.png_animation_index = 0
        self.update()

    def set_spritesheet_animation(self, sheet_path, frame_width, frame_height, rows, cols):
        """从spritesheet自动切割帧动画"""
        from PyQt6.QtGui import QPixmap
        sheet = QPixmap(sheet_path)
        self.png_animation_frames = []
        for row in range(rows):
            for col in range(cols):
                x = col * frame_width
                y = row * frame_height
                frame = sheet.copy(x, y, frame_width, frame_height)
                self.png_animation_frames.append(frame)
        self.png_animation_index = 0
        self.update()

    def set_pet_name(self, name):
        self.pet_name = name

    def play_png_animation(self, dx=None):
        # dx: 鼠标x方向增量，正为右，负为左
        if dx is not None:
            self.facing_right = dx < 0
        if self.png_animation_frames and not self.png_animation_playing:
            self.png_animation_playing = True
            self.png_animation_timer.start(120)  # 120ms一帧

    def stop_png_animation(self):
        if self.png_animation_playing:
            self.png_animation_playing = False
            self.png_animation_timer.stop()
            self.png_animation_index = 0
            self.update()

    def _next_png_frame(self):
        if self.png_animation_frames:
            self.png_animation_index = (self.png_animation_index + 1) % len(self.png_animation_frames)
            self.update()
    
    def _next_anim_frame(self):
        if not self.anim_frames:
            return
        self.anim_index = (self.anim_index + 1) % len(self.anim_frames)
        self.update()
        # 攻击动画只播一轮就恢复走路/近战idle
        if self.anim_state.startswith('attack') and self.anim_index == 0:
            if self.battle_mode:
                self.play_melee_idle()
            else:
                self.play_walk_anim()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取组件尺寸
        width = self.width()
        height = self.height()
        
        # 优先绘制当前动画
        if self.anim_frames:
            frame = self.anim_frames[self.anim_index]
            fw, fh = frame.width(), frame.height()
            x = (width - fw) // 2
            y = (height - fh) // 2
            if self.facing_right:
                painter.drawPixmap(x, y, frame)
            else:
                painter.save()
                painter.translate(x + fw, y)
                painter.scale(-1, 1)
                painter.drawPixmap(0, 0, frame)
                painter.restore()
            return

        # 优先绘制PNG帧动画
        if self.png_animation_frames:
            frame = self.png_animation_frames[self.png_animation_index]
            fw, fh = frame.width(), frame.height()
            x = (width - fw) // 2
            y = (height - fh) // 2
            if self.facing_right:
                painter.drawPixmap(x, y, frame)
            else:
                # 水平镜像绘制
                painter.save()
                painter.translate(x + fw, y)
                painter.scale(-1, 1)
                painter.drawPixmap(0, 0, frame)
                painter.restore()
            return

        # 拖尾特效
        if self.trail_points:
            for i, pt in enumerate(self.trail_points):
                alpha = int(80 * (i + 1) / len(self.trail_points))
                color = QColor(180, 220, 255, alpha)
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(self.mapFromGlobal(pt), 32, 32)
        
        # --- 新增：像素桌宠动画模式 ---
        if self.pixel_pet_animation:
            state = self.pixel_pet_anim_state
            t = self.pixel_pet_anim_time
            anim = self.pixel_pet_animation.get(state) or self.pixel_pet_animation.get('idle')
            if anim:
                for part in anim:
                    kfs = anim[part]['keyframes']
                    anchor = anim[part].get('anchor', (16,16))
                    # 找到当前时间的前后关键帧
                    prev, next = kfs[0], kfs[-1]
                    for i in range(1, len(kfs)):
                        if t < kfs[i]['time']:
                            prev, next = kfs[i-1], kfs[i]
                            break
                    dt = next['time'] - prev['time']
                    if dt == 0:
                        ratio = 0
                    else:
                        ratio = (t - prev['time']) / dt
                        ratio = max(0, min(1, ratio))
                    angle = prev['angle'] + (next['angle'] - prev['angle']) * ratio
                    ox = prev['offset'][0] + (next['offset'][0] - prev['offset'][0]) * ratio
                    oy = prev['offset'][1] + (next['offset'][1] - prev['offset'][1]) * ratio
                    pixels = anim[part].get('pixels', [])
                    painter.save()
                    painter.translate(ox, oy)
                    painter.rotate(angle)
                    # 默认scale=1
                    for px in pixels:
                        color = QColor.fromRgba(px['color'])
                        painter.setBrush(QBrush(color))
                        painter.setPen(Qt.PenStyle.NoPen)
                        painter.drawRect(int(px['x']*6), int(px['y']*6), 6, 6)
                    # 画锚点
                    painter.setPen(QPen(QColor(255,0,0), 2))
                    painter.setBrush(QBrush(QColor(255,255,255)))
                    painter.drawEllipse(int(anchor[0]*6-4), int(anchor[1]*6-4), 8, 8)
                    painter.restore()
                return
        # --- 兼容单一像素桌宠 ---
        if self.pixel_pet_pixels:
            size = 32
            pixel_size = min(width, height) // size
            offset_x = width // 2 - (size * pixel_size) // 2
            offset_y = height // 2 + self.bounce_offset - (size * pixel_size) // 2
            for px in self.pixel_pet_pixels:
                color = QColor.fromRgba(px['color'])
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(offset_x + px['x']*pixel_size, offset_y + px['y']*pixel_size, pixel_size, pixel_size)
            return
        # --- 原有青椒猫绘制 ---
        # 计算宠物位置（居中）
        center_x = width // 2
        center_y = height // 2 + self.bounce_offset
        
        # 根据动画状态绘制青椒猫
        if self.animation_state == "sleeping":
            self.draw_peppercat_sleeping(painter, center_x, center_y)
        elif self.animation_state == "excited":
            self.draw_peppercat_excited(painter, center_x, center_y)
        elif self.animation_state == "hungry":
            self.draw_peppercat_hungry(painter, center_x, center_y)
        elif self.animation_state == "sad":
            self.draw_peppercat_sad(painter, center_x, center_y)
        else:
            self.draw_peppercat_pet(painter, center_x, center_y)
    
    def draw_peppercat_pet(self, painter, x, y, face_override=None, arms_pose=None, legs_pose=None, extra=None):
        """更细致的青椒猫形象（idle/基础体）"""
        # --- 青椒主体 ---
        from PyQt6.QtGui import QPainterPath, QLinearGradient
        pepper_path = QPainterPath()
        pepper_path.moveTo(x-40, y-60)
        pepper_path.cubicTo(x-60, y-40, x-60, y+40, x-40, y+60)
        pepper_path.cubicTo(x-20, y+80, x+20, y+80, x+40, y+60)
        pepper_path.cubicTo(x+60, y+40, x+60, y-40, x+40, y-60)
        pepper_path.cubicTo(x+20, y-80, x-20, y-80, x-40, y-60)
        grad = QLinearGradient(x, y-60, x, y+60)
        grad.setColorAt(0, QColor(160, 230, 120))
        grad.setColorAt(0.5, QColor(100, 180, 80))
        grad.setColorAt(1, QColor(60, 120, 40))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(70, 120, 40), 4))
        painter.drawPath(pepper_path)
        # 青椒高光
        painter.setBrush(QBrush(QColor(255,255,255,60)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x-30, y-40, 24, 60)
        painter.drawEllipse(x+10, y-30, 18, 40)
        # 顶部柄（分叉）
        painter.setBrush(QBrush(QColor(120, 200, 90)))
        painter.setPen(QPen(QColor(70, 120, 40), 3))
        painter.drawEllipse(x-10, y-75, 20, 20)
        painter.drawRect(x-3, y-90, 6, 20)
        painter.drawRect(x+5, y-85, 4, 12)
        painter.drawRect(x-9, y-85, 4, 12)
        # --- 四肢动画参数 ---
        t = self.animation_frame * 0.10
        # 手臂分段运动
        l_shoulder = (-38, -30)
        r_shoulder = (38, -30)
        l_arm_angle = -30 + 25*math.sin(t)
        r_arm_angle = 30 - 25*math.sin(t+0.8)
        l_forearm_angle = 30*math.sin(t+0.5)
        r_forearm_angle = -30*math.sin(t+1.2)
        # 腿
        l_hip = (-20, 55)
        r_hip = (20, 55)
        l_leg_angle = -10 + 10*math.sin(t+1.5)
        r_leg_angle = 10 - 10*math.sin(t+2.1)
        # --- 左手（上臂+前臂+爪）---
        painter.save()
        painter.translate(x+l_shoulder[0], y+l_shoulder[1])
        painter.rotate(l_arm_angle)
        painter.setBrush(QBrush(QColor(230, 210, 180)))
        painter.setPen(QPen(QColor(180, 150, 120), 2))
        painter.drawRoundedRect(-7, 0, 14, 28, 7, 10)
        painter.translate(0, 26)
        painter.rotate(l_forearm_angle)
        painter.drawRoundedRect(-6, 0, 12, 20, 6, 8)
        # 爪子
        painter.setBrush(QBrush(QColor(255, 230, 200)))
        painter.drawEllipse(-8, 14, 16, 10)
        # 肉垫
        painter.setBrush(QBrush(QColor(255, 180, 180)))
        painter.drawEllipse(-2, 20, 4, 4)
        painter.drawEllipse(-6, 18, 3, 3)
        painter.drawEllipse(3, 18, 3, 3)
        painter.restore()
        # --- 右手 ---
        painter.save()
        painter.translate(x+r_shoulder[0], y+r_shoulder[1])
        painter.rotate(r_arm_angle)
        painter.setBrush(QBrush(QColor(230, 210, 180)))
        painter.setPen(QPen(QColor(180, 150, 120), 2))
        painter.drawRoundedRect(-7, 0, 14, 28, 7, 10)
        painter.translate(0, 26)
        painter.rotate(r_forearm_angle)
        painter.drawRoundedRect(-6, 0, 12, 20, 6, 8)
        painter.setBrush(QBrush(QColor(255, 230, 200)))
        painter.drawEllipse(-8, 14, 16, 10)
        painter.setBrush(QBrush(QColor(255, 180, 180)))
        painter.drawEllipse(-2, 20, 4, 4)
        painter.drawEllipse(-6, 18, 3, 3)
        painter.drawEllipse(3, 18, 3, 3)
        painter.restore()
        # --- 左腿 ---
        painter.save()
        painter.translate(x+l_hip[0], y+l_hip[1])
        painter.rotate(l_leg_angle)
        painter.setBrush(QBrush(QColor(230, 210, 180)))
        painter.setPen(QPen(QColor(180, 150, 120), 2))
        painter.drawRoundedRect(-7, 0, 14, 24, 7, 8)
        painter.setBrush(QBrush(QColor(255, 230, 200)))
        painter.drawEllipse(-7, 16, 14, 8)
        painter.restore()
        # --- 右腿 ---
        painter.save()
        painter.translate(x+r_hip[0], y+r_hip[1])
        painter.rotate(r_leg_angle)
        painter.setBrush(QBrush(QColor(230, 210, 180)))
        painter.setPen(QPen(QColor(180, 150, 120), 2))
        painter.drawRoundedRect(-7, 0, 14, 24, 7, 8)
        painter.setBrush(QBrush(QColor(255, 230, 200)))
        painter.drawEllipse(-7, 16, 14, 8)
        painter.restore()
        # --- 青椒洞 ---
        painter.setBrush(QBrush(QColor(220, 240, 200)))
        painter.setPen(QPen(QColor(180, 200, 160), 2))
        painter.drawEllipse(x-24, y-12, 48, 40)
        # --- 猫头 ---
        painter.setBrush(QBrush(QColor(255, 245, 220)))
        painter.setPen(QPen(QColor(180, 150, 120), 2))
        painter.drawEllipse(x-18, y-6, 36, 32)
        # 耳朵（双色）
        painter.setBrush(QBrush(QColor(255, 245, 220)))
        painter.setPen(QPen(QColor(180, 150, 120), 2))
        left_ear = QPolygonF([
            QPointF(x-10, y-6),
            QPointF(x-18, y-22),
            QPointF(x, y-14)
        ])
        right_ear = QPolygonF([
            QPointF(x+10, y-6),
            QPointF(x+18, y-22),
            QPointF(x, y-14)
        ])
        painter.drawPolygon(left_ear)
        painter.drawPolygon(right_ear)
        # 耳朵内侧
        painter.setBrush(QBrush(QColor(255, 220, 200)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygonF([
            QPointF(x-10, y-8), QPointF(x-15, y-18), QPointF(x-2, y-13)
        ]))
        painter.drawPolygon(QPolygonF([
            QPointF(x+10, y-8), QPointF(x+15, y-18), QPointF(x+2, y-13)
        ]))
        # 眼睛
        if not self.eye_blink:
            painter.setBrush(QBrush(QColor(60, 60, 60)))
            painter.drawEllipse(x-8, y+2, 6, 8)
            painter.drawEllipse(x+2, y+2, 6, 8)
            # 瞳孔
            painter.setBrush(QBrush(QColor(30, 30, 30)))
            painter.drawEllipse(x-6, y+5, 2, 3)
            painter.drawEllipse(x+4, y+5, 2, 3)
            # 高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(x-5, y+3, 1, 2)
            painter.drawEllipse(x+6, y+3, 1, 2)
        else:
            painter.setPen(QPen(QColor(60, 60, 60), 2))
            painter.drawLine(x-8, y+7, x-2, y+7)
            painter.drawLine(x+2, y+7, x+8, y+7)
        # 鼻子
        painter.setBrush(QBrush(QColor(255, 180, 180)))
        painter.setPen(QPen(QColor(180, 120, 120), 1))
        painter.drawEllipse(x-2, y+12, 4, 3)
        # 嘴巴
        painter.setPen(QPen(QColor(120, 80, 80), 2))
        painter.drawArc(x-6, y+14, 12, 8, 0, 180*16)
        # 腮红
        painter.setBrush(QBrush(QColor(255, 200, 200, 120)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x-12, y+16, 6, 3)
        painter.drawEllipse(x+6, y+16, 6, 3)
        # 胡须
        painter.setPen(QPen(QColor(180, 150, 120), 1))
        painter.drawLine(x-10, y+18, x-18, y+20)
        painter.drawLine(x-10, y+20, x-18, y+24)
        painter.drawLine(x+10, y+18, x+18, y+20)
        painter.drawLine(x+10, y+20, x+18, y+24)
        # 可选表情/姿态/符号
        if face_override:
            face_override(painter, x, y)
        if arms_pose:
            arms_pose(painter, x, y)
        if legs_pose:
            legs_pose(painter, x, y)
        if extra:
            extra(painter, x, y)
    
    def draw_peppercat_sleeping(self, painter, x, y):
        """青椒猫睡觉状态"""
        def face(p, x, y):
            # 闭眼微笑
            p.setPen(QPen(QColor(60, 60, 60), 2))
            p.drawLine(x-8, y+7, x-2, y+7)
            p.drawLine(x+2, y+7, x+8, y+7)
            p.setPen(QPen(QColor(120, 80, 80), 2))
            p.drawArc(x-6, y+14, 12, 8, 0, 180*16)
        def extra(p, x, y):
            p.setPen(QPen(QColor(100, 100, 255), 3))
            p.setFont(QFont("Arial", 16))
            p.drawText(x+30, y-30, "Z")
            p.drawText(x+36, y-20, "Z")
            p.drawText(x+42, y-10, "Z")
        self.draw_peppercat_pet(painter, x, y, face_override=face, extra=extra)
    def draw_peppercat_excited(self, painter, x, y):
        """青椒猫兴奋状态"""
        def face(p, x, y):
            # 大眼睛+大笑
            p.setBrush(QBrush(QColor(60, 60, 60)))
            p.drawEllipse(x-10, y+2, 8, 10)
            p.drawEllipse(x+2, y+2, 8, 10)
            p.setBrush(QBrush(QColor(30, 30, 30)))
            p.drawEllipse(x-7, y+7, 3, 4)
            p.drawEllipse(x+6, y+7, 3, 4)
            p.setBrush(QBrush(QColor(255, 255, 255)))
            p.drawEllipse(x-5, y+4, 2, 3)
            p.drawEllipse(x+8, y+4, 2, 3)
            p.setPen(QPen(QColor(120, 80, 80), 2))
            p.drawArc(x-8, y+14, 16, 12, 0, 180*16)
        def extra(p, x, y):
            p.setPen(QPen(QColor(255, 100, 100), 2))
            p.setFont(QFont("Arial", 12))
            p.drawText(x-50, y-60, "♥")
            p.drawText(x+40, y-60, "♥")
        self.draw_peppercat_pet(painter, x, y, face_override=face, extra=extra)
    def draw_peppercat_hungry(self, painter, x, y):
        """青椒猫饥饿状态"""
        def face(p, x, y):
            # 可怜眼神+下垂嘴
            p.setBrush(QBrush(QColor(60, 60, 60)))
            p.drawEllipse(x-8, y+4, 6, 7)
            p.drawEllipse(x+2, y+4, 6, 7)
            p.setBrush(QBrush(QColor(30, 30, 30)))
            p.drawEllipse(x-6, y+7, 2, 2)
            p.drawEllipse(x+4, y+7, 2, 2)
            p.setPen(QPen(QColor(120, 80, 80), 2))
            p.drawArc(x-6, y+18, 12, 6, 180*16, 180*16)
        def extra(p, x, y):
            p.setPen(QPen(QColor(255, 150, 0), 2))
            p.setFont(QFont("Arial", 14))
            p.drawText(x-40, y-50, "🍖")
        self.draw_peppercat_pet(painter, x, y, face_override=face, extra=extra)
    def draw_peppercat_sad(self, painter, x, y):
        """青椒猫悲伤状态"""
        def face(p, x, y):
            # 悲伤眼神+嘴角下垂
            p.setBrush(QBrush(QColor(60, 60, 60)))
            p.drawEllipse(x-8, y+6, 6, 6)
            p.drawEllipse(x+2, y+6, 6, 6)
            p.setPen(QPen(QColor(100, 150, 255), 1))
            p.drawEllipse(x-6, y+13, 2, 4)
            p.drawEllipse(x+4, y+13, 2, 4)
            p.setPen(QPen(QColor(120, 80, 80), 2))
            p.drawArc(x-6, y+18, 12, 6, 180*16, 180*16)
        def extra(p, x, y):
            p.setPen(QPen(QColor(100, 100, 100), 2))
            p.setFont(QFont("Arial", 14))
            p.drawText(x-40, y-50, "💧")
        self.draw_peppercat_pet(painter, x, y, face_override=face, extra=extra)
    
    def draw_normal_pet(self, painter, x, y):
        """绘制正常状态的宠物"""
        # 身体（圆形）
        body_color = QColor(255, 200, 100)  # 橙色
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(200, 150, 50), 2))
        painter.drawEllipse(x - 40, y - 30, 80, 60)
        
        # 头部（圆形）
        head_color = QColor(255, 220, 120)
        painter.setBrush(QBrush(head_color))
        painter.drawEllipse(x - 25, y - 50, 50, 50)
        
        # 耳朵（三角形）
        ear_color = QColor(255, 180, 80)
        painter.setBrush(QBrush(ear_color))
        left_ear = QPolygonF([
            QPointF(x - 30, y - 60),
            QPointF(x - 20, y - 75),
            QPointF(x - 10, y - 60)
        ])
        right_ear = QPolygonF([
            QPointF(x + 10, y - 60),
            QPointF(x + 20, y - 75),
            QPointF(x + 30, y - 60)
        ])
        painter.drawPolygon(left_ear)
        painter.drawPolygon(right_ear)
        
        # 眼睛
        if not self.eye_blink:
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.drawEllipse(x - 15, y - 45, 8, 8)
            painter.drawEllipse(x + 7, y - 45, 8, 8)
            
            # 眼睛高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(x - 13, y - 47, 3, 3)
            painter.drawEllipse(x + 9, y - 47, 3, 3)
        else:
            # 眨眼状态
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawLine(x - 15, y - 41, x - 7, y - 41)
            painter.drawLine(x + 7, y - 41, x + 15, y - 41)
        
        # 鼻子
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        painter.drawEllipse(x - 2, y - 35, 4, 4)
        
        # 嘴巴
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawArc(x - 8, y - 30, 16, 16, 0, 180 * 16)
        
        # 尾巴（摇摆）
        tail_x = x + 40 + self.tail_wag
        tail_y = y - 10
        painter.setBrush(QBrush(QColor(255, 180, 80)))
        painter.drawEllipse(tail_x, tail_y, 15, 8)
        
        # 腿
        leg_color = QColor(255, 180, 80)
        painter.setBrush(QBrush(leg_color))
        painter.drawEllipse(x - 25, y + 25, 8, 12)
        painter.drawEllipse(x - 10, y + 25, 8, 12)
        painter.drawEllipse(x + 2, y + 25, 8, 12)
        painter.drawEllipse(x + 17, y + 25, 8, 12)
    
    def draw_sleeping_pet(self, painter, x, y):
        """绘制睡觉状态的宠物"""
        # 身体（躺着的椭圆形）
        body_color = QColor(255, 200, 100)
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(200, 150, 50), 2))
        painter.drawEllipse(x - 50, y - 20, 100, 40)
        
        # 头部（躺着的椭圆形）
        head_color = QColor(255, 220, 120)
        painter.setBrush(QBrush(head_color))
        painter.drawEllipse(x - 30, y - 35, 60, 30)
        
        # 耳朵（下垂）
        ear_color = QColor(255, 180, 80)
        painter.setBrush(QBrush(ear_color))
        painter.drawEllipse(x - 25, y - 40, 15, 20)
        painter.drawEllipse(x + 10, y - 40, 15, 20)
        
        # 闭着的眼睛
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawLine(x - 15, y - 25, x - 7, y - 25)
        painter.drawLine(x + 7, y - 25, x + 15, y - 25)
        
        # 鼻子
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        painter.drawEllipse(x - 2, y - 20, 4, 4)
        
        # 嘴巴（微笑）
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawArc(x - 8, y - 15, 16, 16, 0, 180 * 16)
        
        # ZZZ 符号
        painter.setPen(QPen(QColor(100, 100, 255), 3))
        painter.setFont(QFont("Arial", 16))
        painter.drawText(x + 35, y - 30, "Z")
        painter.drawText(x + 40, y - 20, "Z")
        painter.drawText(x + 45, y - 10, "Z")
    
    def draw_excited_pet(self, painter, x, y):
        """绘制兴奋状态的宠物"""
        # 身体（稍微大一点）
        body_color = QColor(255, 200, 100)
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(200, 150, 50), 2))
        painter.drawEllipse(x - 45, y - 35, 90, 70)
        
        # 头部（稍微大一点）
        head_color = QColor(255, 220, 120)
        painter.setBrush(QBrush(head_color))
        painter.drawEllipse(x - 30, y - 55, 60, 60)
        
        # 耳朵（竖起）
        ear_color = QColor(255, 180, 80)
        painter.setBrush(QBrush(ear_color))
        painter.drawEllipse(x - 25, y - 70, 12, 25)
        painter.drawEllipse(x + 13, y - 70, 12, 25)
        
        # 眼睛（大而圆）
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(x - 18, y - 50, 12, 12)
        painter.drawEllipse(x + 6, y - 50, 12, 12)
        
        # 眼睛高光
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(x - 15, y - 53, 4, 4)
        painter.drawEllipse(x + 9, y - 53, 4, 4)
        
        # 鼻子
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        painter.drawEllipse(x - 3, y - 40, 6, 6)
        
        # 嘴巴（开心的大笑）
        painter.setPen(QPen(QColor(0, 0, 0), 3))
        painter.drawArc(x - 12, y - 35, 24, 20, 0, 180 * 16)
        
        # 尾巴（快速摇摆）
        tail_x = x + 45 + self.tail_wag * 2
        tail_y = y - 15
        painter.setBrush(QBrush(QColor(255, 180, 80)))
        painter.drawEllipse(tail_x, tail_y, 20, 10)
        
        # 腿（跳跃状）
        leg_color = QColor(255, 180, 80)
        painter.setBrush(QBrush(leg_color))
        painter.drawEllipse(x - 30, y + 30, 10, 15)
        painter.drawEllipse(x - 12, y + 30, 10, 15)
        painter.drawEllipse(x + 2, y + 30, 10, 15)
        painter.drawEllipse(x + 20, y + 30, 10, 15)
        
        # 兴奋的符号
        painter.setPen(QPen(QColor(255, 100, 100), 2))
        painter.setFont(QFont("Arial", 12))
        painter.drawText(x - 50, y - 60, "♥")
        painter.drawText(x + 40, y - 60, "♥")
    
    def draw_hungry_pet(self, painter, x, y):
        """绘制饥饿状态的宠物"""
        # 身体（稍微小一点）
        body_color = QColor(255, 200, 100)
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(200, 150, 50), 2))
        painter.drawEllipse(x - 35, y - 25, 70, 50)
        
        # 头部（稍微小一点）
        head_color = QColor(255, 220, 120)
        painter.setBrush(QBrush(head_color))
        painter.drawEllipse(x - 20, y - 45, 40, 45)
        
        # 耳朵（下垂）
        ear_color = QColor(255, 180, 80)
        painter.setBrush(QBrush(ear_color))
        painter.drawEllipse(x - 18, y - 50, 10, 18)
        painter.drawEllipse(x + 8, y - 50, 10, 18)
        
        # 眼睛（可怜的眼神）
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(x - 12, y - 40, 8, 8)
        painter.drawEllipse(x + 4, y - 40, 8, 8)
        
        # 眼睛高光（小一点）
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(x - 10, y - 42, 2, 2)
        painter.drawEllipse(x + 6, y - 42, 2, 2)
        
        # 鼻子
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        painter.drawEllipse(x - 2, y - 30, 4, 4)
        
        # 嘴巴（下垂）
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawArc(x - 6, y - 25, 12, 12, 180 * 16, 180 * 16)
        
        # 尾巴（下垂）
        tail_x = x + 35
        tail_y = y - 5
        painter.setBrush(QBrush(QColor(255, 180, 80)))
        painter.drawEllipse(tail_x, tail_y, 12, 6)
        
        # 腿（无力）
        leg_color = QColor(255, 180, 80)
        painter.setBrush(QBrush(leg_color))
        painter.drawEllipse(x - 20, y + 20, 6, 10)
        painter.drawEllipse(x - 8, y + 20, 6, 10)
        painter.drawEllipse(x + 2, y + 20, 6, 10)
        painter.drawEllipse(x + 14, y + 20, 6, 10)
        
        # 饥饿符号
        painter.setPen(QPen(QColor(255, 150, 0), 2))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(x - 40, y - 50, "🍖")
    
    def draw_sad_pet(self, painter, x, y):
        """绘制悲伤状态的宠物"""
        # 身体（稍微小一点）
        body_color = QColor(200, 180, 100)  # 稍微暗一点
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(150, 130, 50), 2))
        painter.drawEllipse(x - 35, y - 25, 70, 50)
        
        # 头部（稍微小一点）
        head_color = QColor(220, 200, 120)
        painter.setBrush(QBrush(head_color))
        painter.drawEllipse(x - 20, y - 45, 40, 45)
        
        # 耳朵（完全下垂）
        ear_color = QColor(200, 160, 80)
        painter.setBrush(QBrush(ear_color))
        painter.drawEllipse(x - 18, y - 45, 10, 15)
        painter.drawEllipse(x + 8, y - 45, 10, 15)
        
        # 眼睛（悲伤的眼神）
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(x - 12, y - 40, 8, 8)
        painter.drawEllipse(x + 4, y - 40, 8, 8)
        
        # 眼泪
        painter.setBrush(QBrush(QColor(100, 150, 255)))
        painter.drawEllipse(x - 10, y - 30, 3, 5)
        painter.drawEllipse(x + 8, y - 30, 3, 5)
        
        # 鼻子
        painter.setBrush(QBrush(QColor(200, 80, 80)))
        painter.drawEllipse(x - 2, y - 30, 4, 4)
        
        # 嘴巴（悲伤的弧线）
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawArc(x - 6, y - 20, 12, 12, 180 * 16, 180 * 16)
        
        # 尾巴（完全下垂）
        tail_x = x + 35
        tail_y = y
        painter.setBrush(QBrush(QColor(200, 160, 80)))
        painter.drawEllipse(tail_x, tail_y, 10, 5)
        
        # 腿（无力）
        leg_color = QColor(200, 160, 80)
        painter.setBrush(QBrush(leg_color))
        painter.drawEllipse(x - 20, y + 20, 6, 10)
        painter.drawEllipse(x - 8, y + 20, 6, 10)
        painter.drawEllipse(x + 2, y + 20, 6, 10)
        painter.drawEllipse(x + 14, y + 20, 6, 10)
        
        # 悲伤符号
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(x - 40, y - 50, "💧")
    
    def toggle_melee_mode(self):
        print("Toggle Melee Mode")
        self.battle_mode = True  # 进入近战模式
        self.play_melee_idle()
        self.update()

    def play_melee_idle(self):
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets', 'peppercat')
        sheet = os.path.join(asset_dir, 'fightwalk.png')
        self._load_anim_vertical(sheet, 2)
        self.anim_state = 'melee_idle'
        self.anim_playing = True
        self.anim_timer.start(120)
        self.update()

    def play_melee_attack(self):
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets', 'peppercat')
        sheet = os.path.join(asset_dir, 'fight.png')
        self._load_anim_vertical(sheet, 2)
        self.anim_state = 'melee_attack'
        self.anim_playing = True
        self.anim_timer.start(120)
        self.update()

    def play_melee_move(self, direction):
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets', 'peppercat')
        if direction == 'up':
            sheet = os.path.join(asset_dir, 'up.png')
        elif direction == 'down':
            sheet = os.path.join(asset_dir, 'down.png')
        elif direction == 'left':
            sheet = os.path.join(asset_dir, 'left.png')
            self.facing_right = False
        elif direction == 'right':
            sheet = os.path.join(asset_dir, 'right.png')
            self.facing_right = True
        elif direction == 'jump':
            sheet = os.path.join(asset_dir, 'jump.png')
        else:
            sheet = os.path.join(asset_dir, 'fightwalk.png')
        self._load_anim_vertical(sheet, 2)
        self.anim_state = f'melee_{direction}'
        self.anim_playing = True
        self.anim_timer.start(120)
        self.update()

    def play_melee_walk(self, direction):
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets', 'peppercat')
        sheet = os.path.join(asset_dir, 'fightwalk.png')
        if direction == 'left':
            self.facing_right = False
        elif direction == 'right':
            self.facing_right = True
        # 上下不改变朝向
        self._load_anim_vertical(sheet, 2)
        self.anim_state = f'melee_walk_{direction}'
        self.anim_playing = True
        self.anim_timer.start(120)
        self.update()

    def _load_anim_vertical(self, sheet_path, frame_count):
        from PyQt6.QtGui import QPixmap
        sheet = QPixmap(sheet_path)
        w = sheet.width()
        h = sheet.height() // frame_count
        self.anim_frames = [sheet.copy(0, i * h, w, h) for i in range(frame_count)]
        self.anim_index = 0

    def update_animation_external(self):
        """更新动画（供外部调用）"""
        self.update_animation() 

    def handle_key_event(self, key):
        from PyQt6.QtCore import Qt
        if self.battle_mode:
            # 近战模式：WSAD/J/Q/E/R都有效
            if key == Qt.Key.Key_W or key == Qt.Key.Key_Up:
                self.play_melee_walk('up')
            elif key == Qt.Key.Key_S or key == Qt.Key.Key_Down:
                self.play_melee_walk('down')
            elif key == Qt.Key.Key_A or key == Qt.Key.Key_Left:
                self.play_melee_walk('left')
            elif key == Qt.Key.Key_D or key == Qt.Key.Key_Right:
                self.play_melee_walk('right')
            elif key == Qt.Key.Key_Space:
                self.play_melee_move('jump')
            elif key == Qt.Key.Key_J:
                self.play_melee_attack()
            elif key == Qt.Key.Key_Q:
                self.cast_fireball()
            elif key == Qt.Key.Key_E:
                self.cast_iceball()
            elif key == Qt.Key.Key_R:
                self.cast_lightning()
        else:
            # 远程模式：只响应技能键，WSAD无效
            if key == Qt.Key.Key_Q:
                self.cast_fireball()
            elif key == Qt.Key.Key_E:
                self.cast_iceball()
            elif key == Qt.Key.Key_R:
                self.cast_lightning()
            elif key == Qt.Key.Key_Z:
                self.toggle_battle_mode()
            elif key == Qt.Key.Key_J:
                self.play_attack_anim('sword') 

    def play_attack_anim(self, attack_type):
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets', 'peppercat')
        if attack_type == 'fireball':
            sheet = os.path.join(asset_dir, 'fireball.png')
        elif attack_type == 'iceball':
            sheet = os.path.join(asset_dir, 'iceball.png')
        elif attack_type == 'lighting':
            sheet = os.path.join(asset_dir, 'lighting.png')
        elif attack_type == 'sword':
            sheet = os.path.join(asset_dir, 'fight.png')
        else:
            return
        self._load_anim(sheet, 2)
        self.anim_state = f'attack_{attack_type}'
        self.anim_playing = True
        self.anim_timer.start(120)
        self.update()

    def _load_anim(self, sheet_path, frame_count):
        from PyQt6.QtGui import QPixmap
        sheet = QPixmap(sheet_path)
        w = sheet.width() // frame_count
        h = sheet.height()
        self.anim_frames = [sheet.copy(i * w, 0, w, h) for i in range(frame_count)]
        self.anim_index = 0

    def move_up(self):
        print("Move Up")
        # TODO: 移动宠物向上

    def move_down(self):
        print("Move Down")
        # TODO: 移动宠物向下

    def move_left(self):
        print("Move Left")
        # TODO: 移动宠物向左
        self.facing_right = False
        self.play_walk_anim()
        self.update()

    def move_right(self):
        print("Move Right")
        # TODO: 移动宠物向右
        self.facing_right = True
        self.play_walk_anim()
        self.update()

    def jump(self):
        print("Jump")
        # TODO: 播放跳跃动画

    def toggle_battle_mode(self):
        self.battle_mode = not self.battle_mode
        print(f"Battle mode: {self.battle_mode}")
        self.play_walk_anim()

    def play_walk_anim(self):
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets', 'peppercat')
        if self.battle_mode:
            sheet = os.path.join(asset_dir, 'fightwalk.png')
            self._load_anim_vertical(sheet, 2)
        else:
            sheet = os.path.join(asset_dir, 'walk.png')
            self._load_anim(sheet, 2)
        self.anim_state = 'walk'
        self.anim_playing = True
        self.anim_timer.start(120)
        self.update() 

    def cast_fireball(self):
        width = self.width()
        height = self.height()
        if self.anim_frames:
            pet_fw = self.anim_frames[self.anim_index].width()
            pet_fh = self.anim_frames[self.anim_index].height()
        else:
            pet_fw, pet_fh = 80, 160
        offset_x = pet_fw // 2 - 100  # 让火球更靠前
        offset_y = 0
        if self.facing_right:
            x = width // 2 + offset_x
            direction = False  # 让火球向左飞
        else:
            x = width // 2 - offset_x
            direction = True   # 让火球向右飞
        y = height // 2 + offset_y
        global_pos = self.mapToGlobal(QPoint(x, y))
        fireball = FireballSprite((global_pos.x(), global_pos.y()), direction, None)
        fireball.destroyed.connect(lambda obj=None, fb=fireball: self._remove_fireball(fb))
        self.active_fireballs.append(fireball)

    def cast_iceball(self):
        width = self.width()
        height = self.height()
        if self.anim_frames:
            pet_fw = self.anim_frames[self.anim_index].width()
            pet_fh = self.anim_frames[self.anim_index].height()
        else:
            pet_fw, pet_fh = 80, 160
        offset_x = pet_fw // 2 - 100
        offset_y = 0
        if self.facing_right:
            x = width // 2 + offset_x
            direction = False
        else:
            x = width // 2 - offset_x
            direction = True
        y = height // 2 + offset_y
        global_pos = self.mapToGlobal(QPoint(x, y))
        iceball = IceballSprite((global_pos.x(), global_pos.y()), direction, None)
        iceball.destroyed.connect(lambda obj=None, fb=iceball: self._remove_fireball(fb))
        self.active_fireballs.append(iceball)

    def cast_lightning(self):
        width = self.width()
        height = self.height()
        if self.anim_frames:
            pet_fw = self.anim_frames[self.anim_index].width()
            pet_fh = self.anim_frames[self.anim_index].height()
        else:
            pet_fw, pet_fh = 80, 160
        offset_x = pet_fw // 2 - 100
        offset_y = 0
        if self.facing_right:
            x = width // 2 + offset_x
            direction = False
        else:
            x = width // 2 - offset_x
            direction = True
        y = height // 2 + offset_y
        global_pos = self.mapToGlobal(QPoint(x, y))
        lightning = LightningSprite((global_pos.x(), global_pos.y()), direction, None)
        lightning.destroyed.connect(lambda obj=None, fb=lightning: self._remove_fireball(fb))
        self.active_fireballs.append(lightning)

    def _remove_fireball(self, fireball):
        if fireball in self.active_fireballs:
            self.active_fireballs.remove(fireball) 