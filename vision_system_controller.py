# vision_system_controller.py
import os
import sys
import time
from typing import Dict, List, Optional
from enum import Enum

# 导入自定义模块
from vision_test import VisionTester
from advanced_vision_test import AdvancedVisionTest
from vision_training_game import VisionTrainingGame
from vision_analytics import VisionAnalytics

class SystemMode(Enum):
    BASIC_VISION_TEST = "basic_vision_test"
    ADVANCED_VISION_TEST = "advanced_vision_test"
    TRAINING_GAMES = "training_games"
    ANALYTICS = "analytics"
    COMPREHENSIVE_SYSTEM = "comprehensive_system"

class VisionSystemController:
    """视力系统主控制器"""
    
    def __init__(self):
        self.current_mode = None
        self.system_status = "ready"
        self.user_session = {}
        
        # 初始化各个子系统
        self.basic_tester = None
        self.advanced_tester = None
        self.training_games = None
        self.analytics = None
        
        print("=== 视力健康管理系统 ===")
        print("系统初始化完成")
    
    def start_system(self):
        """启动系统"""
        while True:
            try:
                self._show_main_menu()
                choice = input("\n请选择功能 (0-6): ").strip()
                
                if choice == '0':
                    print("感谢使用视力健康管理系统！")
                    break
                elif choice == '1':
                    self._run_basic_vision_test()
                elif choice == '2':
                    self._run_advanced_vision_test()
                elif choice == '3':
                    self._run_training_games()
                elif choice == '4':
                    self._run_analytics()
                elif choice == '5':
                    self._run_comprehensive_system()
                elif choice == '6':
                    self._show_system_info()
                else:
                    print("无效选择，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n检测到中断信号，正在退出...")
                break
            except Exception as e:
                print(f"系统错误: {str(e)}")
                continue
    
    def _show_main_menu(self):
        """显示主菜单"""
        print("\n" + "="*50)
        print("视力健康管理系统")
        print("="*50)
        print("1. 基础视力检测")
        print("2. 高级视力检测")
        print("3. 视力训练游戏")
        print("4. 数据分析报告")
        print("5. 综合视力管理")
        print("6. 系统信息")
        print("0. 退出系统")
        print("="*50)
    
    def _run_basic_vision_test(self):
        """运行基础视力检测"""
        print("\n=== 基础视力检测 ===")
        print("正在初始化基础视力检测系统...")
        
        try:
            if self.basic_tester is None:
                self.basic_tester = VisionTester()
            
            print("基础视力检测开始...")
            result = self.basic_tester.run_test()
            
            if result is not None:
                print(f"\n检测完成！视力结果: {result:.1f}")
                self._save_basic_test_result(result)
            else:
                print("检测失败，请重试")
                
        except Exception as e:
            print(f"基础视力检测失败: {str(e)}")
        finally:
            if self.basic_tester:
                self.basic_tester.cleanup()
    
    def _run_advanced_vision_test(self):
        """运行高级视力检测"""
        print("\n=== 高级视力检测 ===")
        print("正在初始化高级视力检测系统...")
        
        try:
            if self.advanced_tester is None:
                self.advanced_tester = AdvancedVisionTest()
            
            print("高级视力检测开始...")
            report = self.advanced_tester.start_comprehensive_test()
            
            print("\n=== 高级视力检测报告 ===")
            print(f"测试时间: {report['test_timestamp']}")
            print(f"整体评估: {report['overall_assessment']}")
            
            # 显示详细结果
            if 'basic_vision' in report:
                basic = report['basic_vision']
                print(f"基础视力: {basic.get('estimated_vision', 'N/A')}")
                print(f"准确率: {basic.get('accuracy', 0):.2%}")
            
            if 'color_vision' in report:
                color = report['color_vision']
                print(f"色觉评分: {color.get('overall_score', 0):.2f}")
            
            if 'contrast_sensitivity' in report:
                contrast = report['contrast_sensitivity']
                print(f"对比度阈值: {contrast.get('threshold', 0):.2f}")
            
            if 'eye_tracking' in report:
                eye = report['eye_tracking']
                print(f"眼疲劳评分: {eye.get('eye_fatigue_score', 0):.2f}")
            
            print("\n建议:")
            for rec in report['recommendations']:
                print(f"- {rec}")
                
        except Exception as e:
            print(f"高级视力检测失败: {str(e)}")
        finally:
            if self.advanced_tester:
                self.advanced_tester.cleanup()
    
    def _run_training_games(self):
        """运行视力训练游戏"""
        print("\n=== 视力训练游戏 ===")
        print("正在初始化训练游戏系统...")
        
        try:
            if self.training_games is None:
                self.training_games = VisionTrainingGame()
            
            self.training_games.start_game_menu()
            
        except Exception as e:
            print(f"训练游戏启动失败: {str(e)}")
        finally:
            if self.training_games:
                self.training_games.cleanup()
    
    def _run_analytics(self):
        """运行数据分析"""
        print("\n=== 视力数据分析 ===")
        print("正在加载分析系统...")
        
        try:
            if self.analytics is None:
                self.analytics = VisionAnalytics()
            
            # 生成分析报告
            report = self.analytics.create_vision_report()
            
            print("\n=== 视力数据分析报告 ===")
            print(f"报告生成时间: {report['report_date']}")
            
            # 显示视力趋势
            vision_trends = report['vision_trends']
            if 'error' not in vision_trends:
                trend = vision_trends.get('trend', {})
                print(f"\n视力趋势: {trend.get('trend', 'unknown')}")
                print(f"当前视力: {vision_trends.get('current_vision', 'N/A')}")
                print(f"最佳视力: {vision_trends.get('best_vision', 'N/A')}")
                
                improvement = vision_trends.get('improvement', {})
                print(f"改进状态: {improvement.get('status', 'unknown')}")
                print(f"改进率: {improvement.get('improvement_rate', 0):.2%}")
            
            # 显示游戏表现
            game_performance = report['game_performance']
            if 'error' not in game_performance:
                print("\n游戏表现:")
                for game_type, performance in game_performance.items():
                    print(f"- {game_type}: 平均分数 {performance.get('avg_score', 0):.1f}")
            
            # 显示个性化洞察
            insights = report['personalized_insights']
            print(f"\n视力健康状况: {insights['vision_health'].get('overall_health', 'unknown')}")
            print(f"风险等级: {insights['risk_assessment'].get('risk_level', 'unknown')}")
            
            # 显示建议
            print("\n个性化建议:")
            for rec in insights['training_recommendations']:
                print(f"- {rec}")
            
            # 生成趋势图
            print("\n正在生成视力趋势图...")
            self.analytics.plot_vision_trends("vision_trends.png")
            
        except Exception as e:
            print(f"数据分析失败: {str(e)}")
    
    def _run_comprehensive_system(self):
        """运行综合视力管理系统"""
        print("\n=== 综合视力管理系统 ===")
        print("这是一个完整的视力健康管理流程")
        
        try:
            # 1. 基础视力检测
            print("\n步骤1: 基础视力检测")
            self._run_basic_vision_test()
            
            # 2. 高级视力检测
            print("\n步骤2: 高级视力检测")
            self._run_advanced_vision_test()
            
            # 3. 视力训练游戏
            print("\n步骤3: 视力训练游戏")
            choice = input("是否进行视力训练游戏？(y/n): ").lower()
            if choice == 'y':
                self._run_training_games()
            
            # 4. 数据分析
            print("\n步骤4: 数据分析")
            self._run_analytics()
            
            # 5. 生成综合报告
            print("\n步骤5: 生成综合报告")
            self._generate_comprehensive_report()
            
        except Exception as e:
            print(f"综合系统运行失败: {str(e)}")
    
    def _generate_comprehensive_report(self):
        """生成综合报告"""
        print("\n=== 综合视力健康报告 ===")
        
        # 这里可以整合所有数据生成综合报告
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'system_usage': self._get_system_usage_stats(),
            'recommendations': self._generate_system_recommendations()
        }
        
        print(f"报告生成时间: {report['timestamp']}")
        print("\n系统使用统计:")
        for stat, value in report['system_usage'].items():
            print(f"- {stat}: {value}")
        
        print("\n综合建议:")
        for rec in report['recommendations']:
            print(f"- {rec}")
        
        # 保存综合报告
        self._save_comprehensive_report(report)
    
    def _get_system_usage_stats(self) -> Dict:
        """获取系统使用统计"""
        stats = {
            'basic_tests_completed': len([f for f in os.listdir('.') if 'basic_test' in f]),
            'advanced_tests_completed': len([f for f in os.listdir('.') if 'advanced_test' in f]),
            'games_played': len([f for f in os.listdir('.') if 'game_history' in f]),
            'reports_generated': len([f for f in os.listdir('.') if 'report' in f])
        }
        return stats
    
    def _generate_system_recommendations(self) -> List[str]:
        """生成系统建议"""
        recommendations = [
            "建议定期进行视力检测，至少每月一次",
            "建议每天进行15-20分钟的视力训练",
            "建议保持良好的用眼习惯，每30分钟休息5分钟",
            "建议定期查看数据分析报告，了解视力变化趋势",
            "建议根据个人情况调整训练计划"
        ]
        return recommendations
    
    def _save_comprehensive_report(self, report: Dict):
        """保存综合报告"""
        import json
        
        reports_dir = "comprehensive_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"{reports_dir}/comprehensive_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"综合报告已保存至: {filename}")
    
    def _save_basic_test_result(self, result: float):
        """保存基础测试结果"""
        import json
        
        test_result = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'test_type': 'basic_vision_test',
            'result': result,
            'status': 'completed'
        }
        
        results_dir = "basic_test_results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"{results_dir}/basic_test_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        
        print(f"测试结果已保存至: {filename}")
    
    def _show_system_info(self):
        """显示系统信息"""
        print("\n=== 系统信息 ===")
        print(f"系统版本: 1.0.0")
        print(f"当前状态: {self.system_status}")
        print(f"Python版本: {sys.version}")
        
        # 检查依赖模块
        modules = ['cv2', 'mediapipe', 'numpy', 'torch', 'matplotlib']
        print("\n依赖模块状态:")
        for module in modules:
            try:
                __import__(module)
                print(f"- {module}: ✓ 已安装")
            except ImportError:
                print(f"- {module}: ✗ 未安装")
        
        # 检查数据文件
        data_files = [
            "user_memory.json",
            "game_history.json",
            "vision_reports/",
            "analytics_reports/"
        ]
        
        print("\n数据文件状态:")
        for file_path in data_files:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    file_count = len([f for f in os.listdir(file_path) if f.endswith('.json')])
                    print(f"- {file_path}: ✓ 存在 ({file_count} 个文件)")
                else:
                    print(f"- {file_path}: ✓ 存在")
            else:
                print(f"- {file_path}: ✗ 不存在")
    
    def cleanup(self):
        """清理系统资源"""
        print("正在清理系统资源...")
        
        if self.basic_tester:
            self.basic_tester.cleanup()
        
        if self.advanced_tester:
            self.advanced_tester.cleanup()
        
        if self.training_games:
            self.training_games.cleanup()
        
        print("系统资源清理完成")

# 主程序入口
if __name__ == "__main__":
    try:
        controller = VisionSystemController()
        controller.start_system()
    except Exception as e:
        print(f"系统启动失败: {str(e)}")
    finally:
        if 'controller' in locals():
            controller.cleanup() 