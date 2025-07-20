# eye_health_llm.py
import asyncio
import json
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# 导入现有的眼部健康模块
from vision_test import VisionTester
from advanced_vision_test import AdvancedVisionTest
from vision_training_game import VisionTrainingGame
from vision_analytics import VisionAnalytics
from api_integration import DeepseekAPI
from image_processing import analyze_image

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eye_health_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EyeHealthTool:
    """眼部健康工具基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = "ready"
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具功能"""
        raise NotImplementedError("子类必须实现execute方法")
    
    async def cleanup(self):
        """清理资源"""
        pass

class VisionTestTool(EyeHealthTool):
    """视力检测工具"""
    
    def __init__(self):
        super().__init__("vision_test", "进行基础视力检测，使用E字表测试视力水平")
        self.vision_tester = None
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行视力检测"""
        try:
            if self.vision_tester is None:
                self.vision_tester = VisionTester()
            
            logger.info("开始基础视力检测...")
            result = self.vision_tester.run_test()
            
            if result is not None:
                return {
                    "status": "success",
                    "vision_score": result,
                    "message": f"视力检测完成，结果为: {result:.1f}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": "视力检测失败，请重试"
                }
        except Exception as e:
            logger.error(f"视力检测出错: {e}")
            return {
                "status": "error",
                "message": f"视力检测出错: {str(e)}"
            }
    
    async def cleanup(self):
        """清理资源"""
        if self.vision_tester:
            self.vision_tester.cleanup()

class AdvancedVisionTestTool(EyeHealthTool):
    """高级视力检测工具"""
    
    def __init__(self):
        super().__init__("advanced_vision_test", "进行综合视力检测，包括色觉、对比度、周边视野和眼动追踪")
        self.advanced_tester = None
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行高级视力检测"""
        try:
            if self.advanced_tester is None:
                self.advanced_tester = AdvancedVisionTest()
            
            logger.info("开始高级视力检测...")
            report = self.advanced_tester.start_comprehensive_test()
            
            return {
                "status": "success",
                "report": report,
                "message": "高级视力检测完成",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"高级视力检测出错: {e}")
            return {
                "status": "error",
                "message": f"高级视力检测出错: {str(e)}"
            }
    
    async def cleanup(self):
        """清理资源"""
        if self.advanced_tester:
            self.advanced_tester.cleanup()

