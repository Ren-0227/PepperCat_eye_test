from src.openmanus_agent.tool_base import BaseTool

class FileOpsTool(BaseTool):
    name: str = "fileopstool"
    description: str = "Write text content to a local file."
    parameters: dict = {
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "The file name to write to."},
            "content": {"type": "string", "description": "The text content to write."}
        },
        "required": ["filename", "content"],
    }
    async def execute(self, filename: str, content: str) -> str:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"内容已写入文件: {filename}"
        except Exception as e:
            return f"写入文件失败: {e}" 