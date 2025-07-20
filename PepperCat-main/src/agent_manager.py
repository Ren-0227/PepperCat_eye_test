import asyncio
import re
import json
from .tool_registry import ToolRegistry
from .tools.ollama_client import ask_ollama

class AgentManager:
    def __init__(self):
        self.tool_registry = ToolRegistry()
        # 注册所有工具
        from .tools.web_search import web_search
        from .tools.pet_control import pet_say
        from .tools.eye_games import EyeGamesTool
        from .tools.image_analysis import ImageAnalysisTool
        from .tools.vision_test import VisionTestTool
        from .tools.oct_analysis import OCTAnalysisTool
        from .openmanus_agent.visualize_tool import VisualizeTool
        
        self.tool_registry.register("web_search", web_search)
        self.tool_registry.register("pet_say", pet_say)
        self.tool_registry.register("eye_games", EyeGamesTool())
        self.tool_registry.register("image_analysis", ImageAnalysisTool())
        self.tool_registry.register("oct_analysis", OCTAnalysisTool())
        self.tool_registry.register("vision_test", VisionTestTool())
        self.tool_registry.register("visualize", VisualizeTool())

    def parse_command(self, user_input):
        prompt = (
            "你是一个智能助手，用户输入命令后，请将其拆解为工具调用计划，"
            "输出格式为JSON数组，每个元素包含tool和args字段。例如："
            '[{"tool": "web_search", "args": {"query": "天气"}}, {"tool": "pet_say", "args": {"message": "天气晴"}}]\n'
            "可用工具：\n"
            "- web_search(搜索): 搜索网络信息\n"
            "- pet_say(说话): 桌宠说话\n"
            "- eye_games(眼部游戏): 启动眼部训练游戏\n"
            "- image_analysis(图片分析): 分析普通眼部图片（如自拍、手机拍摄的眼部照片），不能分析OCT图片\n"
            "- oct_analysis(OCT分析): 专门分析OCT（光学相干断层扫描）图片，检测青光眼、黄斑变性、糖尿病视网膜病变等眼部疾病。只要用户输入中出现‘OCT’、‘光学相干断层扫描’、‘OCT图片’、‘OCT检查’等关键词，必须使用本工具，不能用image_analysis或vision_test。\n"
            "- vision_test(视力检测): 进行视力表测试、E字表测试等，不能分析图片\n"
            "- visualize(可视化): 创建数据可视化图表\n"
            "\n"
            "【特别注意】\n"
            "1. 只要用户输入中出现‘OCT’、‘光学相干断层扫描’、‘OCT图片’、‘OCT检查’等关键词，必须使用oct_analysis工具，不能用image_analysis或vision_test。\n"
            "2. image_analysis 仅用于分析普通眼部照片，不能分析OCT图片。\n"
            "3. vision_test 仅用于视力表/E字表等测试，不能分析任何图片。\n"
            "4. 用户输入中有‘csv’、‘数据可视化’等，使用visualize。\n"
            "5. 用户输入中有‘玩游戏’、‘训练’等，使用eye_games。\n"
            "\n"
            "【正例】\n"
            "用户：分析我的OCT图片pictures/eyes.png\n"
            "输出：[{\'tool\': \'oct_analysis\', \'args\': {\'image_path\': \'pictures/eyes.png\'}}]\n"
            "用户：分析我的自拍眼部照片\n"
            "输出：[{\'tool\': \'image_analysis\', \'args\': {\'image_path\': \'xxx.jpg\'}}]\n"
            "用户：做一次视力检测\n"
            "输出：[{\'tool\': \'vision_test\', \'args\': {}}]\n"
            "\n"
            "【反例】\n"
            "用户：分析OCT图片\n"
            "错误：用image_analysis或vision_test\n"
            "正确：用oct_analysis\n"
            "\n"
            f"用户命令：{user_input}\n"
            "请只输出JSON，不要输出其他内容。"
        )
        plan_str = ask_ollama(prompt)
        # 尝试只提取第一个JSON数组
        try:
            match = re.search(r'\[.*?\]', plan_str, re.DOTALL)
            if match:
                plan = json.loads(match.group(0))
            else:
                # 兜底：自动提取图片路径
                img_path = self._extract_image_path(user_input)
                plan = [{"tool": "oct_analysis", "args": {"image_path": img_path}}]
        except Exception:
            img_path = self._extract_image_path(user_input)
            plan = [{"tool": "oct_analysis", "args": {"image_path": img_path}}]
        return plan

    def _extract_image_path(self, user_input):
        """自动从用户输入中提取图片路径，支持桌面/desktop/本地路径"""
        # 匹配绝对路径、桌面路径、pictures路径、文件名
        img_match = re.search(r'(?:桌面|Desktop)[/\\]?([\w\-\u4e00-\u9fa5]+\.(?:png|jpg|jpeg|bmp|gif))', user_input, re.IGNORECASE)
        if img_match:
            img_name = img_match.group(1)
            # 假定用户已手动放到 pictures/ 目录
            return f'pictures/{img_name}'
        # 匹配 pictures/xxx.png
        img_match2 = re.search(r'(pictures[/\\][\w\-\u4e00-\u9fa5]+\.(?:png|jpg|jpeg|bmp|gif))', user_input, re.IGNORECASE)
        if img_match2:
            return img_match2.group(1).replace('\\', '/').replace('pictures//', 'pictures/')
        # 匹配任意文件名
        img_match3 = re.search(r'([\w\-\u4e00-\u9fa5]+\.(?:png|jpg|jpeg|bmp|gif))', user_input, re.IGNORECASE)
        if img_match3:
            return f'pictures/{img_match3.group(1)}'
        # 默认兜底
        return 'pictures/eyes.png'

    async def run_plan(self, plan):
        results = []
        for step in plan:
            try:
                result = await self.tool_registry.run_tool(step["tool"], **step["args"])
                results.append(result)
            except Exception as e:
                error_result = f"工具 {step['tool']} 执行失败: {str(e)}"
                results.append(error_result)
        return results
    
    def run_plan_sync(self, plan):
        """同步运行计划（用于非异步环境）"""
        results = []
        for step in plan:
            try:
                result = self.tool_registry.run_tool_sync(step["tool"], **step["args"])
                results.append(result)
            except Exception as e:
                error_result = f"工具 {step['tool']} 执行失败: {str(e)}"
                results.append(error_result)
        return results 