#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌宠启动测试脚本
测试桌宠是否能正常启动和运行
"""

import sys
import os
import time
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pet_startup():
    """测试桌宠启动"""
    print("🚀 开始桌宠启动测试")
    print("=" * 40)
    
    try:
        # 创建QApplication
        app = QApplication(sys.argv)
        print("✅ QApplication创建成功")
        
        # 导入主窗口
        from src.ui.main_window import MainWindow
        print("✅ 主窗口模块导入成功")
        
        # 创建主窗口
        window = MainWindow()
        print("✅ 主窗口创建成功")
        
        # 显示窗口
        window.show()
        print("✅ 主窗口显示成功")
        
        # 测试基本功能
        print("\n=== 测试基本功能 ===")
        
        # 测试桌宠智能体
        pet_agent = window.pet_agent
        print(f"✅ 桌宠智能体: {pet_agent.name}")
        
        # 测试状态获取
        stats = pet_agent.get_stats_summary()
        print(f"✅ 状态获取: {len(stats)}字符")
        
        # 测试活动检测
        activity = pet_agent.get_activity_summary()
        print(f"✅ 活动检测: {activity}")
        
        # 测试消息处理
        response = pet_agent._handle_chat("你好")
        print(f"✅ 消息处理: {response[:50]}...")
        
        # 测试跟随功能
        print(f"✅ 跟随功能: {'已启用' if window.follow_mouse_enabled else '未启用'}")
        
        print("\n=== 功能测试完成 ===")
        print("桌宠已成功启动，可以正常使用！")
        print("\n使用说明:")
        print("- 左键拖拽: 移动桌宠")
        print("- 右键点击: 切换跟随状态")
        print("- 左键双击: 打开功能菜单")
        print("- 按ESC键: 退出程序")
        
        # 设置定时器，5秒后自动关闭（用于自动化测试）
        def auto_close():
            print("\n⏰ 5秒后自动关闭（测试模式）")
            app.quit()
        
        timer = QTimer()
        timer.timeout.connect(auto_close)
        timer.start(5000)  # 5秒
        
        # 运行应用
        return app.exec()
        
    except Exception as e:
        print(f"❌ 桌宠启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

def test_pet_interactive():
    """交互式测试桌宠"""
    print("🎮 交互式桌宠测试")
    print("桌宠将保持运行，你可以手动测试各种功能")
    print("按Ctrl+C退出测试")
    
    try:
        # 创建QApplication
        app = QApplication(sys.argv)
        
        # 导入并创建主窗口
        from src.ui.main_window import MainWindow
        window = MainWindow()
        window.show()
        
        print("✅ 桌宠已启动，开始交互式测试...")
        print("提示:")
        print("- 尝试拖拽桌宠")
        print("- 右键点击切换跟随")
        print("- 双击打开菜单")
        print("- 测试各种功能")
        
        # 运行应用（保持运行）
        return app.exec()
        
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
        return 0
    except Exception as e:
        print(f"❌ 交互式测试失败: {e}")
        return 1

def main():
    """主函数"""
    print("桌宠启动测试工具")
    print("选择测试模式:")
    print("1. 快速测试 (5秒自动关闭)")
    print("2. 交互式测试 (手动控制)")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        return test_pet_startup()
    elif choice == "2":
        return test_pet_interactive()
    else:
        print("无效选择，使用默认快速测试")
        return test_pet_startup()

if __name__ == "__main__":
    sys.exit(main()) 