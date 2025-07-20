#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的OCT分析测试
"""

import os
import sys

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_oct_analyzer():
    """测试OCT分析器"""
    print("=== 测试OCT分析器 ===")
    
    try:
        from src.tools.oct_analysis import OCTAnalyzer
        
        analyzer = OCTAnalyzer()
        
        # 测试图片路径
        test_images = [
            "pictures/glaucoma_classification_1.png",
            "pictures/E.png"
        ]
        
        for image_path in test_images:
            if os.path.exists(image_path):
                print(f"\n分析OCT图片: {image_path}")
                result = analyzer.analyze_oct_image(image_path)
                
                if "error" in result:
                    print(f"❌ 错误: {result['error']}")
                else:
                    print("✅ 分析成功!")
                    print(f"检测到异常: {len(result['oct_features']['abnormalities'])}个")
                    
                    # 获取主要疾病
                    disease_analysis = result['disease_analysis']
                    primary_disease = max(disease_analysis.items(), key=lambda x: x[1])
                    print(f"主要疾病: {primary_disease[0]} (置信度: {primary_disease[1]:.1%})")
                    
                    # 显示报告摘要
                    report = result['report']
                    print(f"报告长度: {len(report)} 字符")
                    print("报告摘要:")
                    lines = report.split('\n')[:10]  # 只显示前10行
                    for line in lines:
                        print(f"  {line}")
            else:
                print(f"❌ 图片不存在: {image_path}")
                
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

def test_oct_tool():
    """测试OCT分析工具"""
    print("\n=== 测试OCT分析工具 ===")
    
    try:
        from src.tools.oct_analysis import OCTAnalysisTool
        
        oct_tool = OCTAnalysisTool()
        
        # 测试图片路径
        test_images = [
            "pictures/glaucoma_classification_1.png",
            "pictures/E.png"
        ]
        
        for image_path in test_images:
            if os.path.exists(image_path):
                print(f"\n使用OCT工具分析: {image_path}")
                
                # 同步执行
                import asyncio
                result = asyncio.run(oct_tool.execute(image_path))
                
                if "错误" in result or "失败" in result:
                    print(f"❌ 工具执行失败: {result}")
                else:
                    print("✅ 工具执行成功!")
                    print(f"报告长度: {len(result)} 字符")
                    print("报告摘要:")
                    lines = result.split('\n')[:10]  # 只显示前10行
                    for line in lines:
                        print(f"  {line}")
            else:
                print(f"❌ 图片不存在: {image_path}")
                
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

def test_agent_manager():
    """测试智能体管理器"""
    print("\n=== 测试智能体管理器 ===")
    
    try:
        from src.agent_manager import AgentManager
        
        agent_manager = AgentManager()
        
        # 测试命令
        test_commands = [
            "分析我的OCT图片pictures/glaucoma_classification_1.png",
            "读取我的桌面的eyes.png图片，这是一个oct的图片，分析，然后告诉我我生了什么病"
        ]
        
        for command in test_commands:
            print(f"\n测试命令: {command}")
            
            # 解析命令
            plan = agent_manager.parse_command(command)
            print(f"解析计划: {plan}")
            
            if plan and len(plan) > 0:
                print(f"✅ 命令解析成功，使用工具: {plan[0].get('tool', 'unknown')}")
            else:
                print("❌ 命令解析失败")
                
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("简化的OCT分析测试")
    print("="*50)
    
    test_oct_analyzer()
    test_oct_tool()
    test_agent_manager()
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 