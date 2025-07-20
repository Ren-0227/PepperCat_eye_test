import requests

class OllamaChatCompletion:
    def __init__(self, model="deepseek-llm"):
        self.model = model

    async def ask_tool(self, messages, system_msgs=None, tools=None, tool_choice=None):
        # 拼接 prompt
        prompt = ""
        if system_msgs:
            for msg in system_msgs:
                prompt += msg.content + "\n"
        for msg in messages:
            prompt += msg.content + "\n"
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload, timeout=60)
        # 这里需适配 OpenManus 的 response 结构
        class DummyResponse:
            def __init__(self, content):
                self.content = content
                self.tool_calls = []
        return DummyResponse(response.json().get("response", "[无回复]")) 