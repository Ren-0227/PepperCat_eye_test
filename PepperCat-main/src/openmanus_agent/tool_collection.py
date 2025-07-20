from typing import Dict, Any
import re

class ToolCollection:
    def __init__(self, *tools):
        self.tool_map = {}
        for tool in tools:
            names = set()
            base = tool.name.lower()
            names.add(base)
            # 支持下划线、去除tool后缀、驼峰转下划线
            if base.endswith('tool'):
                names.add(base[:-4])
            names.add(base.replace('_', ''))
            names.add(re.sub(r'tool$', '', base))
            # 驼峰转下划线
            snake = re.sub(r'([a-z])([A-Z])', r'\1_\2', tool.name).lower()
            names.add(snake)
            for n in names:
                self.tool_map[n] = tool
    def to_params(self):
        return [tool.to_param() for tool in self.tool_map.values()]
    async def execute(self, name: str, tool_input: dict):
        tool = self.tool_map.get(name.lower())
        if tool is None:
            return f"Tool {name} not found"
        return await tool(**tool_input) 