from typing import Any, Dict, List, Optional


class ToolCollection:
    """工具集合类，用于管理多个工具"""
    
    def __init__(self, *tools):
        self.tools = list(tools)
    
    def add_tool(self, tool: Dict[str, Any]) -> None:
        """添加工具"""
        self.tools.append(tool)
    
    def add_tools(self, *tools: Dict[str, Any]) -> None:
        """添加多个工具"""
        for tool in tools:
            self.add_tool(tool)
    
    def remove_tool(self, tool_name: str) -> bool:
        """移除工具"""
        for i, tool in enumerate(self.tools):
            if tool.get("name") == tool_name:
                del self.tools[i]
                return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取指定工具"""
        for tool in self.tools:
            if tool.get("name") == tool_name:
                return tool
        return None
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """获取所有工具"""
        return self.tools.copy()
    
    def get_tool_names(self) -> List[str]:
        """获取所有工具名称"""
        return [tool.get("name", "") for tool in self.tools]
    
    def get_tools_info(self) -> List[Dict[str, str]]:
        """获取工具信息"""
        return [
            {
                "name": tool.get("name", ""),
                "description": tool.get("description", "")
            }
            for tool in self.tools
        ]
    
    def clear(self) -> None:
        """清空所有工具"""
        self.tools.clear()
    
    def __len__(self) -> int:
        return len(self.tools)
    
    def __iter__(self):
        return iter(self.tools)
    
    def __getitem__(self, index):
        return self.tools[index]
    
    def __contains__(self, tool_name: str) -> bool:
        return any(tool.get("name") == tool_name for tool in self.tools) 