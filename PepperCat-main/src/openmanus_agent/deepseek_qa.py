from typing import ClassVar, Dict, Any
from src.openmanus_agent.tool_base import BaseTool
from src.tools.ollama_client import ask_ollama

class DeepseekQATool(BaseTool):
    name: str = "deepseekqa"
    description: str = "用大模型分析数据"
    parameters: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "data": {"type": "string", "description": "数据内容"},
            "question": {"type": "string", "description": "分析指令"}
        },
        "required": ["data", "question"]
    }
    async def execute(self, data: str, question: str) -> str:
        prompt = f"请根据以下数据进行分析：\n{data}\n\n分析要求：{question}"
        return ask_ollama(prompt) 