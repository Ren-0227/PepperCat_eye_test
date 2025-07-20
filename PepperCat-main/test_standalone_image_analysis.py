#!/usr/bin/env python3
"""
独立图像分析功能测试脚本
不依赖Web端，直接进行图片检测
"""

import os
import sys
import asyncio

def test_standalone_image_analysis():
    """测试独立的图像分析功能"""
    print("🔍 测试独立图像分析功能...")
    
    try:
        # 导入图像分析工具
        sys.path.insert(0, 'src')
        from tools.image_analysis import ImageAnalysisTool
        
        # 创建工具实例
        tool = ImageAnalysisTool()
        
        # 测试图片路径
        test_image_path = "../pictures/glaucoma_classification_1.png"
        if not os.path.exists(test_image_path):
            print(f"❌ 测试图片不存在：{test_image_path}")
            return False
        
        print(f"📸 使用测试图片：{test_image_path}")
        
        # 异步执行图像分析
        async def run_analysis():
            result = await tool.execute(test_image_path, generate_report=True)
            return result
        
        # 运行分析
        result = asyncio.run(run_analysis())
        print(f"✅ 图像分析成功！")
        print(f"📊 分析结果：\n{result}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入图像分析工具失败：{e}")
        return False
    except Exception as e:
        print(f"❌ 图像分析失败：{e}")
        return False

def test_detailed_analysis():
    """测试详细分析功能"""
    print("\n📋 测试详细分析功能...")
    
    try:
        sys.path.insert(0, 'src')
        from tools.image_analysis import ImageAnalysisTool
        
        tool = ImageAnalysisTool()
        test_image_path = "../pictures/glaucoma_classification_1.png"
        
        if not os.path.exists(test_image_path):
            print(f"❌ 测试图片不存在：{test_image_path}")
            return False
        
        # 获取详细分析结果
        detailed_result = tool.get_detailed_analysis(test_image_path)
        
        if detailed_result["success"]:
            print("✅ 详细分析成功！")
            print(f"📊 检测结果：{detailed_result['result']}")
            print(f"🎯 置信度：{detailed_result['confidence']:.2%}")
            print(f"📈 所有概率：")
            for disease, prob in detailed_result['all_probabilities'].items():
                print(f"  - {disease}: {prob:.2%}")
            print(f"📋 健康报告：\n{detailed_result['report']}")
            return True
        else:
            print(f"❌ 详细分析失败：{detailed_result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ 详细分析测试失败：{e}")
        return False

def test_chat_integration():
    """测试聊天集成功能"""
    print("\n💬 测试聊天集成功能...")
    
    try:
        sys.path.insert(0, 'src')
        from ui.pet_chat_dialog import PetChatDialog
        from PyQt6.QtWidgets import QApplication
        
        # 创建QApplication实例
        app = QApplication([])
        
        # 创建聊天对话框
        dialog = PetChatDialog()
        
        # 模拟图像分析请求
        test_message = "分析图片pictures/glaucoma_classification_1.png"
        print(f"💬 模拟用户消息：{test_message}")
        
        # 测试解析功能
        steps = dialog.parse_plan("[step1]-image_analysis: pictures/glaucoma_classification_1.png")
        
        if steps and len(steps) > 0:
            step = steps[0]
            if step['tool'] == 'image_analysis' and step['args']['image_path'] == 'pictures/glaucoma_classification_1.png':
                print("✅ 聊天集成解析正常！")
                return True
            else:
                print(f"❌ 解析结果异常：{step}")
                return False
        else:
            print("❌ 解析失败，未得到步骤")
            return False
            
    except Exception as e:
        print(f"❌ 聊天集成测试失败：{e}")
        return False

def test_convenience_function():
    """测试便捷函数"""
    print("\n⚡ 测试便捷函数...")
    
    try:
        sys.path.insert(0, 'src')
        from tools.image_analysis import analyze_image_direct
        
        test_image_path = "../pictures/glaucoma_classification_1.png"
        
        if not os.path.exists(test_image_path):
            print(f"❌ 测试图片不存在：{test_image_path}")
            return False
        
        # 使用便捷函数
        result = analyze_image_direct(test_image_path, generate_report=True)
        
        if result and "图片分析完成" in result:
            print("✅ 便捷函数测试成功！")
            print(f"📊 结果：{result[:200]}...")
            return True
        else:
            print(f"❌ 便捷函数测试失败：{result}")
            return False
            
    except Exception as e:
        print(f"❌ 便捷函数测试失败：{e}")
        return False

def main():
    """主测试函数"""
    print("🏥 独立图像分析功能测试")
    print("=" * 50)
    
    # 测试结果
    results = []
    
    # 1. 测试独立图像分析
    results.append(("独立图像分析", test_standalone_image_analysis()))
    
    # 2. 测试详细分析
    results.append(("详细分析功能", test_detailed_analysis()))
    
    # 3. 测试聊天集成
    results.append(("聊天集成", test_chat_integration()))
    
    # 4. 测试便捷函数
    results.append(("便捷函数", test_convenience_function()))
    
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
        print("🎉 所有测试通过！独立图像分析功能正常工作。")
        print("\n💡 使用说明：")
        print("1. 在桌宠聊天中直接说：'分析图片pictures/glaucoma_classification_1.png'")
        print("2. 桌宠会自动调用图像分析工具进行检测")
        print("3. 然后使用DeepSeek生成详细的健康报告")
        print("4. 无需启动Web端，完全独立运行！")
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 