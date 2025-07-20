from src.openmanus_agent.llm_ollama import OllamaChatCompletion
from src.openmanus_agent.mcp import MCPAgent
 
class PatchedMCPAgent(MCPAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = OllamaChatCompletion(model="deepseek-llm") 