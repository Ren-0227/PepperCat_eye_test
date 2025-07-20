#!/usr/bin/env python3
"""
桌宠端图像分析功能测试脚本
"""

import requests
import os
import sys
import json

def test_image_analysis_api():
    """测试Web端图像分析API"""
    print("🔍 测试Web端图像分析API...")
    
    # 检查Web服务是否运行
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Web服务正在运行")
        else:
            print("❌ Web服务响应异常")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Web服务未启动，请先启动Web服务：python start_web_app.py")
        return False
    
    # 测试图片路径
    test_image_path = "../pictures/glaucoma_classification_1.png"
    if not os.path.exists(test_image_path):
        print(f"❌ 测试图片不存在：{test_image_path}")
        return False
    
    print(f"📸 使用测试图片：{test_image_path}")
    
    # 发送图片分析请求
    try:
        with open(test_image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post('http://localhost:5000/api/image/recognition', files=files)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data.get('result', '')
                report = data.get('report', '')
                print(f"✅ 图像分析成功！")
                print(f"📊 分析结果：{result}")
                print(f"📋 AI报告：{report}")
                return True
            else:
                print(f"❌ 图像分析失败：{data.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ API请求失败，状态码：{response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常：{e}")
        return False

def test_pet_agent_image_analysis():
    """测试桌宠代理的图像分析功能"""
    print("\n🐱 测试桌宠代理图像分析功能...")
    
    # 导入桌宠代理
    try:
        sys.path.insert(0, 'src')
        from agent.pet_agent import PetAgent
        
        # 创建桌宠代理实例
        pet = PetAgent("测试宠物")
        
        # 模拟图片分析请求
        test_message = '分析图片名为glaucoma_classification_1.png'
        print(f"💬 模拟用户消息：{test_message}")
        
        # 调用聊天处理函数
        response = pet._handle_chat(test_message)
        print(f"🤖 桌宠响应：{response}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入桌宠代理失败：{e}")
        return False
    except Exception as e:
        print(f"❌ 桌宠代理测试失败：{e}")
        return False

def test_visualize_tool():
    """测试可视化工具"""
    print("\n📊 测试可视化工具...")
    
    try:
        sys.path.insert(0, 'src')
        from openmanus_agent.visualize_tool import VisualizeTool
        import asyncio
        
        # 创建可视化工具实例
        tool = VisualizeTool()
        
        # 测试数据
        test_data = """日期,销售额
2024-01,100
2024-02,150
2024-03,200
2024-04,180"""
        
        print("📈 测试折线图生成...")
        
        # 异步执行
        async def test_visualize():
            result = await tool.execute(data=test_data, chart_type="line")
            if result.startswith("data:image/png;base64,"):
                print("✅ 折线图生成成功！")
                print(f"📏 图片大小：{len(result)} 字符")
                return True
            else:
                print(f"❌ 折线图生成失败：{result}")
                return False
        
        # 运行测试
        success = asyncio.run(test_visualize())
        return success
        
    except ImportError as e:
        print(f"❌ 导入可视化工具失败：{e}")
        return False
    except Exception as e:
        print(f"❌ 可视化工具测试失败：{e}")
        return False

def test_chat_dialog_image_analysis():
    """测试聊天对话框的图像分析功能"""
    print("\n💬 测试聊天对话框图像分析功能...")
    
    try:
        sys.path.insert(0, 'src')
        from ui.pet_chat_dialog import PetChatDialog
        from PyQt6.QtWidgets import QApplication
        import asyncio
        
        # 创建QApplication实例
        app = QApplication([])
        
        # 创建聊天对话框
        dialog = PetChatDialog()
        
        # 测试图像显示功能
        test_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        print("🖼️ 测试图像显示功能...")
        dialog.show_image_from_base64(test_base64)
        print("✅ 图像显示功能正常")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入聊天对话框失败：{e}")
        return False
    except Exception as e:
        print(f"❌ 聊天对话框测试失败：{e}")
        return False

def main():
    """主测试函数"""
    print("🏥 桌宠端图像分析功能测试")
    print("=" * 50)
    
    # 测试结果
    results = []
    
    # 1. 测试Web端API
    results.append(("Web端API", test_image_analysis_api()))
    
    # 2. 测试桌宠代理
    results.append(("桌宠代理", test_pet_agent_image_analysis()))
    
    # 3. 测试可视化工具
    results.append(("可视化工具", test_visualize_tool()))
    
    # 4. 测试聊天对话框
    results.append(("聊天对话框", test_chat_dialog_image_analysis()))
    
    # 输出测试结果
    print("\n📋 测试结果汇总")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:<15} {status}")
        if success:
            passed += 1
    
    print(f"\n📊 总体结果：{passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！桌宠端图像分析功能正常工作。")
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 