#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示对战系统的新功能
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import QTimer

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.battle_dialog import BattleDialog

class BattleDemo(QMainWindow):
    """对战功能演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("对战系统功能演示")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("🎮 桌宠对战系统 - 新功能演示")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # 功能说明
        features = QLabel("""
        ✨ 新功能特性：
        
        1. 🖱️ 桌宠移动控制
           - 点击屏幕任意位置移动桌宠
           - 平滑的移动动画效果
           - 实时位置显示
        
        2. 🎯 动态攻击路径
           - 火球Y轴偏移控制
           - 弓箭角度调整（30-90度）
           - 攻击路径根据位置动态计算
        
        3. 🌐 网络对战增强
           - 实时玩家位置同步
           - 动态攻击动画
           - 多玩家实时对战
        
        4. ⚡ 攻击效果优化
           - 火球轨迹可调整
           - 弓箭抛物线效果
           - 受击动画增强
        
        5. ⚔️ 战斗规则系统
           - 攻击冷却时间
           - 状态效果系统
           - 伤害计算机制
        """)
        features.setStyleSheet("font-size: 14px; margin: 20px;")
        layout.addWidget(features)
        
        # 战斗规则说明
        rules_text = QTextEdit()
        rules_text.setMaximumHeight(200)
        rules_text.setPlainText("""
🔥 火球攻击: 25伤害, 2秒冷却, 灼烧3秒(每秒5伤害)
🏹 弓箭攻击: 35伤害, 3秒冷却, 无特殊效果
⚡ 闪电攻击: 20伤害, 1.5秒冷却, 电击4秒(每秒3伤害)
❄️ 冰霜攻击: 15伤害, 4秒冷却, 缓速5秒(移动速度减半)
        """)
        rules_text.setReadOnly(True)
        layout.addWidget(rules_text)
        
        # 演示按钮
        demo_btn = QPushButton("🚀 启动对战演示")
        demo_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 15px 30px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        demo_btn.clicked.connect(self.start_battle_demo)
        layout.addWidget(demo_btn)
        
        # 使用说明
        instructions = QLabel("""
        📋 使用说明：
        
        1. 点击"启动对战演示"按钮
        2. 在对战界面中点击屏幕移动桌宠
        3. 调整攻击参数滑块
        4. 选择目标进行攻击
        5. 观察动态攻击路径效果
        6. 体验攻击冷却和状态效果系统
        7. 在局域网中与其他玩家对战
        """)
        instructions.setStyleSheet("font-size: 12px; margin: 20px; color: #666;")
        layout.addWidget(instructions)
    
    def start_battle_demo(self):
        """启动对战演示"""
        battle_dialog = BattleDialog(pet_name="演示桌宠", parent=self)
        battle_dialog.show()
        
        # 显示演示提示
        QTimer.singleShot(1000, lambda: self.show_demo_tips(battle_dialog))
    
    def show_demo_tips(self, battle_dialog):
        """显示演示提示"""
        print("=== 对战系统演示 ===")
        print("🎯 演示步骤：")
        print("1. 点击屏幕任意位置移动桌宠")
        print("2. 调整'火球Y轴偏移'滑块（-100到100）")
        print("3. 调整'弓箭角度'滑块（30到90度）")
        print("4. 选择在线玩家作为攻击目标")
        print("5. 点击攻击按钮观察动态路径")
        print("6. 体验攻击冷却系统")
        print("7. 观察状态效果系统")
        print("\n💡 战斗规则提示：")
        print("- 火球攻击：25伤害，2秒冷却，灼烧3秒")
        print("- 弓箭攻击：35伤害，3秒冷却，无特殊效果")
        print("- 闪电攻击：20伤害，1.5秒冷却，电击4秒")
        print("- 冰霜攻击：15伤害，4秒冷却，缓速5秒")
        print("\n🎮 策略建议：")
        print("- 利用移动躲避攻击")
        print("- 合理使用攻击冷却时间")
        print("- 观察状态效果持续时间")
        print("- 在局域网中与其他玩家对战")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建演示窗口
    demo = BattleDemo()
    demo.show()
    
    return app.exec()

if __name__ == "__main__":
    main() 