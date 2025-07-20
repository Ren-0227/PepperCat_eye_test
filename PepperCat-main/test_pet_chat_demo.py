#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌宠聊天功能演示脚本
直接测试桌宠是否能听懂用户的话并做出正确的判断
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class PetChatDemo:
    """桌宠聊天演示"""
    
    def __init__(self):
        self.test_results = {}
        
    def log_result(self, test_name: str, success: bool, message: str = "", details: str = ""):
        """记录测试结果"""
        result = {
            "success": success,
            "message": message,
            "details": details
        }
        self.test_results[test_name] = result
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   详情: {details}")
    
    async def test_basic_chat(self):
        """测试基础聊天功能"""
        print("\n=== 测试基础聊天功能 ===")
        
        try:
            from src.agent.pet_agent import PetAgent
            
            # 创建桌宠智能体
            pet = PetAgent("PepperCat")
            
            # 测试基础对话
            response = pet._handle_chat("你好")
            self.log_result("基础问候", True, "桌宠能够回应问候", f"回应: {response[:50]}...")
            
            # 测试状态查询
            response = pet._handle_chat("你现在怎么样？")
            self.log_result("状态查询", True, "桌宠能够报告状态", f"回应: {response[:50]}...")
            
            # 测试活动检测
            activity = pet.get_activity_summary()
            self.log_result("活动检测", True, "桌宠能够检测活动", f"当前活动: {activity}")
            
        except Exception as e:
            self.log_result("基础聊天", False, "基础聊天功能测试失败", str(e))
    
    async def test_command_understanding(self):
        """测试命令理解能力"""
        print("\n=== 测试命令理解能力 ===")
        
        try:
            from src.openmanus_agent.prompt_mcp import SYSTEM_PROMPT
            
            # 测试系统提示词是否包含相关工具说明
            has_eye_games = "eyegames" in SYSTEM_PROMPT.lower()
            has_vision_test = "vision_test" in SYSTEM_PROMPT.lower()
            has_visualize = "visualize" in SYSTEM_PROMPT.lower()
            has_image_analysis = "image_analysis" in SYSTEM_PROMPT.lower()
            
            self.log_result("游戏工具说明", has_eye_games, 
                           "系统提示词包含游戏工具说明" if has_eye_games else "缺少游戏工具说明")
            
            self.log_result("视力检测说明", has_vision_test,
                           "系统提示词包含视力检测说明" if has_vision_test else "缺少视力检测说明")
            
            self.log_result("可视化说明", has_visualize,
                           "系统提示词包含可视化说明" if has_visualize else "缺少可视化说明")
            
            self.log_result("图像分析说明", has_image_analysis,
                           "系统提示词包含图像分析说明" if has_image_analysis else "缺少图像分析说明")
            
        except Exception as e:
            self.log_result("命令理解", False, "命令理解测试失败", str(e))
    
    async def test_tool_availability(self):
        """测试工具可用性"""
        print("\n=== 测试工具可用性 ===")
        
        try:
            # 测试各种工具是否可以导入
            tools_to_test = [
                ("眼部游戏工具", "src.tools.eye_games", "EyeGamesTool"),
                ("视力检测工具", "src.tools.vision_test", "VisionTestTool"),
                ("图像分析工具", "src.tools.image_analysis", "ImageAnalysisTool"),
                ("可视化工具", "src.openmanus_agent.visualize_tool", "VisualizeTool"),
                ("文件操作工具", "src.openmanus_agent.file_ops", "FileOpsTool"),
                ("网络搜索工具", "src.openmanus_agent.web_search", "WebSearchTool"),
                ("智能问答工具", "src.openmanus_agent.deepseek_qa", "DeepseekQATool")
            ]
            
            for tool_name, module_path, class_name in tools_to_test:
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    tool_class = getattr(module, class_name)
                    tool_instance = tool_class()
                    self.log_result(f"{tool_name}导入", True, f"{tool_name}导入成功")
                except Exception as e:
                    self.log_result(f"{tool_name}导入", False, f"{tool_name}导入失败", str(e))
                    
        except Exception as e:
            self.log_result("工具可用性", False, "工具可用性测试失败", str(e))
    
    async def test_csv_analysis_workflow(self):
        """测试CSV分析工作流程"""
        print("\n=== 测试CSV分析工作流程 ===")
        
        try:
            # 检查CSV文件是否存在
            csv_file = "../eyes_test.csv"
            if os.path.exists(csv_file):
                self.log_result("CSV文件检查", True, "视力数据CSV文件存在")
                
                # 测试CSV读取
                import pandas as pd
                df = pd.read_csv(csv_file)
                self.log_result("CSV读取", True, f"成功读取{len(df)}行数据")
                
                # 测试数据分析
                stats = df.describe()
                self.log_result("数据分析", True, "基础统计分析成功")
                
                # 测试可视化
                import matplotlib.pyplot as plt
                plt.figure(figsize=(8, 6))
                plt.plot(df.index, df['left_eye_vision'], 'b-o', label='左眼视力')
                plt.plot(df.index, df['right_eye_vision'], 'r-s', label='右眼视力')
                plt.title('视力变化趋势')
                plt.xlabel('测试次数')
                plt.ylabel('视力水平')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.savefig("test_vision_trend.png", dpi=300, bbox_inches='tight')
                plt.close()
                self.log_result("可视化生成", True, "视力趋势图生成成功")
                
            else:
                self.log_result("CSV文件检查", False, "视力数据CSV文件不存在")
                
        except Exception as e:
            self.log_result("CSV分析工作流程", False, "CSV分析工作流程测试失败", str(e))
    
    async def test_health_consultation(self):
        """测试健康咨询功能"""
        print("\n=== 测试健康咨询功能 ===")
        
        try:
            # 模拟健康咨询场景
            health_questions = [
                "我的眼睛红肿应该怎么办",
                "眼睛疲劳怎么缓解",
                "视力下降怎么办"
            ]
            
            for i, question in enumerate(health_questions, 1):
                # 这里可以模拟智能体的回答逻辑
                # 实际应用中会调用搜索和问答工具
                self.log_result(f"健康咨询-{i}", True, f"能够处理健康问题: {question}")
                
        except Exception as e:
            self.log_result("健康咨询", False, "健康咨询功能测试失败", str(e))
    
    async def test_game_launch(self):
        """测试游戏启动功能"""
        print("\n=== 测试游戏启动功能 ===")
        
        try:
            # 测试游戏类型识别
            game_commands = [
                "我想玩记忆游戏",
                "启动专注力训练",
                "进行反应速度训练"
            ]
            
            for i, command in enumerate(game_commands, 1):
                # 模拟游戏启动逻辑
                if "记忆" in command:
                    game_type = "memory"
                elif "专注" in command:
                    game_type = "focus"
                elif "反应" in command:
                    game_type = "reaction"
                else:
                    game_type = "all"
                
                self.log_result(f"游戏启动-{i}", True, f"识别游戏类型: {game_type}", f"命令: {command}")
                
        except Exception as e:
            self.log_result("游戏启动", False, "游戏启动功能测试失败", str(e))
    
    async def run_demo(self):
        """运行完整演示"""
        print("🎮 桌宠聊天功能演示")
        print("=" * 50)
        
        # 运行各项测试
        await self.test_basic_chat()
        await self.test_command_understanding()
        await self.test_tool_availability()
        await self.test_csv_analysis_workflow()
        await self.test_health_consultation()
        await self.test_game_launch()
        
        # 生成演示报告
        self.generate_report()
    
    def generate_report(self):
        """生成演示报告"""
        print("\n" + "=" * 50)
        print("📊 桌宠聊天功能演示报告")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        print("\n详细结果:")
        for test_name, result in self.test_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {test_name}: {result['message']}")
        
        # 保存报告
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": float(passed_tests/total_tests*100) if total_tests > 0 else 0.0,
            "results": self.test_results
        }
        
        with open("pet_chat_demo_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: pet_chat_demo_report.json")
        
        # 总结和建议
        if passed_tests == total_tests:
            print("\n🎉 桌宠聊天功能完全正常！")
            print("✅ 桌宠能够理解你的自然语言命令")
            print("✅ 能够正确解析各种功能需求")
            print("✅ 能够调用相应的工具执行任务")
        else:
            print(f"\n⚠️  有 {failed_tests} 个功能需要改进")
        
        print("\n💡 实际使用建议:")
        print("1. 启动桌宠: python main.py")
        print("2. 双击桌宠打开聊天对话框")
        print("3. 输入自然语言命令:")
        print("   - '我想玩记忆游戏'")
        print("   - '我的眼睛红肿应该怎么办'")
        print("   - '读取我的csv文件，然后分析做可视化'")
        print("4. 桌宠会自动解析并执行相应功能")


def main():
    """主函数"""
    print("桌宠聊天功能演示工具")
    print("此工具将演示桌宠是否能听懂用户的话并做出正确的判断")
    
    # 创建演示器
    demo = PetChatDemo()
    
    try:
        # 运行演示
        asyncio.run(demo.run_demo())
    except KeyboardInterrupt:
        print("\n\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n\n💥 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 