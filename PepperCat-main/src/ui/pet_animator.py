#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌宠动画录制与预览界面
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QComboBox, QSlider
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QPointF, QTimer
import math

class AnimatorPartInstance:
    def __init__(self, name, pixels, offset, angle, scale, anchor, z_order):
        self.name = name
        self.pixels = pixels
        self.offset = QPointF(*offset)
        self.angle = angle
        self.scale = scale
        self.anchor = QPointF(*anchor)
        self.z_order = z_order
        self.keyframes = [{'time': 0, 'angle': angle, 'offset': (offset[0], offset[1])}]

    def get_state_at(self, t):
        # 简单线性插值
        if len(self.keyframes) == 1:
            return self.keyframes[0]
        prev, next = self.keyframes[0], self.keyframes[-1]
        for i in range(1, len(self.keyframes)):
            if t < self.keyframes[i]['time']:
                prev, next = self.keyframes[i-1], self.keyframes[i]
                break
        dt = next['time'] - prev['time']
        if dt == 0:
            return prev
        ratio = (t - prev['time']) / dt
        angle = prev['angle'] + (next['angle'] - prev['angle']) * ratio
        ox = prev['offset'][0] + (next['offset'][0] - prev['offset'][0]) * ratio
        oy = prev['offset'][1] + (next['offset'][1] - prev['offset'][1]) * ratio
        return {'time': t, 'angle': angle, 'offset': (ox, oy)}

class AnimatorCanvas(QWidget):
    def __init__(self, part_states, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 400)
        self.parts = [AnimatorPartInstance(
            p['name'], p['pixels'], p['offset'], p['angle'], p['scale'], p['anchor'], p['z_order']) for p in part_states]
        self.selected_part = self.parts[0] if self.parts else None
        self.drag_offset = QPointF(0,0)
        self.mode = 'idle'  # 'move', 'rotate'
        self.current_time = 0
        self.max_time = 2

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(240,240,240))
        # 按z_order排序
        for part in sorted(self.parts, key=lambda p: p.z_order):
            state = part.get_state_at(self.current_time)
            painter.save()
            painter.translate(QPointF(*state['offset']))
            painter.rotate(state['angle'])
            painter.scale(part.scale, part.scale)
            for px in part.pixels:
                color = QColor.fromRgba(px['color'])
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(px['x']*6, px['y']*6, 6, 6)
            # 画锚点
            painter.setPen(QPen(QColor(255,0,0), 2))
            painter.setBrush(QBrush(QColor(255,255,255)))
            painter.drawEllipse(int(part.anchor.x()*6-4), int(part.anchor.y()*6-4), 8, 8)
            painter.restore()
        # 高亮选中
        if self.selected_part:
            painter.save()
            state = self.selected_part.get_state_at(self.current_time)
            painter.translate(QPointF(*state['offset']))
            painter.rotate(state['angle'])
            painter.scale(self.selected_part.scale, self.selected_part.scale)
            painter.setPen(QPen(QColor(0,120,255), 2, Qt.PenStyle.DashLine))
            painter.drawRect(0, 0, 32*6, 32*6)
            painter.restore()

    def mousePressEvent(self, event):
        pos = event.position()
        for part in sorted(self.parts, key=lambda p: -p.z_order):
            state = part.get_state_at(self.current_time)
            local = pos - QPointF(*state['offset'])
            local = self._rotate_point(local, -state['angle'])
            local = local / part.scale
            if 0 <= local.x() < 32*6 and 0 <= local.y() < 32*6:
                self.selected_part = part
                if self.mode == 'move':
                    self.drag_offset = pos - QPointF(*state['offset'])
                elif self.mode == 'rotate':
                    self.drag_offset = pos
                self.update()
                return
        self.selected_part = None
        self.update()

    def mouseMoveEvent(self, event):
        if self.selected_part and event.buttons() & Qt.MouseButton.LeftButton:
            if self.mode == 'move':
                new_offset = event.position() - self.drag_offset
                self.selected_part.keyframes[-1]['offset'] = (new_offset.x(), new_offset.y())
            elif self.mode == 'rotate':
                state = self.selected_part.get_state_at(self.current_time)
                anchor = QPointF(state['offset'][0]+self.selected_part.anchor.x()*6, state['offset'][1]+self.selected_part.anchor.y()*6)
                v1 = self.drag_offset - anchor
                v2 = event.position() - anchor
                angle = math.degrees(math.atan2(v2.y(), v2.x()) - math.atan2(v1.y(), v1.x()))
                self.selected_part.keyframes[-1]['angle'] = state['angle'] + angle
            self.update()

    def _rotate_point(self, pt, angle):
        rad = math.radians(angle)
        x = pt.x()*math.cos(rad) - pt.y()*math.sin(rad)
        y = pt.x()*math.sin(rad) + pt.y()*math.cos(rad)
        return QPointF(x, y)

    def set_mode(self, mode):
        self.mode = mode

    def set_time(self, t):
        self.current_time = t
        self.update()

    def add_keyframe(self):
        if self.selected_part:
            t = self.current_time
            state = self.selected_part.get_state_at(t)
            self.selected_part.keyframes.append({'time': t, 'angle': state['angle'], 'offset': state['offset']})
            self.selected_part.keyframes.sort(key=lambda k: k['time'])
            self.update()

    def del_keyframe(self):
        if self.selected_part and len(self.selected_part.keyframes) > 1:
            t = self.current_time
            self.selected_part.keyframes = [k for k in self.selected_part.keyframes if k['time'] != t]
            self.update()

    def get_animation_data(self):
        return {
            p.name: {
                'keyframes': p.keyframes,
                'anchor': (p.anchor.x(), p.anchor.y()),
                'pixels': p.pixels  # 新增pixels字段，保证动画数据完整
            }
            for p in self.parts
        }

