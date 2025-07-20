#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌宠部件拼装与锚点设置界面
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QSlider
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QPointF
import math

class PartInstance:
    def __init__(self, name, pixels, color=QColor(0,0,0)):
        self.name = name
        self.pixels = pixels  # [{'x':..,'y':..,'color':..}]
        self.offset = QPointF(160, 160)  # 初始位置
        self.angle = 0.0
        self.scale = 1.0
        self.z_order = 0
        self.anchor = QPointF(16, 16)  # 默认锚点
        self.selected = False

class AssemblerCanvas(QWidget):
    def __init__(self, part_dict, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 400)
        self.parts = []
        for i, (name, pixels) in enumerate(part_dict.items()):
            inst = PartInstance(name, pixels)
            inst.z_order = i
            self.parts.append(inst)
        self.selected_part = None
        self.drag_offset = QPointF(0,0)
        self.setting_anchor = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(240,240,240))
        # 按z_order排序
        for part in sorted(self.parts, key=lambda p: p.z_order):
            painter.save()
            painter.translate(part.offset)
            painter.rotate(part.angle)
            painter.scale(part.scale, part.scale)
            # 画像素
            for px in part.pixels:
                color = QColor.fromRgba(px['color'])
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(px['x']*6, px['y']*6, 6, 6)
            # 画锚点
            painter.setPen(QPen(QColor(255,0,0), 2))
            painter.setBrush(QBrush(QColor(255,255,255)))
            x = int(part.anchor.x()*6-4)
            y = int(part.anchor.y()*6-4)
            w = int(8)
            h = int(8)
            painter.drawEllipse(x, y, w, h)
            painter.restore()
        # 高亮选中
        if self.selected_part:
            painter.save()
            painter.translate(self.selected_part.offset)
            painter.rotate(self.selected_part.angle)
            painter.scale(self.selected_part.scale, self.selected_part.scale)
            painter.setPen(QPen(QColor(0,120,255), 2, Qt.PenStyle.DashLine))
            painter.drawRect(0, 0, 32*6, 32*6)
            painter.restore()

    def mousePressEvent(self, event):
        pos = event.position()
        # 逆序找z_order最高的部件
        for part in sorted(self.parts, key=lambda p: -p.z_order):
            local = pos - part.offset
            local = self._rotate_point(local, -part.angle)
            local = local / part.scale
            if 0 <= local.x() < 32*6 and 0 <= local.y() < 32*6:
                self.selected_part = part
                self.drag_offset = pos - part.offset
                if self.setting_anchor:
                    # 设置锚点
                    part.anchor = QPointF(local.x()/6, local.y()/6)
                    self.setting_anchor = False
                    self.update()
                    return
                self.update()
                return
        self.selected_part = None
        self.update()

    def mouseMoveEvent(self, event):
        if self.selected_part and event.buttons() & Qt.MouseButton.LeftButton and not self.setting_anchor:
            self.selected_part.offset = event.position() - self.drag_offset
            self.update()

    def wheelEvent(self, event):
        if self.selected_part:
            delta = event.angleDelta().y()
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # 缩放
                self.selected_part.scale = max(0.2, min(3.0, self.selected_part.scale + delta/1200))
            else:
                # 旋转
                self.selected_part.angle += delta/8
            self.update()

    def _rotate_point(self, pt, angle):
        rad = math.radians(angle)
        x = pt.x()*math.cos(rad) - pt.y()*math.sin(rad)
        y = pt.x()*math.sin(rad) + pt.y()*math.cos(rad)
        return QPointF(x, y)

    def set_anchor_mode(self, enable):
        self.setting_anchor = enable

    def bring_forward(self):
        if self.selected_part:
            self.selected_part.z_order += 1
            self.update()
    def send_backward(self):
        if self.selected_part:
            self.selected_part.z_order -= 1
            self.update()

    def get_part_states(self):
        # 返回所有部件的拼装参数
        return [
            {
                'name': p.name,
                'offset': (p.offset.x(), p.offset.y()),
                'angle': p.angle,
                'scale': p.scale,
                'anchor': (p.anchor.x(), p.anchor.y()),
                'z_order': p.z_order,
                'pixels': p.pixels
            } for p in self.parts
        ]

class PetAssembler(QDialog):
    def __init__(self, part_pixels, parent=None):
        super().__init__(parent)
        self.setWindowTitle("桌宠拼装与锚点设置")
        self.canvas = AssemblerCanvas(part_pixels)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        btn_layout = QHBoxLayout()
        anchor_btn = QPushButton("设置锚点")
        anchor_btn.clicked.connect(lambda: self.canvas.set_anchor_mode(True))
        btn_layout.addWidget(anchor_btn)
        up_btn = QPushButton("上移一层")
        up_btn.clicked.connect(self.canvas.bring_forward)
        btn_layout.addWidget(up_btn)
        down_btn = QPushButton("下移一层")
        down_btn.clicked.connect(self.canvas.send_backward)
        btn_layout.addWidget(down_btn)
        ok_btn = QPushButton("完成")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def get_assembled_parts(self):
        return self.canvas.get_part_states() 