#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视力检测功能测试脚本
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.vision_test import VisionTestTool

async def test_vision_test():
    """测试视力检测功能"""
    print("=== 视力检测功能测试 ===")
    
    try:
        # 创建视力检测工具
        vision_tool = VisionTestTool()
        
        print("1. 测试视力检测工具初始化...")
        print(f"工具名称: {vision_tool.name}")
        print(f"工具描述: {vision_tool.description}")
        print("✅ 工具初始化成功")
        
        print("\n2. 测试视力检测执行...")
        print("注意：这将打开摄像头进行实际检测")
        print("请确保摄像头可用，并按照提示进行手势操作")
        
        # 执行视力检测
        result = await vision_tool.execute()
        
        print(f"\n3. 检测结果:")
        print(result)
        
        print("\n✅ 视力检测功能测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_vision_test_sync():
    """同步测试视力检测功能"""
    print("=== 视力检测功能同步测试 ===")
    
    try:
        from src.tools.vision_test import VisionTestWindow
        
        print("1. 创建视力检测窗口...")
        window = VisionTestWindow()
        window.create_window()
        
        print("2. 窗口已创建，请手动操作进行测试")
        print("窗口功能说明:")
        print("- 点击'开始检测'按钮开始视力检测")
        print("- 用手势指示E字开口方向")
        print("- 检测完成后查看结果")
        print("- 点击'关闭'按钮结束测试")
        
        # 保持窗口运行
        if window.window:
            window.window.mainloop()
        
        print("✅ 同步测试完成")
        
    except Exception as e:
        print(f"❌ 同步测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("视力检测功能测试")
    print("选择测试模式:")
    print("1. 异步测试 (推荐)")
    print("2. 同步测试 (手动操作)")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        asyncio.run(test_vision_test())
    elif choice == "2":
        test_vision_test_sync()
    else:
        print("无效选择，使用默认异步测试")
        asyncio.run(test_vision_test()) 