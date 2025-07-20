class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, func):
        self.tools[name] = func

    def run_tool(self, name, **kwargs):
        if name in self.tools:
            return self.tools[name](**kwargs)
        return f"工具 {name} 未注册" 