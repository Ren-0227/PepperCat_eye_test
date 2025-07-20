#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
像素桌宠自定义设计器
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QColorDialog, QLabel, QWidget)
from PyQt6.QtGui import QPainter, QColor, QImage, QMouseEvent, QPen
from PyQt6.QtCore import Qt, QSize

class PixelCanvas(QWidget):
    def __init__(self, size=32, pixel_size=16, parent=None):
        super().__init__(parent)
        self.grid_size = size
        self.pixel_size = pixel_size
        self.image = QImage(size, size, QImage.Format.Format_ARGB32)
        self.image.fill(Qt.GlobalColor.transparent)
        self.pen_color = QColor(0, 0, 0)
        self.eraser = False
        self.last_image = self.image.copy()
        self.setFixedSize(size*pixel_size, size*pixel_size)

    def paintEvent(self, event):
        painter = QPainter(self)
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                color = QColor(self.image.pixel(x, y))
                if color.alpha() > 0:
                    painter.setBrush(color)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawRect(x*self.pixel_size, y*self.pixel_size, self.pixel_size, self.pixel_size)
        # 画网格
        painter.setPen(QPen(QColor(200,200,200), 1))
        for i in range(self.grid_size+1):
            painter.drawLine(0, i*self.pixel_size, self.grid_size*self.pixel_size, i*self.pixel_size)
            painter.drawLine(i*self.pixel_size, 0, i*self.pixel_size, self.grid_size*self.pixel_size)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_image = self.image.copy()
            self.draw_at(event.position())

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.draw_at(event.position())

    def draw_at(self, pos):
        x = int(pos.x() // self.pixel_size)
        y = int(pos.y() // self.pixel_size)
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            if self.eraser:
                self.image.setPixelColor(x, y, QColor(0,0,0,0))
            else:
                self.image.setPixelColor(x, y, self.pen_color)
            self.update()

    def set_pen_color(self, color):
        self.pen_color = color
        self.eraser = False

    def set_eraser(self):
        self.eraser = True

    def undo(self):
        self.image = self.last_image.copy()
        self.update()

    def clear(self):
        self.image.fill(Qt.GlobalColor.transparent)
        self.update()

    def get_pixels(self):
        pixels = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                color = QColor(self.image.pixel(x, y))
                # 自动将纯黑色视为透明
                if color.red() == 0 and color.green() == 0 and color.blue() == 0 and color.alpha() == 255:
                    continue
                if color.alpha() > 0:
                    pixels.append({'x': x, 'y': y, 'color': color.rgba()})
        return pixels

class PetDesigner(QDialog):
    def __init__(self, size=32, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义像素桌宠")
        self.canvas = PixelCanvas(size=size, pixel_size=12)
        self.selected_color = QColor(0,0,0)
        self.init_ui()
        self.result_pixels = None

    def init_ui(self):
        layout = QVBoxLayout(self)
        # 警示标签
        warn_label = QLabel("如需要黑色部分，请用黑色绘制，否则生成时会变为透明")
        warn_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(warn_label)
        # 工具栏
        tool_layout = QHBoxLayout()
        color_btn = QPushButton("选择颜色")
        color_btn.clicked.connect(self.choose_color)
        pen_btn = QPushButton("画笔")
        pen_btn.clicked.connect(lambda: self.canvas.set_pen_color(self.selected_color))
        eraser_btn = QPushButton("橡皮")
        eraser_btn.clicked.connect(self.canvas.set_eraser)
        undo_btn = QPushButton("撤销")
        undo_btn.clicked.connect(self.canvas.undo)
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.canvas.clear)
        tool_layout.addWidget(color_btn)
        tool_layout.addWidget(pen_btn)
        tool_layout.addWidget(eraser_btn)
        tool_layout.addWidget(undo_btn)
        tool_layout.addWidget(clear_btn)
        layout.addLayout(tool_layout)
        # 画布
        layout.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignCenter)
        # 生成按钮
        gen_btn = QPushButton("生成桌宠")
        gen_btn.clicked.connect(self.on_generate)
        layout.addWidget(gen_btn)

    def choose_color(self):
        color = QColorDialog.getColor(self.selected_color, self, "选择颜色")
        if color.isValid():
            self.selected_color = color
            self.canvas.set_pen_color(color)

    def on_generate(self):
        self.result_pixels = self.canvas.get_pixels()
        self.accept()

    def get_pixels(self):
        return self.result_pixels 

class MultiPartPetDesigner(QDialog):
    """多部件像素桌宠设计器"""
    def __init__(self, size=32, parent=None):
        super().__init__(parent)
        self.setWindowTitle("分部件像素桌宠设计")
        self.grid_size = size
        self.parts = [
            ("body", "绘制桌宠主体"),
            ("left_arm", "绘制左手臂"),
            ("right_arm", "绘制右手臂"),
            ("left_leg", "绘制左腿"),
            ("right_leg", "绘制右腿")
        ]
        self.pixels_dict = {}
        self.current_part = 0
        self.selected_color = QColor(0,0,0)
        self.init_ui()

    def init_ui(self):
        self._layout = QVBoxLayout(self)
        self.label = QLabel()
        self._layout.addWidget(self.label)
        self.canvas = PixelCanvas(size=self.grid_size, pixel_size=12)  # 先创建canvas
        # 工具栏
        self.tool_layout = QHBoxLayout()
        self.color_btn = QPushButton("选择颜色")
        self.color_btn.clicked.connect(self.choose_color)
        self.pen_btn = QPushButton("画笔")
        self.pen_btn.clicked.connect(lambda: self.canvas.set_pen_color(self.selected_color))
        self.eraser_btn = QPushButton("橡皮")
        self.eraser_btn.clicked.connect(self.canvas.set_eraser)
        self.undo_btn = QPushButton("撤销")
        self.undo_btn.clicked.connect(self.canvas.undo)
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.canvas.clear)
        self.tool_layout.addWidget(self.color_btn)
        self.tool_layout.addWidget(self.pen_btn)
        self.tool_layout.addWidget(self.eraser_btn)
        self.tool_layout.addWidget(self.undo_btn)
        self.tool_layout.addWidget(self.clear_btn)
        self._layout.addLayout(self.tool_layout)
        self._layout.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignCenter)
        btn_layout = QHBoxLayout()
        self.next_btn = QPushButton("下一步")
        self.next_btn.clicked.connect(self.next_part)
        btn_layout.addWidget(self.next_btn)
        self._layout.addLayout(btn_layout)
        self.update_part()

    def choose_color(self):
        color = QColorDialog.getColor(self.selected_color, self, "选择颜色")
        if color.isValid():
            self.selected_color = color
            self.canvas.set_pen_color(color)

    def update_part(self):
        part_key, part_name = self.parts[self.current_part]
        self.label.setText(f"{part_name}（{self.current_part+1}/{len(self.parts)}）")
        self.canvas.clear()
        self.next_btn.setText("完成" if self.current_part == len(self.parts)-1 else "下一步")
        # 工具栏按钮状态同步
        self.canvas.set_pen_color(self.selected_color)

    def next_part(self):
        part_key, _ = self.parts[self.current_part]
        self.pixels_dict[part_key] = self.canvas.get_pixels()
        if self.current_part < len(self.parts)-1:
            self.current_part += 1
            self.update_part()
        else:
            self.accept()

    def get_all_parts(self):
        return self.pixels_dict 