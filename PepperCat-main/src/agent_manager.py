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
        self.tool_registry.register("web_search", web_search)
        self.tool_registry.register("pet_say", pet_say)
        self.tool_registry.register("eye_games", EyeGamesTool())
        self.tool_registry.register("image_analysis", ImageAnalysisTool())
        self.tool_registry.register("vision_test", VisionTestTool())

    def parse_command(self, user_input):
        # 用 LLM 让其输出 JSON 工具链计划
        prompt = (
            "你是一个智能助手，用户输入命令后，请将其拆解为工具调用计划，"
            "输出格式为JSON数组，每个元素包含tool和args字段。例如："
            '[{"tool": "web_search", "args": {"query": "天气"}}, {"tool": "pet_say", "args": {"message": "今天天气晴"}}]\n'
            "可用工具：web_search(搜索)、pet_say(说话)、eye_games(眼部游戏)、image_analysis(图片分析)\n"
            f"用户命令：{user_input}\n"
            "请只输出JSON，不要输出其他内容。"
        )
        import json
        plan_str = ask_ollama(prompt)
        try:
            plan = json.loads(plan_str)
        except Exception:
            plan = [{"tool": "pet_say", "args": {"message": "无法解析指令"}}]
        return plan

    def run_plan(self, plan):
        results = []
        for step in plan:
            result = self.tool_registry.run_tool(step["tool"], **step["args"])
            results.append(result)
        return results 