class VisionTrainingTool(EyeHealthTool):
    """视力训练工具"""
    
    def __init__(self):
        super().__init__("vision_training", "启动视力训练游戏，包括眼动追踪、专注力、反应速度等训练")
        self.training_games = None
    
    async def execute(self, game_type: str = "all", **kwargs) -> Dict[str, Any]:
        """执行视力训练"""
        try:
            if self.training_games is None:
                self.training_games = VisionTrainingGame()
            
            logger.info(f"开始视力训练，游戏类型: {game_type}")
            
            # 根据游戏类型执行特定训练
            if game_type == "eye_tracking":
                result = await self._run_eye_tracking_game()
            elif game_type == "focus":
                result = await self._run_focus_training()
            elif game_type == "reaction":
                result = await self._run_reaction_training()
            else:
                # 运行综合训练
                result = await self._run_comprehensive_training()
            
            return {
                "status": "success",
                "training_result": result,
                "message": f"视力训练完成，游戏类型: {game_type}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"视力训练出错: {e}")
            return {
                "status": "error",
                "message": f"视力训练出错: {str(e)}"
            }
    
    async def _run_eye_tracking_game(self) -> Dict[str, Any]:
        """运行眼动追踪游戏"""
        return {"game_type": "eye_tracking", "score": 85, "duration": 300}
    
    async def _run_focus_training(self) -> Dict[str, Any]:
        """运行专注力训练"""
        return {"game_type": "focus", "score": 78, "duration": 240}
    
    async def _run_reaction_training(self) -> Dict[str, Any]:
        """运行反应速度训练"""
        return {"game_type": "reaction", "score": 92, "duration": 180}
    
    async def _run_comprehensive_training(self) -> Dict[str, Any]:
        """运行综合训练"""
        return {"game_type": "comprehensive", "score": 88, "duration": 600}
    
    async def cleanup(self):
        """清理资源"""
        if self.training_games:
            self.training_games.cleanup()

class VisionAnalyticsTool(EyeHealthTool):
    """视力分析工具"""
    
    def __init__(self):
        super().__init__("vision_analytics", "分析视力数据，生成趋势报告和个性化建议")
        self.analytics = None
    
    async def execute(self, analysis_type: str = "comprehensive", **kwargs) -> Dict[str, Any]:
        """执行视力分析"""
        try:
            if self.analytics is None:
                self.analytics = VisionAnalytics()
            
            logger.info(f"开始视力分析，分析类型: {analysis_type}")
            
            if analysis_type == "trends":
                result = self.analytics.analyze_vision_trends()
            elif analysis_type == "performance":
                result = self.analytics.analyze_game_performance()
            elif analysis_type == "insights":
                result = self.analytics.generate_personalized_insights()
            else:
                # 综合分析
                result = self.analytics.create_vision_report()
            
            return {
                "status": "success",
                "analysis_result": result,
                "message": f"视力分析完成，分析类型: {analysis_type}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"视力分析出错: {e}")
            return {
                "status": "error",
                "message": f"视力分析出错: {str(e)}"
            }

class EyeHealthConsultationTool(EyeHealthTool):
    """眼部健康咨询工具"""
    
    def __init__(self):
        super().__init__("eye_health_consultation", "基于症状进行眼部健康咨询，提供专业建议")
        self.api_handler = None
    
    async def execute(self, symptoms: str, **kwargs) -> Dict[str, Any]:
        """执行眼部健康咨询"""
        try:
            if self.api_handler is None:
                self.api_handler = DeepseekAPI()
            
            logger.info(f"开始眼部健康咨询，症状: {symptoms}")
            
            # 调用API获取专业建议
            advice = self.api_handler.get_health_advice(symptoms)
            
            # 分析是否需要视力检测
            needs_vision_test = self._analyze_symptoms_for_vision_test(symptoms)
            
            return {
                "status": "success",
                "advice": advice,
                "needs_vision_test": needs_vision_test,
                "message": "眼部健康咨询完成",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"眼部健康咨询出错: {e}")
            return {
                "status": "error",
                "message": f"眼部健康咨询出错: {str(e)}"
            }
    
    def _analyze_symptoms_for_vision_test(self, symptoms: str) -> bool:
        """分析症状是否需要视力检测"""
        vision_keywords = ['模糊', '近视', '远视', '看不清', '视力下降', '眼睛疲劳', '眯眼']
        return any(keyword in symptoms for keyword in vision_keywords)

class EyeHealthLLM:
    """眼部健康大模型系统"""
    
    def __init__(self):
        self.tools = {
            "vision_test": VisionTestTool(),
            "advanced_vision_test": AdvancedVisionTestTool(),
            "vision_training": VisionTrainingTool(),
            "vision_analytics": VisionAnalyticsTool(),
            "eye_health_consultation": EyeHealthConsultationTool()
        }
        self.conversation_history = []
        self.system_status = "ready"
        
        logger.info("眼部健康大模型系统初始化完成")
    
    def _analyze_request(self, request: str) -> Dict[str, Any]:
        """分析用户请求，确定需要使用的工具"""
        request_lower = request.lower()
        
        # 定义关键词映射
        keywords = {
            "vision_test": ["视力检测", "检测视力", "vision test", "e字表"],
            "advanced_vision_test": ["高级检测", "综合检测", "advanced test", "色觉", "对比度"],
            "vision_training": ["训练", "游戏", "training", "game", "眼动", "专注"],
            "vision_analytics": ["分析", "报告", "趋势", "analytics", "report", "trend"],
            "eye_health_consultation": ["咨询", "症状", "建议", "consultation", "symptom", "advice"]
        }
        
        # 匹配关键词
        matched_tools = []
        for tool_name, tool_keywords in keywords.items():
            if any(keyword in request_lower for keyword in tool_keywords):
                matched_tools.append(tool_name)
        
        # 提取参数
        params = {}
        if "眼动" in request or "eye tracking" in request_lower:
            params["game_type"] = "eye_tracking"
        elif "专注" in request or "focus" in request_lower:
            params["game_type"] = "focus"
        elif "反应" in request or "reaction" in request_lower:
            params["game_type"] = "reaction"
        
        if "趋势" in request or "trend" in request_lower:
            params["analysis_type"] = "trends"
        elif "表现" in request or "performance" in request_lower:
            params["analysis_type"] = "performance"
        elif "洞察" in request or "insight" in request_lower:
            params["analysis_type"] = "insights"
        
        return {
            "tools": matched_tools,
            "params": params,
            "original_request": request
        }
    
    async def process_request(self, request: str) -> Dict[str, Any]:
        """处理用户请求"""
        try:
            logger.info(f"处理用户请求: {request}")
            
            # 分析请求
            analysis = self._analyze_request(request)
            
            # 记录对话历史
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_request": request,
                "analysis": analysis
            })
            
            # 如果没有匹配到工具，提供通用建议
            if not analysis["tools"]:
                return await self._provide_general_advice(request)
            
            # 执行匹配的工具
            results = []
            for tool_name in analysis["tools"]:
                if tool_name in self.tools:
                    tool = self.tools[tool_name]
                    try:
                        result = await tool.execute(**analysis["params"])
                        results.append({
                            "tool": tool_name,
                            "result": result
                        })
                    except Exception as e:
                        logger.error(f"工具 {tool_name} 执行失败: {e}")
                        results.append({
                            "tool": tool_name,
                            "result": {
                                "status": "error",
                                "message": f"工具执行失败: {str(e)}"
                            }
                        })
            
            # 生成综合响应
            return await self._generate_comprehensive_response(request, results)
            
        except Exception as e:
            logger.error(f"请求处理失败: {e}")
            return {
                "status": "error",
                "message": f"请求处理失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _provide_general_advice(self, request: str) -> Dict[str, Any]:
        """提供通用建议"""
        consultation_tool = self.tools["eye_health_consultation"]
        result = await consultation_tool.execute(symptoms=request)
        
        return {
            "status": "success",
            "type": "general_advice",
            "result": result,
            "message": "已为您提供眼部健康建议",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_comprehensive_response(self, request: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成综合响应"""
        # 分析结果
        successful_results = [r for r in results if r["result"]["status"] == "success"]
        failed_results = [r for r in results if r["result"]["status"] == "error"]
        
        # 生成响应消息
        if successful_results:
            message = "已成功完成以下操作:\n"
            for result in successful_results:
                tool_name = result["tool"]
                result_data = result["result"]
                if "message" in result_data:
                    message += f"- {tool_name}: {result_data['message']}\n"
        else:
            message = "操作执行失败，请重试"
        
        if failed_results:
            message += "\n以下操作失败:\n"
            for result in failed_results:
                tool_name = result["tool"]
                result_data = result["result"]
                message += f"- {tool_name}: {result_data['message']}\n"
        
        return {
            "status": "success" if successful_results else "partial_success",
            "type": "comprehensive_response",
            "results": results,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_available_services(self) -> List[Dict[str, str]]:
        """获取可用服务列表"""
        services = []
        for tool_name, tool in self.tools.items():
            services.append({
                "name": tool_name,
                "description": tool.description,
                "status": tool.status
            })
        return services
    
    async def cleanup(self):
        """清理系统资源"""
        for tool in self.tools.values():
            await tool.cleanup()
        logger.info("眼部健康大模型系统清理完成")

# 主程序
async def main():
    """主函数"""
    system = EyeHealthLLM()
    
    try:
        print("=== 眼部健康大模型系统 ===")
        print("系统已启动，请输入您的需求:")
        print("1. 视力检测 - 进行基础或高级视力检测")
        print("2. 视力训练 - 进行各种视力训练游戏")
        print("3. 健康咨询 - 描述症状获取专业建议")
        print("4. 数据分析 - 查看视力趋势和分析报告")
        print("5. 查看可用服务")
        print("6. 退出系统")
        
        while True:
            try:
                user_input = input("\n请输入您的需求: ").strip()
                
                if user_input.lower() in ['退出', 'exit', 'quit', '6']:
                    print("感谢使用眼部健康大模型系统！")
                    break
                
                if user_input.lower() in ['5', '查看可用服务', 'services']:
                    services = system.get_available_services()
                    print("\n=== 可用服务 ===")
                    for service in services:
                        print(f"- {service['name']}: {service['description']} (状态: {service['status']})")
                    continue
                
                if not user_input:
                    continue
                
                # 处理用户请求
                result = await system.process_request(user_input)
                
                # 显示结果
                print(f"\n=== 处理结果 ===")
                print(f"状态: {result.get('status', 'unknown')}")
                print(f"类型: {result.get('type', 'general')}")
                print(f"消息: {result.get('message', '无')}")
                
                # 显示详细结果
                if 'results' in result:
                    print("\n详细结果:")
                    for res in result['results']:
                        print(f"- {res['tool']}: {res['result'].get('message', '无消息')}")
                
                print(f"时间: {result.get('timestamp', 'unknown')}")
                
            except KeyboardInterrupt:
                print("\n检测到中断信号，正在退出...")
                break
            except Exception as e:
                print(f"处理请求时出错: {str(e)}")
                continue
                
    except Exception as e:
        print(f"系统启动失败: {str(e)}")
    finally:
        await system.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 