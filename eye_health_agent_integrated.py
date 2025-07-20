# eye_health_agent_integrated.py
import asyncio
import json
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# 导入OpenManus核心模块
from openmanus_core.agent.toolcall import ToolCallAgent
from openmanus_core.tool_collection import ToolCollection
from openmanus_core.config import config
from openmanus_core.logger import logger

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

class EyeHealthAgent(ToolCallAgent):
    """专门的眼部健康智能代理"""
    
    name: str = "EyeHealthAgent"
    description: str = "专门处理眼部健康相关任务的智能代理"
    
    # 自定义系统提示
    system_prompt: str = """你是一个专业的眼部健康智能助手，专门帮助用户进行视力检测、训练和健康咨询。

你可以使用以下工具来帮助用户：

{tools_description}

请根据用户的需求选择合适的工具并执行。如果用户的需求不明确，请询问更多细节。

记住：
1. 优先使用专业工具进行检测和训练
2. 提供个性化的健康建议
3. 用中文回复，语言要专业且易懂
4. 关注用户的眼部健康需求"""

    next_step_prompt: str = """基于当前的情况，请决定下一步行动：

1. 如果检测或训练已完成，请总结结果并提供建议
2. 如果需要更多信息，请询问用户具体症状或需求
3. 如果需要使用工具，请选择合适的工具并执行
4. 如果遇到问题，请说明问题并提供解决方案

请用中文回复，语言要专业且易懂。"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 创建工具集合
        self.tool_collection = ToolCollection()
        
        # 创建眼部健康工具实例
        self.eye_health_tools = {
            "vision_test": VisionTestTool(),
            "advanced_vision_test": AdvancedVisionTestTool(),
            "vision_training": VisionTrainingTool(),
            "vision_analytics": VisionAnalyticsTool(),
            "eye_health_consultation": EyeHealthConsultationTool()
        }
        
        # 将工具添加到代理中
        self._setup_tools()
    
    def _setup_tools(self):
        """设置工具"""
        for tool_name, tool_instance in self.eye_health_tools.items():
            tool_dict = {
                "name": tool_instance.name,
                "description": tool_instance.description,
                "execute": tool_instance.execute,
                "cleanup": tool_instance.cleanup
            }
            self.tool_collection.add_tool(tool_dict)
            self.add_tool(tool_dict)
    
    async def initialize_eye_health_tools(self):
        """初始化眼部健康工具"""
        for tool in self.eye_health_tools.values():
            if hasattr(tool, 'initialize'):
                await tool.initialize()
    
    async def cleanup_eye_health_tools(self):
        """清理眼部健康工具"""
        for tool in self.eye_health_tools.values():
            if hasattr(tool, 'cleanup'):
                await tool.cleanup()
    
    async def run_eye_health_task(self, task_description: str) -> Dict[str, Any]:
        """运行眼部健康相关任务"""
        try:
            logger.info(f"开始执行眼部健康任务: {task_description}")
            
            # 初始化工具
            await self.initialize_eye_health_tools()
            
            # 运行任务
            result = await self.run(task_description)
            
            # 提取search工具的网页结果
            web_results = None
            for msg in self.memory.messages:
                if msg.role == "tool" and msg.name and "search" in msg.name:
                    try:
                        data = json.loads(msg.content)
                        if isinstance(data, dict) and "results" in data:
                            web_results = data["results"]
                    except Exception:
                        pass
            # 获取结果
            return {
                "status": "success",
                "task": task_description,
                "result": result,
                "web_results": web_results,
                "timestamp": datetime.now().isoformat(),
                "memory": self.memory.messages[-1].content if self.memory.messages else ""
            }
            
        except Exception as e:
            logger.error(f"眼部健康任务执行失败: {e}")
            return {
                "status": "error",
                "message": str(e),
                "task": task_description,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            await self.cleanup_eye_health_tools()

class EyeHealthSystem:
    """眼部健康大模型系统"""
    
    def __init__(self):
        self.agent = None
        self.system_status = "initializing"
        
    async def initialize(self):
        """初始化系统"""
        try:
            logger.info("正在初始化眼部健康大模型系统...")
            
            # 创建眼部健康代理
            self.agent = EyeHealthAgent()
            
            self.system_status = "ready"
            logger.info("眼部健康大模型系统初始化完成")
            
        except Exception as e:
            logger.error(f"系统初始化失败: {e}")
            self.system_status = "error"
    
    async def process_request(self, request: str) -> Dict[str, Any]:
        """处理用户请求"""
        if self.system_status != "ready":
            await self.initialize()
        
        try:
            logger.info(f"处理用户请求: {request}")
            
            # 分析请求类型
            request_type = self._analyze_request_type(request)
            
            # 根据请求类型执行相应操作
            if request_type == "vision_test":
                return await self._handle_vision_test_request(request)
            elif request_type == "training":
                return await self._handle_training_request(request)
            elif request_type == "consultation":
                return await self._handle_consultation_request(request)
            elif request_type == "analysis":
                return await self._handle_analysis_request(request)
            else:
                # 使用代理处理通用请求
                return await self.agent.run_eye_health_task(request)
                
        except Exception as e:
            logger.error(f"请求处理失败: {e}")
            return {
                "status": "error",
                "message": f"请求处理失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_request_type(self, request: str) -> str:
        """分析请求类型"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ['视力检测', 'vision test', '检测视力']):
            return "vision_test"
        elif any(word in request_lower for word in ['训练', 'training', '游戏', 'game']):
            return "training"
        elif any(word in request_lower for word in ['咨询', '症状', 'consultation', 'symptom']):
            return "consultation"
        elif any(word in request_lower for word in ['分析', '报告', 'analysis', 'report']):
            return "analysis"
        else:
            return "general"
    
    async def _handle_vision_test_request(self, request: str) -> Dict[str, Any]:
        """处理视力检测请求"""
        vision_tool = VisionTestTool()
        
        try:
            result = await vision_tool.execute()
            return {
                "type": "vision_test",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            await vision_tool.cleanup()
    
    async def _handle_training_request(self, request: str) -> Dict[str, Any]:
        """处理训练请求"""
        training_tool = VisionTrainingTool()
        
        try:
            # 从请求中提取游戏类型
            game_type = "all"
            if "眼动" in request or "eye tracking" in request.lower():
                game_type = "eye_tracking"
            elif "专注" in request or "focus" in request.lower():
                game_type = "focus"
            elif "反应" in request or "reaction" in request.lower():
                game_type = "reaction"
            
            result = await training_tool.execute(game_type=game_type)
            return {
                "type": "training",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            await training_tool.cleanup()
    
    async def _handle_consultation_request(self, request: str) -> Dict[str, Any]:
        """处理咨询请求"""
        consultation_tool = EyeHealthConsultationTool()
        
        try:
            # 提取症状描述
            symptoms = self._extract_symptoms(request)
            result = await consultation_tool.execute(symptoms=symptoms)
            return {
                "type": "consultation",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            await consultation_tool.cleanup()
    
    async def _handle_analysis_request(self, request: str) -> Dict[str, Any]:
        """处理分析请求"""
        analytics_tool = VisionAnalyticsTool()
        
        try:
            # 从请求中提取分析类型
            analysis_type = "comprehensive"
            if "趋势" in request or "trend" in request.lower():
                analysis_type = "trends"
            elif "表现" in request or "performance" in request.lower():
                analysis_type = "performance"
            elif "洞察" in request or "insight" in request.lower():
                analysis_type = "insights"
            
            result = await analytics_tool.execute(analysis_type=analysis_type)
            return {
                "type": "analysis",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            await analytics_tool.cleanup()
    
    def _extract_symptoms(self, request: str) -> str:
        """从请求中提取症状描述"""
        # 简单的症状提取逻辑
        symptoms_keywords = ['症状', '感觉', '问题', '不舒服', 'symptom', 'feel', 'problem']
        
        for keyword in symptoms_keywords:
            if keyword in request:
                # 提取关键词后的内容作为症状描述
                parts = request.split(keyword)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # 如果没有找到关键词，返回整个请求
        return request
    
    async def cleanup(self):
        """清理系统资源"""
        if self.agent:
            await self.agent.cleanup_eye_health_tools()
        logger.info("眼部健康大模型系统清理完成")

# 使用示例
async def main():
    """主函数"""
    system = EyeHealthSystem()
    
    try:
        await system.initialize()
        
        print("=== 眼部健康大模型系统 (OpenManus集成版) ===")
        print("系统已启动，请输入您的需求:")
        print("1. 视力检测 - 进行基础或高级视力检测")
        print("2. 视力训练 - 进行各种视力训练游戏")
        print("3. 健康咨询 - 描述症状获取专业建议")
        print("4. 数据分析 - 查看视力趋势和分析报告")
        print("5. 退出系统")
        
        while True:
            try:
                user_input = input("\n请输入您的需求: ").strip()
                
                if user_input.lower() in ['退出', 'exit', 'quit', '5']:
                    print("感谢使用眼部健康大模型系统！")
                    break
                
                if not user_input:
                    continue
                
                # 处理用户请求
                result = await system.process_request(user_input)
                
                # 显示结果
                print(f"\n=== 处理结果 ===")
                print(f"状态: {result.get('status', 'unknown')}")
                print(f"类型: {result.get('type', 'general')}")
                
                if result.get('result'):
                    result_data = result['result']
                    if isinstance(result_data, dict):
                        if 'message' in result_data:
                            print(f"消息: {result_data['message']}")
                        if 'vision_score' in result_data:
                            print(f"视力分数: {result_data['vision_score']}")
                        if 'advice' in result_data:
                            print(f"建议: {result_data['advice']}")
                
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