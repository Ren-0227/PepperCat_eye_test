#!/usr/bin/env python3
"""
眼部健康游戏测试脚本
"""

import tkinter as tk
import asyncio
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.tools.eye_games import EyeGamesTool, MemoryGame, FocusGame, ReactionGame

def test_individual_games():
    """测试单个游戏"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    print("测试眼部健康游戏...")
    
    # 测试记忆训练游戏
    print("\n1. 启动记忆训练游戏...")
    memory_game = MemoryGame()
    memory_game.create_window()
    
    # 测试专注力训练游戏
    print("\n2. 启动专注力训练游戏...")
    focus_game = FocusGame()
    focus_game.create_window()
    
    # 测试反应速度训练游戏
    print("\n3. 启动反应速度训练游戏...")
    reaction_game = ReactionGame()
    reaction_game.create_window()
    
    print("\n所有游戏已启动，请在新窗口中测试！")
    print("关闭游戏窗口后程序将退出。")
    
    # 等待所有窗口关闭
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    finally:
        root.destroy()

async def test_eye_games_tool():
    """测试眼部游戏工具"""
    print("测试眼部游戏工具...")
    
    tool = EyeGamesTool()
    
    # 测试启动所有游戏
    print("\n启动所有游戏...")
    result = await tool.execute(game_type="all")
    print(f"结果: {result}")
    
    # 测试启动单个游戏
    print("\n启动记忆训练游戏...")
    result = await tool.execute(game_type="memory")
    print(f"结果: {result}")

if __name__ == "__main__":
    print("眼部健康游戏测试")
    print("=" * 50)
    
    # 选择测试模式
    mode = input("选择测试模式 (1: 单个游戏测试, 2: 工具测试): ").strip()
    
    if mode == "1":
        test_individual_games()
    elif mode == "2":
        asyncio.run(test_eye_games_tool())
    else:
        print("无效选择，默认运行单个游戏测试...")
        test_individual_games() 