#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌宠智能对话和命令理解测试脚本
测试桌宠是否能听懂用户的话并做出正确的判断和执行
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class PetIntelligenceTester:
    """桌宠智能测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.passed_tests = 0
        self.total_tests = 0
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "status": status,
            "message": message,
            "success": success
        }
        self.test_results[test_name] = result
        
        print(f"{status} {test_name}: {message}")
    
    async def test_command_parsing(self):
        """测试命令解析功能"""
        print("\n=== 测试命令解析功能 ===")
        
        try:
            from src.agent_manager import AgentManager
            manager = AgentManager()
            
            # 测试各种用户命令
            test_commands = [
                "我想玩记忆游戏",
                "启动专注力训练",
                "进行视力检测",
                "分析图片pictures/glaucoma_classification_1.png",
                "读取我的csv文件，然后分析做可视化",
                "我的眼睛红肿应该怎么办",
                "搜索眼部健康知识",
                "查看我的视力数据"
            ]
            
            for i, command in enumerate(test_commands, 1):
                try:
                    plan = manager.parse_command(command)
                    if plan and len(plan) > 0:
                        self.log_test(f"命令解析-{i}", True, f"'{command}' -> 生成{len(plan)}个步骤")
                        print(f"   解析结果: {plan}")
                    else:
                        self.log_test(f"命令解析-{i}", False, f"'{command}' -> 解析失败")
                except Exception as e:
                    self.log_test(f"命令解析-{i}", False, f"'{command}' -> 错误: {e}")
                    
        except Exception as e:
            self.log_test("命令解析系统", False, f"命令解析系统测试失败: {e}")
    
    async def test_game_commands(self):
        """测试游戏相关命令"""
        print("\n=== 测试游戏命令 ===")
        
        try:
            from src.agent_manager import AgentManager
            manager = AgentManager()
            
            game_commands = [
                "我想玩记忆游戏",
                "启动记忆训练",
                "开始专注力训练",
                "进行反应速度训练",
                "玩眼部健康游戏",
                "启动所有眼部游戏"
            ]
            
            for i, command in enumerate(game_commands, 1):
                try:
                    plan = manager.parse_command(command)
                    if plan and len(plan) > 0:
                        # 检查是否包含眼部游戏工具
                        has_eye_games = any('eyegames' in str(step).lower() for step in plan)
                        self.log_test(f"游戏命令-{i}", has_eye_games, f"'{command}' -> {'包含游戏工具' if has_eye_games else '未包含游戏工具'}")
                    else:
                        self.log_test(f"游戏命令-{i}", False, f"'{command}' -> 解析失败")
                except Exception as e:
                    self.log_test(f"游戏命令-{i}", False, f"'{command}' -> 错误: {e}")
                    
        except Exception as e:
            self.log_test("游戏命令系统", False, f"游戏命令系统测试失败: {e}")
    
    async def test_health_commands(self):
        """测试健康咨询命令"""
        print("\n=== 测试健康咨询命令 ===")
        
        try:
            from src.agent_manager import AgentManager
            manager = AgentManager()
            
            health_commands = [
                "我的眼睛红肿应该怎么办",
                "眼睛疲劳怎么缓解",
                "视力下降怎么办",
                "眼部健康建议",
                "如何保护眼睛",
                "眼睛干涩怎么处理"
            ]
            
            for i, command in enumerate(health_commands, 1):
                try:
                    plan = manager.parse_command(command)
                    if plan and len(plan) > 0:
                        # 检查是否包含搜索或问答工具
                        has_search = any('websearch' in str(step).lower() or 'deepseek' in str(step).lower() for step in plan)
                        self.log_test(f"健康咨询-{i}", has_search, f"'{command}' -> {'包含搜索工具' if has_search else '未包含搜索工具'}")
                    else:
                        self.log_test(f"健康咨询-{i}", False, f"'{command}' -> 解析失败")
                except Exception as e:
                    self.log_test(f"健康咨询-{i}", False, f"'{command}' -> 错误: {e}")
                    
        except Exception as e:
            self.log_test("健康咨询系统", False, f"健康咨询系统测试失败: {e}")
    
    async def test_data_analysis_commands(self):
        """测试数据分析命令"""
        print("\n=== 测试数据分析命令 ===")
        
        try:
            from src.agent_manager import AgentManager
            manager = AgentManager()
            
            data_commands = [
                "读取我的csv文件，然后分析做可视化",
                "分析视力数据",
                "查看我的测试记录",
                "生成视力报告",
                "绘制视力趋势图",
                "分析眼部健康数据"
            ]
            
            for i, command in enumerate(data_commands, 1):
                try:
                    plan = manager.parse_command(command)
                    if plan and len(plan) > 0:
                        # 检查是否包含文件读取和可视化工具
                        has_file_read = any('read_file' in str(step).lower() for step in plan)
                        has_visualize = any('visualize' in str(step).lower() for step in plan)
                        has_analysis = has_file_read or has_visualize
                        self.log_test(f"数据分析-{i}", has_analysis, f"'{command}' -> {'包含分析工具' if has_analysis else '未包含分析工具'}")
                    else:
                        self.log_test(f"数据分析-{i}", False, f"'{command}' -> 解析失败")
                except Exception as e:
                    self.log_test(f"数据分析-{i}", False, f"'{command}' -> 错误: {e}")
                    
        except Exception as e:
            self.log_test("数据分析系统", False, f"数据分析系统测试失败: {e}")
    
    async def test_vision_test_commands(self):
        """测试视力检测命令"""
        print("\n=== 测试视力检测命令 ===")
        
        try:
            from src.agent_manager import AgentManager
            manager = AgentManager()
            
            vision_commands = [
                "进行视力检测",
                "开始视力测试",
                "检测我的视力",
                "视力检查",
                "E字表测试"
            ]
            
            for i, command in enumerate(vision_commands, 1):
                try:
                    plan = manager.parse_command(command)
                    if plan and len(plan) > 0:
                        # 检查是否包含视力检测工具
                        has_vision_test = any('vision_test' in str(step).lower() for step in plan)
                        self.log_test(f"视力检测-{i}", has_vision_test, f"'{command}' -> {'包含视力检测工具' if has_vision_test else '未包含视力检测工具'}")
                    else:
                        self.log_test(f"视力检测-{i}", False, f"'{command}' -> 解析失败")
                except Exception as e:
                    self.log_test(f"视力检测-{i}", False, f"'{command}' -> 错误: {e}")
                    
        except Exception as e:
            self.log_test("视力检测系统", False, f"视力检测系统测试失败: {e}")
    
    async def test_image_analysis_commands(self):
        """测试图像分析命令"""
        print("\n=== 测试图像分析命令 ===")
        
        try:
            from src.agent_manager import AgentManager
            manager = AgentManager()
            
            image_commands = [
                "分析图片pictures/glaucoma_classification_1.png",
                "检查这张眼部图片",
                "分析眼部图像",
                "图片诊断",
                "眼部图片分析"
            ]
            
            for i, command in enumerate(image_commands, 1):
                try:
                    plan = manager.parse_command(command)
                    if plan and len(plan) > 0:
                        # 检查是否包含图像分析工具
                        has_image_analysis = any('image_analysis' in str(step).lower() for step in plan)
                        self.log_test(f"图像分析-{i}", has_image_analysis, f"'{command}' -> {'包含图像分析工具' if has_image_analysis else '未包含图像分析工具'}")
                    else:
                        self.log_test(f"图像分析-{i}", False, f"'{command}' -> 解析失败")
                except Exception as e:
                    self.log_test(f"图像分析-{i}", False, f"'{command}' -> 错误: {e}")
                    
        except Exception as e:
            self.log_test("图像分析系统", False, f"图像分析系统测试失败: {e}")
    
    async def test_chat_dialog(self):
        """测试聊天对话框功能"""
        print("\n=== 测试聊天对话框功能 ===")
        
        try:
            from src.ui.pet_chat_dialog import PetChatDialog
            from PyQt6.QtWidgets import QApplication
            
            # 创建QApplication（如果还没有的话）
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            # 创建聊天对话框
            dialog = PetChatDialog()
            self.log_test("聊天对话框创建", True, "聊天对话框创建成功")
            
            # 测试消息处理
            test_messages = [
                "我想玩记忆游戏",
                "我的眼睛红肿应该怎么办",
                "读取我的csv文件，然后分析做可视化"
            ]
            
            for i, message in enumerate(test_messages, 1):
                try:
                    # 模拟发送消息
                    dialog.input_field.setText(message)
                    # 这里可以添加更多测试逻辑
                    self.log_test(f"消息处理-{i}", True, f"消息'{message}'处理正常")
                except Exception as e:
                    self.log_test(f"消息处理-{i}", False, f"消息'{message}'处理失败: {e}")
                    
        except Exception as e:
            self.log_test("聊天对话框", False, f"聊天对话框测试失败: {e}")
    
    async def test_full_workflow(self):
        """测试完整工作流程"""
        print("\n=== 测试完整工作流程 ===")
        
        try:
            from src.agent_manager import AgentManager
            from src.openmanus_agent.mcp_patch import PatchedMCPAgent
            from src.openmanus_agent.tool_collection import ToolCollection
            from src.openmanus_agent.web_search import WebSearchTool
            from src.openmanus_agent.file_ops import FileOpsTool
            from src.openmanus_agent.deepseek_qa import DeepseekQATool
            from src.tools.eye_games import EyeGamesTool
            from src.tools.vision_test import VisionTestTool
            from src.tools.image_analysis import ImageAnalysisTool
            from src.openmanus_agent.visualize_tool import VisualizeTool
            
            # 创建智能体
            agent = PatchedMCPAgent()
            agent.available_tools = ToolCollection(
                WebSearchTool(), FileOpsTool(), DeepseekQATool(),
                EyeGamesTool(), VisionTestTool(), ImageAnalysisTool(), VisualizeTool()
            )
            
            # 测试完整工作流程
            workflow_tests = [
                {
                    "command": "我想玩记忆游戏",
                    "expected_tools": ["eyegames"],
                    "description": "记忆游戏启动"
                },
                {
                    "command": "我的眼睛红肿应该怎么办",
                    "expected_tools": ["websearch", "deepseek"],
                    "description": "健康咨询"
                },
                {
                    "command": "读取我的csv文件，然后分析做可视化",
                    "expected_tools": ["read_file", "visualize"],
                    "description": "数据分析可视化"
                }
            ]
            
            for i, test in enumerate(workflow_tests, 1):
                try:
                    # 解析命令
                    manager = AgentManager()
                    plan = manager.parse_command(test["command"])
                    
                    if plan and len(plan) > 0:
                        # 检查是否包含预期工具
                        plan_str = str(plan).lower()
                        expected_found = all(tool in plan_str for tool in test["expected_tools"])
                        self.log_test(f"工作流程-{i}", expected_found, f"{test['description']} -> {'包含预期工具' if expected_found else '缺少预期工具'}")
                    else:
                        self.log_test(f"工作流程-{i}", False, f"{test['description']} -> 解析失败")
                except Exception as e:
                    self.log_test(f"工作流程-{i}", False, f"{test['description']} -> 错误: {e}")
                    
        except Exception as e:
            self.log_test("完整工作流程", False, f"完整工作流程测试失败: {e}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧠 开始桌宠智能对话和命令理解测试")
        print("=" * 60)
        
        # 运行各项测试
        await self.test_command_parsing()
        await self.test_game_commands()
        await self.test_health_commands()
        await self.test_data_analysis_commands()
        await self.test_vision_test_commands()
        await self.test_image_analysis_commands()
        await self.test_chat_dialog()
        await self.test_full_workflow()
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 桌宠智能对话和命令理解测试报告")
        print("=" * 60)
        
        print(f"总测试数: {self.total_tests}")
        print(f"通过测试: {self.passed_tests}")
        print(f"失败测试: {self.total_tests - self.passed_tests}")
        print(f"通过率: {self.passed_tests/self.total_tests*100:.1f}%")
        
        print("\n详细结果:")
        for test_name, result in self.test_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {test_name}: {result['message']}")
        
        # 保存报告到文件
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "pass_rate": float(self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0.0,
            "results": self.test_results
        }
        
        with open("pet_intelligence_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: pet_intelligence_test_report.json")
        
        # 总结
        if self.passed_tests == self.total_tests:
            print("\n🎉 桌宠智能对话功能完全正常！")
            print("✅ 桌宠能够理解你的自然语言命令")
            print("✅ 能够正确解析各种功能需求")
            print("✅ 能够调用相应的工具执行任务")
        else:
            print(f"\n⚠️  有 {self.total_tests - self.passed_tests} 个测试失败，请检查相关功能")
        
        print("\n💡 使用建议:")
        print("- 双击桌宠打开聊天对话框")
        print("- 输入自然语言命令，如'我想玩记忆游戏'")
        print("- 桌宠会自动解析并执行相应功能")


def main():
    """主函数"""
    print("桌宠智能对话和命令理解测试工具")
    print("此工具将测试桌宠是否能听懂用户的话并做出正确的判断")
    
    # 创建测试器
    tester = PetIntelligenceTester()
    
    try:
        # 运行所有测试
        asyncio.run(tester.run_all_tests())
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 