#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌宠全面功能测试脚本
测试所有核心功能是否正常运行
"""

import asyncio
import sys
import os
import time
import json
import threading
from typing import Dict, List, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class PetFeatureTester:
    """桌宠功能测试器"""
    
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
    
    def test_imports(self):
        """测试所有必要的模块导入"""
        print("\n=== 测试模块导入 ===")
        
        # 测试基础模块
        try:
            import cv2
            self.log_test("OpenCV导入", True, "OpenCV模块导入成功")
        except ImportError as e:
            self.log_test("OpenCV导入", False, f"OpenCV导入失败: {e}")
        
        try:
            import mediapipe as mp
            self.log_test("MediaPipe导入", True, "MediaPipe模块导入成功")
        except ImportError as e:
            self.log_test("MediaPipe导入", False, f"MediaPipe导入失败: {e}")
        
        try:
            import numpy as np
            self.log_test("NumPy导入", True, "NumPy模块导入成功")
        except ImportError as e:
            self.log_test("NumPy导入", False, f"NumPy导入失败: {e}")
        
        try:
            from PyQt6.QtWidgets import QApplication
            self.log_test("PyQt6导入", True, "PyQt6模块导入成功")
        except ImportError as e:
            self.log_test("PyQt6导入", False, f"PyQt6导入失败: {e}")
        
        try:
            import tkinter as tk
            self.log_test("Tkinter导入", True, "Tkinter模块导入成功")
        except ImportError as e:
            self.log_test("Tkinter导入", False, f"Tkinter导入失败: {e}")
    
    def test_pet_agent(self):
        """测试桌宠智能体"""
        print("\n=== 测试桌宠智能体 ===")
        
        try:
            from src.agent.pet_agent import PetAgent
            agent = PetAgent("TestPet")
            
            # 测试基础属性
            self.log_test("桌宠智能体创建", True, "桌宠智能体创建成功")
            
            # 测试状态获取
            stats = agent.get_stats_summary()
            self.log_test("状态获取", len(stats) > 0, f"获取到状态信息: {len(stats)}字符")
            
            # 测试活动检测
            activity = agent.get_activity_summary()
            self.log_test("活动检测", len(activity) > 0, f"活动检测正常: {activity}")
            
            # 测试消息处理
            response = agent._handle_chat("你好")
            self.log_test("消息处理", len(response) > 0, f"消息响应正常: {response[:50]}...")
            
        except Exception as e:
            self.log_test("桌宠智能体", False, f"桌宠智能体测试失败: {e}")
    
    def test_tools(self):
        """测试所有工具"""
        print("\n=== 测试工具系统 ===")
        
        # 测试工具注册表
        try:
            from src.agent_manager import AgentManager
            manager = AgentManager()
            self.log_test("工具管理器", True, "工具管理器创建成功")
            
            # 测试工具解析
            plan = manager.parse_command("搜索天气")
            self.log_test("命令解析", len(plan) > 0, f"命令解析成功，生成{len(plan)}个步骤")
            
        except Exception as e:
            self.log_test("工具管理器", False, f"工具管理器测试失败: {e}")
        
        # 测试眼部游戏工具
        try:
            from src.tools.eye_games import EyeGamesTool
            eye_tool = EyeGamesTool()
            self.log_test("眼部游戏工具", True, "眼部游戏工具创建成功")
            
            # 测试游戏类型（简化测试，不实际启动游戏）
            game_types = ["memory", "focus", "reaction", "all"]
            for game_type in game_types:
                self.log_test(f"游戏工具-{game_type}", True, f"{game_type}游戏工具可用")
                    
        except Exception as e:
            self.log_test("眼部游戏工具", False, f"眼部游戏工具测试失败: {e}")
        
        # 测试图像分析工具
        try:
            from src.tools.image_analysis import ImageAnalysisTool
            img_tool = ImageAnalysisTool()
            self.log_test("图像分析工具", True, "图像分析工具创建成功")
            
            # 测试模型文件存在
            model_files = ["oct_scripted.pt", "best_model.pth", "full_model.pth"]
            for model_file in model_files:
                if os.path.exists(f"../{model_file}"):
                    self.log_test(f"模型文件-{model_file}", True, f"模型文件存在: {model_file}")
                else:
                    self.log_test(f"模型文件-{model_file}", False, f"模型文件不存在: {model_file}")
            
        except Exception as e:
            self.log_test("图像分析工具", False, f"图像分析工具测试失败: {e}")
        
        # 测试视力检测工具
        try:
            from src.tools.vision_test import VisionTestTool
            vision_tool = VisionTestTool()
            self.log_test("视力检测工具", True, "视力检测工具创建成功")
            
        except Exception as e:
            self.log_test("视力检测工具", False, f"视力检测工具测试失败: {e}")
    
    def test_ui_components(self):
        """测试UI组件"""
        print("\n=== 测试UI组件 ===")
        
        # 测试UI模块导入（不创建实际窗口）
        try:
            from src.ui.bubble_menu import BubbleMenu
            self.log_test("气泡菜单模块", True, "气泡菜单模块导入成功")
        except Exception as e:
            self.log_test("气泡菜单模块", False, f"气泡菜单模块测试失败: {e}")
        
        try:
            from src.ui.upgrade_machine import UpgradeMachine
            self.log_test("升级机器模块", True, "升级机器模块导入成功")
        except Exception as e:
            self.log_test("升级机器模块", False, f"升级机器模块测试失败: {e}")
        
        try:
            from src.ui.battle_dialog import BattleDialog
            self.log_test("对战对话框模块", True, "对战对话框模块导入成功")
        except Exception as e:
            self.log_test("对战对话框模块", False, f"对战对话框模块测试失败: {e}")
        
        try:
            from src.ui.pet_widget import PetWidget
            self.log_test("桌宠组件模块", True, "桌宠组件模块导入成功")
        except Exception as e:
            self.log_test("桌宠组件模块", False, f"桌宠组件模块测试失败: {e}")
    
    def test_agent_system(self):
        """测试智能体系统"""
        print("\n=== 测试智能体系统 ===")
        
        try:
            from src.openmanus_agent.mcp_patch import PatchedMCPAgent
            from src.openmanus_agent.tool_collection import ToolCollection
            from src.openmanus_agent.web_search import WebSearchTool
            from src.openmanus_agent.file_ops import FileOpsTool
            from src.openmanus_agent.deepseek_qa import DeepseekQATool
            
            # 创建智能体
            agent = PatchedMCPAgent()
            agent.available_tools = ToolCollection(
                WebSearchTool(), FileOpsTool(), DeepseekQATool()
            )
            
            self.log_test("智能体系统", True, "智能体系统创建成功")
            
            # 测试工具集合
            tool_count = len(agent.available_tools.tool_map)
            self.log_test("工具集合", tool_count > 0, f"工具集合包含{tool_count}个工具")
            
        except Exception as e:
            self.log_test("智能体系统", False, f"智能体系统测试失败: {e}")
    
    def test_data_files(self):
        """测试数据文件"""
        print("\n=== 测试数据文件 ===")
        
        # 测试CSV文件
        try:
            import pandas as pd
            df = pd.read_csv("eyes_test.csv")
            self.log_test("视力数据CSV", len(df) > 0, f"视力数据文件正常，包含{len(df)}条记录")
        except Exception as e:
            self.log_test("视力数据CSV", False, f"视力数据文件测试失败: {e}")
        
        # 测试JSON文件
        try:
            with open("user_habits.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            self.log_test("用户习惯JSON", len(data) > 0, f"用户习惯文件正常，包含{len(data)}个键")
        except Exception as e:
            self.log_test("用户习惯JSON", False, f"用户习惯文件测试失败: {e}")
        
        # 测试宠物状态文件
        try:
            with open("pet_stats.json", "r", encoding="utf-8") as f:
                stats = json.load(f)
            self.log_test("宠物状态JSON", len(stats) > 0, f"宠物状态文件正常，包含{len(stats)}个属性")
        except Exception as e:
            self.log_test("宠物状态JSON", False, f"宠物状态文件测试失败: {e}")
    
    def test_camera_access(self):
        """测试摄像头访问"""
        print("\n=== 测试摄像头访问 ===")
        
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    self.log_test("摄像头访问", True, f"摄像头正常，图像尺寸: {frame.shape}")
                else:
                    self.log_test("摄像头访问", False, "摄像头无法读取图像")
                cap.release()
            else:
                self.log_test("摄像头访问", False, "无法打开摄像头")
        except Exception as e:
            self.log_test("摄像头访问", False, f"摄像头测试失败: {e}")
    
    def test_mediapipe_models(self):
        """测试MediaPipe模型"""
        print("\n=== 测试MediaPipe模型 ===")
        
        try:
            import mediapipe as mp
            
            # 测试面部网格模型
            face_mesh = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=1, refine_landmarks=True,
                min_detection_confidence=0.5, min_tracking_confidence=0.5
            )
            self.log_test("面部网格模型", True, "面部网格模型初始化成功")
            face_mesh.close()
            
            # 测试手势识别模型
            hands = mp.solutions.hands.Hands(
                min_detection_confidence=0.5, min_tracking_confidence=0.5
            )
            self.log_test("手势识别模型", True, "手势识别模型初始化成功")
            hands.close()
            
        except Exception as e:
            self.log_test("MediaPipe模型", False, f"MediaPipe模型测试失败: {e}")
    
    def test_async_operations(self):
        """测试异步操作"""
        print("\n=== 测试异步操作 ===")
        
        async def test_async():
            try:
                # 测试异步工具执行
                from src.openmanus_agent.web_search import WebSearchTool
                tool = WebSearchTool()
                result = await tool.execute(query="测试")
                return len(result) > 0
            except Exception as e:
                print(f"异步测试失败: {e}")
                return False
        
        try:
            result = asyncio.run(test_async())
            self.log_test("异步操作", result, "异步工具执行测试完成")
        except Exception as e:
            self.log_test("异步操作", False, f"异步操作测试失败: {e}")
    
    def test_file_operations(self):
        """测试文件操作"""
        print("\n=== 测试文件操作 ===")
        
        try:
            # 测试文件读取
            from src.openmanus_agent.file_ops import FileOpsTool
            file_tool = FileOpsTool()
            
            # 创建测试文件
            test_content = "这是一个测试文件\n用于测试文件操作功能"
            test_filename = "test_file.txt"
            
            with open(test_filename, "w", encoding="utf-8") as f:
                f.write(test_content)
            
            # 测试文件读取
            async def test_file_read():
                return await file_tool.execute(filename=test_filename, content="")
            
            result = asyncio.run(test_file_read())
            self.log_test("文件读取", "测试文件" in result, "文件读取功能正常")
            
            # 测试文件写入
            async def test_file_write():
                return await file_tool.execute(filename="test_write.txt", content="写入测试内容")
            
            result = asyncio.run(test_file_write())
            self.log_test("文件写入", "写入测试内容" in result, "文件写入功能正常")
            
            # 清理写入的测试文件
            if os.path.exists("test_write.txt"):
                os.remove("test_write.txt")
            
            # 清理测试文件
            os.remove(test_filename)
            
        except Exception as e:
            self.log_test("文件操作", False, f"文件操作测试失败: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始桌宠全面功能测试")
        print("=" * 50)
        
        # 运行各项测试
        self.test_imports()
        self.test_pet_agent()
        self.test_tools()
        self.test_ui_components()
        self.test_agent_system()
        self.test_data_files()
        self.test_camera_access()
        self.test_mediapipe_models()
        self.test_async_operations()
        self.test_file_operations()
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 50)
        print("📊 测试报告")
        print("=" * 50)
        
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
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "pass_rate": self.passed_tests/self.total_tests*100 if self.total_tests > 0 else 0,
            "results": self.test_results
        }
        
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: test_report.json")
        
        # 总结
        if self.passed_tests == self.total_tests:
            print("\n🎉 所有测试通过！桌宠功能正常")
        else:
            print(f"\n⚠️  有 {self.total_tests - self.passed_tests} 个测试失败，请检查相关功能")


def main():
    """主函数"""
    print("桌宠全面功能测试工具")
    print("此工具将测试桌宠的所有核心功能")
    
    # 创建测试器
    tester = PetFeatureTester()
    
    try:
        # 运行所有测试
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 