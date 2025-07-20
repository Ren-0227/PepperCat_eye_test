from typing import ClassVar, Dict, Any
from src.openmanus_agent.tool_base import BaseTool
import requests
import re

class WebSearchTool(BaseTool):
    name: str = "websearchtool"
    description: str = "Search the web for information using a query string."
    parameters: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词"}
        },
        "required": ["query"]
    }
    async def execute(self, query: str) -> str:
        # 使用Google搜索（抓取前几个结果摘要）
        try:
            url = f"https://www.google.com/search?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=8)
            html = resp.text
            # 提取Google搜索结果摘要（前3条）
            results = re.findall(r'<span class="aCOpRe">(.*?)</span>', html, re.S)
            if not results:
                # 新版Google可能用这个class
                results = re.findall(r'<div class="BNeawe s3v9rd AP7Wnd">(.*?)</div>', html, re.S)
            clean = lambda s: re.sub(r'<.*?>', '', s).replace('\n', '').strip()
            summary = '\n'.join([clean(r) for r in results[:3]])
            return summary or "未能获取到有效的Google搜索摘要。"
        except Exception as e:
            return f"Google搜索异常: {e}" 