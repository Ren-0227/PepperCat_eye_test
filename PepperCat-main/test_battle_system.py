#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试对战系统的新功能
包括桌宠移动控制和动态攻击路径
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.battle_dialog import BattleDialog

def test_battle_system():
    """测试对战系统"""
    app = QApplication(sys.argv)
    
    # 创建对战对话框
    battle_dialog = BattleDialog(pet_name="测试桌宠")
    battle_dialog.show()
    
    # 模拟一些测试操作
    def run_tests():
        print("=== 对战系统测试 ===")
        print("1. 测试桌宠移动控制")
        print("   - 点击屏幕任意位置移动桌宠")
        print("   - 使用'移动到中心'和'移动到角落'按钮")
        
        print("\n2. 测试攻击参数控制")
        print("   - 调整火球Y轴偏移滑块")
        print("   - 调整弓箭角度滑块（30-90度）")
        
        print("\n3. 测试动态攻击路径")
        print("   - 移动桌宠后攻击路径会相应改变")
        print("   - 火球会根据Y轴偏移调整轨迹")
        print("   - 弓箭会根据角度调整抛物线")
        
        print("\n4. 网络对战功能")
        print("   - 创建房间或加入房间")
        print("   - 实时显示其他玩家移动")
        print("   - 攻击动画会根据双方位置计算")
        
        print("\n=== 使用说明 ===")
        print("- 点击屏幕任意位置移动桌宠")
        print("- 调整攻击参数后选择目标进行攻击")
        print("- 观察攻击路径的动态变化")
        print("- 在局域网中与其他玩家进行实时对战")
    
    # 延迟执行测试说明
    timer = QTimer()
    timer.singleShot(1000, run_tests)
    
    return app.exec()

if __name__ == "__main__":
    test_battle_system() 