class PetAnimator(QDialog):
    def __init__(self, part_states, parent=None):
        super().__init__(parent)
        self.setWindowTitle("桌宠动画录制与预览")
        self.canvas = AnimatorCanvas(part_states)
        layout = QVBoxLayout(self)
        # 部件选择
        part_names = [p['name'] for p in part_states]
        self.part_combo = QComboBox()
        self.part_combo.addItems(part_names)
        self.part_combo.currentIndexChanged.connect(self.on_part_changed)
        layout.addWidget(QLabel("选择部件："))
        layout.addWidget(self.part_combo)
        # 操作按钮
        btn_layout = QHBoxLayout()
        move_btn = QPushButton("移动关键帧")
        move_btn.clicked.connect(lambda: self.canvas.set_mode('move'))
        btn_layout.addWidget(move_btn)
        rot_btn = QPushButton("旋转关键帧")
        rot_btn.clicked.connect(lambda: self.canvas.set_mode('rotate'))
        btn_layout.addWidget(rot_btn)
        addkf_btn = QPushButton("添加关键帧")
        addkf_btn.clicked.connect(self.canvas.add_keyframe)
        btn_layout.addWidget(addkf_btn)
        delkf_btn = QPushButton("删除关键帧")
        delkf_btn.clicked.connect(self.canvas.del_keyframe)
        btn_layout.addWidget(delkf_btn)
        layout.addLayout(btn_layout)
        # 时间轴
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 20)
        self.slider.valueChanged.connect(self.on_time_changed)
        layout.addWidget(QLabel("时间轴 (0-2s)："))
        layout.addWidget(self.slider)
        # 预览按钮
        preview_btn = QPushButton("预览动画")
        preview_btn.clicked.connect(self.preview_anim)
        layout.addWidget(preview_btn)
        layout.addWidget(self.canvas)
        # 完成
        ok_btn = QPushButton("完成")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self._on_anim_tick)
        self.anim_playing = False
        self.anim_time = 0

    def on_part_changed(self, idx):
        self.canvas.selected_part = self.canvas.parts[idx]
        self.canvas.update()

    def on_time_changed(self, v):
        t = v / 10.0
        self.canvas.set_time(t)

    def preview_anim(self):
        self.anim_time = 0
        self.anim_playing = True
        self.anim_timer.start(50)

    def _on_anim_tick(self):
        if not self.anim_playing:
            return
        t = self.anim_time / 10.0
        self.canvas.set_time(t)
        self.anim_time += 1
        if self.anim_time > 20:
            self.anim_playing = False
            self.anim_timer.stop()

    def get_animation_data(self):
        return self.canvas.get_animation_data() 