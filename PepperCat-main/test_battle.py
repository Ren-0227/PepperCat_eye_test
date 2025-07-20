#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对战功能测试脚本
"""

import sys
import time
import threading
from PyQt6.QtWidgets import QApplication
from src.ui.battle_dialog import BattleDialog

def test_battle_system():
    """测试对战系统"""
    app = QApplication(sys.argv)
    
    # 创建对战对话框
    battle_dialog = BattleDialog(pet_name="测试桌宠")
    battle_dialog.show()
    
    print("对战系统测试启动")
    print("1. 点击'创建房间'启动服务器")
    print("2. 在另一个实例中点击'加入房间'连接到服务器")
    print("3. 选择目标玩家并点击攻击按钮")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_battle_system() 