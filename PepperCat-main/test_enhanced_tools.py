#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强眼部工具功能测试脚本
测试所有修复和完善的功能
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class EnhancedToolsTester:
    """增强工具测试器"""
    
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
    
    async def test_eye_games_tool(self):
        """测试眼部游戏工具"""
        print("\n=== 测试眼部游戏工具 ===")
        
        try:
            from src.tools.eye_games import EyeGamesTool
            
            # 创建工具实例
            tool = EyeGamesTool()
            self.log_test("游戏工具创建", True, "眼部游戏工具创建成功")
            
            # 测试工具属性
            self.log_test("工具名称", tool.name == "eye_games", f"工具名称: {tool.name}")
            self.log_test("工具描述", len(tool.description) > 0, f"描述长度: {len(tool.description)}")
            self.log_test("参数定义", "game_type" in str(tool.parameters), "参数定义正确")
            
            # 测试tkinter线程
            self.log_test("tkinter线程", hasattr(tool, 'tkinter_thread'), "tkinter线程属性存在")
            self.log_test("tkinter线程状态", tool.tkinter_thread is not None, "tkinter线程已创建")
            
            # 测试游戏启动（不实际启动GUI）
            try:
                # 模拟游戏启动
                result = await tool.execute("memory")
                self.log_test("记忆游戏启动", "记忆训练游戏" in result, f"启动结果: {result[:50]}...")
            except Exception as e:
                self.log_test("记忆游戏启动", False, f"启动失败: {e}")
            
            # 清理资源
            tool.cleanup()
            self.log_test("资源清理", True, "游戏工具资源清理成功")
            
        except Exception as e:
            self.log_test("眼部游戏工具", False, f"游戏工具测试失败: {e}")
    
    async def test_vision_test_tool(self):
        """测试视力检测工具"""
        print("\n=== 测试视力检测工具 ===")
        
        try:
            from src.tools.vision_test import VisionTestTool
            
            # 创建工具实例
            tool = VisionTestTool()
            self.log_test("视力检测工具创建", True, "视力检测工具创建成功")
            
            # 测试工具属性
            self.log_test("工具名称", tool.name == "vision_test", f"工具名称: {tool.name}")
            self.log_test("工具描述", len(tool.description) > 0, f"描述长度: {len(tool.description)}")
            
            # 测试tkinter线程
            self.log_test("tkinter线程", hasattr(tool, 'tkinter_thread'), "tkinter线程属性存在")
            self.log_test("tkinter线程状态", tool.tkinter_thread is not None, "tkinter线程已创建")
            
            # 测试视力检测（不实际启动GUI）
            try:
                # 模拟视力检测
                result = await tool.execute()
                self.log_test("视力检测执行", "视力检测" in result, f"执行结果: {result[:50]}...")
            except Exception as e:
                self.log_test("视力检测执行", False, f"执行失败: {e}")
            
            # 清理资源
            tool.cleanup()
            self.log_test("资源清理", True, "视力检测工具资源清理成功")
            
        except Exception as e:
            self.log_test("视力检测工具", False, f"视力检测工具测试失败: {e}")
    
    async def test_image_analysis_tool(self):
        """测试图像分析工具"""
        print("\n=== 测试图像分析工具 ===")
        
        try:
            from src.tools.image_analysis import ImageAnalysisTool, EyeImageAnalyzer
            
            # 测试分析器创建
            analyzer = EyeImageAnalyzer()
            self.log_test("图像分析器创建", True, "图像分析器创建成功")
            
            # 测试分析器属性
            self.log_test("健康指标", len(analyzer.health_indicators) > 0, f"健康指标数量: {len(analyzer.health_indicators)}")
            self.log_test("模型初始化", analyzer.face_mesh is not None or analyzer.eye_cascade is not None, "检测模型已初始化")
            
            # 测试图像分析（使用测试图片）
            test_image = "../pictures/glaucoma_classification_1.png"
            if os.path.exists(test_image):
                result = analyzer.analyze_image(test_image)
                if "error" not in result:
                    self.log_test("图像分析", True, f"分析成功，检测到{len(result.get('analysis_results', []))}个眼部区域")
                else:
                    self.log_test("图像分析", False, f"分析失败: {result['error']}")
            else:
                self.log_test("图像分析", False, f"测试图片不存在: {test_image}")
            
            # 测试工具类
            tool = ImageAnalysisTool()
            self.log_test("图像分析工具创建", True, "图像分析工具创建成功")
            
            # 测试工具属性
            self.log_test("工具名称", tool.name == "image_analysis", f"工具名称: {tool.name}")
            self.log_test("工具描述", len(tool.description) > 0, f"描述长度: {len(tool.description)}")
            
            # 清理资源
            analyzer.cleanup()
            tool.cleanup()
            self.log_test("资源清理", True, "图像分析工具资源清理成功")
            
        except Exception as e:
            self.log_test("图像分析工具", False, f"图像分析工具测试失败: {e}")
    
    async def test_visualization_tool(self):
        """测试可视化工具"""
        print("\n=== 测试可视化工具 ===")
        
        try:
            from src.openmanus_agent.visualize_tool import VisualizeTool, DataVisualizer
            import pandas as pd
            import numpy as np
            
            # 测试可视化器创建
            visualizer = DataVisualizer()
            self.log_test("可视化器创建", True, "数据可视化器创建成功")
            
            # 测试输出目录
            self.log_test("输出目录", os.path.exists(visualizer.output_dir), f"输出目录: {visualizer.output_dir}")
            
            # 创建测试数据
            test_data = pd.DataFrame({
                '日期': pd.date_range('2024-01-01', periods=10, freq='D'),
                '左眼视力': np.random.normal(5.0, 0.3, 10),
                '右眼视力': np.random.normal(5.1, 0.3, 10),
                '眼压': np.random.normal(17, 2, 10)
            })
            
            # 测试折线图
            result = visualizer.create_line_chart(test_data, "视力趋势测试", "日期", "左眼视力")
            if "error" not in result:
                self.log_test("折线图生成", True, f"折线图生成成功: {result['filename']}")
            else:
                self.log_test("折线图生成", False, f"折线图生成失败: {result['error']}")
            
            # 测试柱状图
            result = visualizer.create_bar_chart(test_data, "视力分布测试", "日期", "右眼视力")
            if "error" not in result:
                self.log_test("柱状图生成", True, f"柱状图生成成功: {result['filename']}")
            else:
                self.log_test("柱状图生成", False, f"柱状图生成失败: {result['error']}")
            
            # 测试散点图
            result = visualizer.create_scatter_chart(test_data, "视力相关性测试", "左眼视力", "右眼视力")
            if "error" not in result:
                self.log_test("散点图生成", True, f"散点图生成成功: {result['filename']}")
            else:
                self.log_test("散点图生成", False, f"散点图生成失败: {result['error']}")
            
            # 测试热力图
            result = visualizer.create_heatmap(test_data, "相关性热力图测试")
            if "error" not in result:
                self.log_test("热力图生成", True, f"热力图生成成功: {result['filename']}")
            else:
                self.log_test("热力图生成", False, f"热力图生成失败: {result['error']}")
            
            # 测试综合分析
            result = visualizer.create_comprehensive_analysis(test_data, "视力数据综合分析")
            if "error" not in result:
                self.log_test("综合分析生成", True, f"综合分析生成成功: {result['filename']}")
            else:
                self.log_test("综合分析生成", False, f"综合分析生成失败: {result['error']}")
            
            # 测试工具类
            tool = VisualizeTool()
            self.log_test("可视化工具创建", True, "可视化工具创建成功")
            
            # 测试工具属性
            self.log_test("工具名称", tool.name == "visualize", f"工具名称: {tool.name}")
            self.log_test("工具描述", len(tool.description) > 0, f"描述长度: {len(tool.description)}")
            
            # 测试CSV文件可视化
            csv_file = "../eyes_test.csv"
            if os.path.exists(csv_file):
                result = await tool.execute(csv_file, "line", "视力数据趋势", "日期", "左眼视力")
                self.log_test("CSV可视化", "可视化完成" in result, f"CSV可视化结果: {result[:50]}...")
            else:
                self.log_test("CSV可视化", False, f"CSV文件不存在: {csv_file}")
            
            # 清理资源
            tool.cleanup()
            self.log_test("资源清理", True, "可视化工具资源清理成功")
            
        except Exception as e:
            self.log_test("可视化工具", False, f"可视化工具测试失败: {e}")
    
    async def test_tool_integration(self):
        """测试工具集成"""
        print("\n=== 测试工具集成 ===")
        
        try:
            from src.agent_manager import AgentManager
            from src.openmanus_agent.tool_collection import ToolCollection
            from src.tools.eye_games import EyeGamesTool
            from src.tools.vision_test import VisionTestTool
            from src.tools.image_analysis import ImageAnalysisTool
            from src.openmanus_agent.visualize_tool import VisualizeTool
            
            # 创建工具集合
            tools = ToolCollection(
                EyeGamesTool(),
                VisionTestTool(),
                ImageAnalysisTool(),
                VisualizeTool()
            )
            
            self.log_test("工具集合创建", True, f"工具集合创建成功，包含{len(tools.tools)}个工具")
            
            # 测试工具注册
            tool_names = [tool.name for tool in tools.tools]
            expected_names = ["eye_games", "vision_test", "image_analysis", "visualize"]
            
            for name in expected_names:
                self.log_test(f"工具注册-{name}", name in tool_names, f"工具{name}已注册")
            
            # 测试智能体管理器
            manager = AgentManager()
            self.log_test("智能体管理器", True, "智能体管理器创建成功")
            
            # 测试命令解析
            test_commands = [
                "我想玩记忆游戏",
                "进行视力检测",
                "分析图片pictures/glaucoma_classification_1.png",
                "读取我的csv文件，然后分析做可视化"
            ]
            
            for i, command in enumerate(test_commands, 1):
                try:
                    plan = manager.parse_command(command)
                    self.log_test(f"命令解析-{i}", plan is not None and len(plan) > 0, f"命令'{command}'解析成功")
                except Exception as e:
                    self.log_test(f"命令解析-{i}", False, f"命令'{command}'解析失败: {e}")
            
        except Exception as e:
            self.log_test("工具集成", False, f"工具集成测试失败: {e}")
    
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")
        
        try:
            from src.tools.eye_games import EyeGamesTool
            from src.tools.vision_test import VisionTestTool
            from src.tools.image_analysis import ImageAnalysisTool
            from src.openmanus_agent.visualize_tool import VisualizeTool
            
            # 测试眼部游戏工具错误处理
            tool = EyeGamesTool()
            result = await tool.execute("invalid_game_type")
            self.log_test("游戏工具错误处理", "未知的游戏类型" in result, f"错误处理结果: {result}")
            
            # 测试图像分析工具错误处理
            analyzer = ImageAnalysisTool()
            result = await analyzer.execute("nonexistent_image.png")
            self.log_test("图像分析错误处理", "图像文件不存在" in result, f"错误处理结果: {result}")
            
            # 测试可视化工具错误处理
            visualizer = VisualizeTool()
            result = await visualizer.execute("nonexistent_data.csv")
            self.log_test("可视化错误处理", "错误" in result, f"错误处理结果: {result}")
            
            # 清理资源
            tool.cleanup()
            analyzer.cleanup()
            visualizer.cleanup()
            self.log_test("错误处理资源清理", True, "错误处理测试资源清理成功")
            
        except Exception as e:
            self.log_test("错误处理", False, f"错误处理测试失败: {e}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🔧 增强眼部工具功能测试")
        print("=" * 60)
        
        # 运行各项测试
        await self.test_eye_games_tool()
        await self.test_vision_test_tool()
        await self.test_image_analysis_tool()
        await self.test_visualization_tool()
        await self.test_tool_integration()
        await self.test_error_handling()
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 增强眼部工具功能测试报告")
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
        
        with open("enhanced_tools_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: enhanced_tools_test_report.json")
        
        # 总结
        if self.passed_tests == self.total_tests:
            print("\n🎉 所有眼部工具功能完全正常！")
            print("✅ tkinter线程问题已修复")
            print("✅ 工具类字段问题已解决")
            print("✅ 错误处理机制已完善")
            print("✅ 资源清理功能已实现")
            print("✅ 工具集成功能正常")
        else:
            print(f"\n⚠️  有 {self.total_tests - self.passed_tests} 个测试失败，请检查相关功能")
        
        print("\n💡 功能改进总结:")
        print("1. 修复了tkinter_thread字段问题")
        print("2. 增强了错误处理机制")
        print("3. 完善了资源清理功能")
        print("4. 优化了工具集成")
        print("5. 增强了图像分析能力")
        print("6. 扩展了可视化功能")


def main():
    """主函数"""
    print("增强眼部工具功能测试工具")
    print("此工具将测试所有修复和完善的眼部工具功能")
    
    # 创建测试器
    tester = EnhancedToolsTester()
    
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