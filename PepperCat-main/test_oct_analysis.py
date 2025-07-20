#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCT分析功能测试脚本
测试桌宠的OCT图片分析能力
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agent_manager import AgentManager
from src.tools.oct_analysis import OCTAnalyzer, OCTAnalysisTool

class OCTAnalysisTester:
    """OCT分析测试器"""
    
    def __init__(self):
        self.agent_manager = AgentManager()
        self.test_results = []
        
    async def test_oct_analyzer(self):
        """测试OCT分析器"""
        print("=== 测试OCT分析器 ===")
        
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
                    self.test_results.append({
                        "test": f"OCT分析器 - {image_path}",
                        "status": "FAIL",
                        "error": result['error']
                    })
                else:
                    print("✅ 分析成功!")
                    print(f"检测到异常: {len(result['oct_features']['abnormalities'])}个")
                    
                    # 获取主要疾病
                    disease_analysis = result['disease_analysis']
                    primary_disease = max(disease_analysis.items(), key=lambda x: x[1])
                    print(f"主要疾病: {primary_disease[0]} (置信度: {primary_disease[1]:.1%})")
                    
                    self.test_results.append({
                        "test": f"OCT分析器 - {image_path}",
                        "status": "PASS",
                        "disease": primary_disease[0],
                        "confidence": primary_disease[1]
                    })
            else:
                print(f"❌ 图片不存在: {image_path}")
                self.test_results.append({
                    "test": f"OCT分析器 - {image_path}",
                    "status": "FAIL",
                    "error": "图片文件不存在"
                })
    
    async def test_oct_tool(self):
        """测试OCT分析工具"""
        print("\n=== 测试OCT分析工具 ===")
        
        oct_tool = OCTAnalysisTool()
        
        # 测试图片路径
        test_images = [
            "pictures/glaucoma_classification_1.png",
            "pictures/E.png"
        ]
        
        for image_path in test_images:
            if os.path.exists(image_path):
                print(f"\n使用OCT工具分析: {image_path}")
                result = await oct_tool.execute(image_path)
                
                if "错误" in result or "失败" in result:
                    print(f"❌ 工具执行失败: {result}")
                    self.test_results.append({
                        "test": f"OCT工具 - {image_path}",
                        "status": "FAIL",
                        "error": result
                    })
                else:
                    print("✅ 工具执行成功!")
                    print(f"报告长度: {len(result)} 字符")
                    
                    self.test_results.append({
                        "test": f"OCT工具 - {image_path}",
                        "status": "PASS",
                        "report_length": len(result)
                    })
            else:
                print(f"❌ 图片不存在: {image_path}")
                self.test_results.append({
                    "test": f"OCT工具 - {image_path}",
                    "status": "FAIL",
                    "error": "图片文件不存在"
                })
    
    async def test_agent_integration(self):
        """测试智能体集成"""
        print("\n=== 测试智能体集成 ===")
        
        # 测试命令
        test_commands = [
            "分析我的OCT图片pictures/glaucoma_classification_1.png",
            "读取我的桌面的eyes.png图片，这是一个oct的图片，分析，然后告诉我我生了什么病",
            "帮我分析这张OCT图片pictures/E.png"
        ]
        
        for command in test_commands:
            print(f"\n测试命令: {command}")
            
            try:
                # 解析命令
                plan = self.agent_manager.parse_command(command)
                print(f"解析计划: {plan}")
                
                if plan and len(plan) > 0:
                    # 执行计划
                    results = await self.agent_manager.run_plan(plan)
                    
                    if results and len(results) > 0:
                        print("✅ 命令执行成功!")
                        print(f"结果: {results[0][:200]}...")  # 只显示前200字符
                        
                        self.test_results.append({
                            "test": f"智能体集成 - {command[:30]}...",
                            "status": "PASS",
                            "plan": plan,
                            "result_length": len(str(results))
                        })
                    else:
                        print("❌ 命令执行失败")
                        self.test_results.append({
                            "test": f"智能体集成 - {command[:30]}...",
                            "status": "FAIL",
                            "error": "执行结果为空"
                        })
                else:
                    print("❌ 命令解析失败")
                    self.test_results.append({
                        "test": f"智能体集成 - {command[:30]}...",
                        "status": "FAIL",
                        "error": "解析计划为空"
                    })
                    
            except Exception as e:
                print(f"❌ 测试出错: {e}")
                self.test_results.append({
                    "test": f"智能体集成 - {command[:30]}...",
                    "status": "FAIL",
                    "error": str(e)
                })
    
    async def test_natural_language_commands(self):
        """测试自然语言命令"""
        print("\n=== 测试自然语言命令 ===")
        
        # 模拟用户的各种OCT分析请求
        test_scenarios = [
            {
                "command": "我的眼睛不舒服，帮我分析一下这张OCT图片pictures/glaucoma_classification_1.png",
                "expected_tool": "oct_analysis"
            },
            {
                "command": "医生说我可能有青光眼，请分析这张OCT图片",
                "expected_tool": "oct_analysis"
            },
            {
                "command": "这张OCT图片显示什么疾病？",
                "expected_tool": "oct_analysis"
            }
        ]
        
        for scenario in test_scenarios:
            command = scenario["command"]
            expected_tool = scenario["expected_tool"]
            
            print(f"\n测试场景: {command}")
            
            try:
                # 解析命令
                plan = self.agent_manager.parse_command(command)
                
                if plan and len(plan) > 0:
                    used_tool = plan[0].get("tool", "")
                    
                    if used_tool == expected_tool:
                        print(f"✅ 正确识别工具: {used_tool}")
                        self.test_results.append({
                            "test": f"自然语言识别 - {command[:30]}...",
                            "status": "PASS",
                            "recognized_tool": used_tool
                        })
                    else:
                        print(f"❌ 工具识别错误: 期望 {expected_tool}, 实际 {used_tool}")
                        self.test_results.append({
                            "test": f"自然语言识别 - {command[:30]}...",
                            "status": "FAIL",
                            "expected": expected_tool,
                            "actual": used_tool
                        })
                else:
                    print("❌ 命令解析失败")
                    self.test_results.append({
                        "test": f"自然语言识别 - {command[:30]}...",
                        "status": "FAIL",
                        "error": "解析失败"
                    })
                    
            except Exception as e:
                print(f"❌ 测试出错: {e}")
                self.test_results.append({
                    "test": f"自然语言识别 - {command[:30]}...",
                    "status": "FAIL",
                    "error": str(e)
                })
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 OCT分析功能测试报告")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        print("\n详细结果:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if "error" in result:
                print(f"   错误: {result['error']}")
        
        # 保存报告
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": passed_tests/total_tests*100,
            "results": self.test_results
        }
        
        report_file = "oct_analysis_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        if failed_tests == 0:
            print("\n🎉 所有测试通过！OCT分析功能正常工作")
        else:
            print(f"\n⚠️  有 {failed_tests} 个测试失败，请检查相关功能")

async def main():
    """主测试函数"""
    print("OCT分析功能测试工具")
    print("此工具将测试桌宠的OCT图片分析能力")
    print("🔧 OCT分析功能测试")
    print("="*60)
    
    tester = OCTAnalysisTester()
    
    # 运行所有测试
    await tester.test_oct_analyzer()
    await tester.test_oct_tool()
    await tester.test_agent_integration()
    await tester.test_natural_language_commands()
    
    # 生成报告
    tester.generate_report()

if __name__ == "__main__":
    asyncio.run(main()) 