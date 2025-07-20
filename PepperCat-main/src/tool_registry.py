import asyncio
from typing import Any, Dict

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, func):
        self.tools[name] = func

    async def run_tool(self, name, **kwargs):
        if name in self.tools:
            tool = self.tools[name]
            try:
                # 检查是否是异步函数
                if asyncio.iscoroutinefunction(tool):
                    result = await tool(**kwargs)
                else:
                    result = tool(**kwargs)
                return result
            except Exception as e:
                return f"工具 {name} 执行失败: {str(e)}"
        return f"工具 {name} 未注册"
    
    def run_tool_sync(self, name, **kwargs):
        """同步运行工具（用于非异步环境）"""
        if name in self.tools:
            tool = self.tools[name]
            try:
                return tool(**kwargs)
            except Exception as e:
                return f"工具 {name} 执行失败: {str(e)}"
        return f"工具 {name} 未注册" 