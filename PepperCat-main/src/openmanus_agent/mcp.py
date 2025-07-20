from typing import Any, Dict, List, Optional, Tuple

from pydantic import Field

from src.openmanus_agent.toolcall import ToolCallAgent
from src.openmanus_agent.logger import logger
from src.openmanus_agent.prompt_mcp import MULTIMEDIA_RESPONSE_PROMPT, NEXT_STEP_PROMPT, SYSTEM_PROMPT
from src.openmanus_agent.schema import AgentState, Message
from src.openmanus_agent.tool_base import ToolResult
# from src.openmanus_agent.tool_mcp import MCPClients  # 如需工具链可后续补充

class MCPAgent(ToolCallAgent):
    name: str = "mcp_agent"
    description: str = "An agent that connects to an MCP server and uses its tools."
    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT
    mcp_clients: object = Field(default_factory=object)  # 占位，后续可补全
    available_tools: object = None
    max_steps: int = 20
    connection_type: str = "stdio"
    tool_schemas: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    _refresh_tools_interval: int = 5
    special_tool_names: List[str] = Field(default_factory=lambda: ["terminate"])
    async def initialize(self, *args, **kwargs):
        pass  # 省略实现，后续可补全
    async def _refresh_tools(self):
        pass
    async def think(self) -> bool:
        return await super().think()
    async def _handle_special_tool(self, name: str, result: Any, **kwargs) -> None:
        await super()._handle_special_tool(name, result, **kwargs)
    def _should_finish_execution(self, name: str, **kwargs) -> bool:
        return name.lower() == "terminate"
    async def cleanup(self) -> None:
        pass
    async def run(self, request: Optional[str] = None) -> str:
        return await super().run(request) 