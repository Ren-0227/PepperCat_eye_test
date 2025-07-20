from typing import ClassVar, Dict, Any
from src.openmanus_agent.tool_base import BaseTool

class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "读取本地文件内容"
    parameters: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "文件路径"}
        },
        "required": ["filename"]
    }
    async def execute(self, filename: str) -> str:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"读取失败: {e}" 