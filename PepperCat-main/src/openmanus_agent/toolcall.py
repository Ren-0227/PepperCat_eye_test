import asyncio
import json
from typing import Any, List, Optional, Union

from pydantic import Field

from src.openmanus_agent.react import ReActAgent
from src.openmanus_agent.exceptions import TokenLimitExceeded
from src.openmanus_agent.logger import logger
from src.openmanus_agent.prompt_toolcall import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from src.openmanus_agent.schema import TOOL_CHOICE_TYPE, AgentState, Message, ToolCall, ToolChoice
from src.openmanus_agent.tool_create_chat_completion import CreateChatCompletion
from src.openmanus_agent.tool_terminate import Terminate
from src.openmanus_agent.tool_collection import ToolCollection

TOOL_CALL_REQUIRED = "Tool calls required but none provided"

class ToolCallAgent(ReActAgent):
    name: str = "toolcall"
    description: str = "an agent that can execute tool calls."
    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT
    available_tools: ToolCollection = ToolCollection(
        CreateChatCompletion(), Terminate()
    )
    tool_choices: TOOL_CHOICE_TYPE = ToolChoice.AUTO  # type: ignore
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])
    tool_calls: List[ToolCall] = Field(default_factory=list)
    _current_base64_image: Optional[str] = None
    max_steps: int = 30
    max_observe: Optional[Union[int, bool]] = None
    async def think(self) -> bool:
        return await super().think()
    async def act(self) -> str:
        return await super().act()
    async def execute_tool(self, command: ToolCall) -> str:
        return ""
    async def _handle_special_tool(self, name: str, result: Any, **kwargs):
        pass
    @staticmethod
    def _should_finish_execution(**kwargs) -> bool:
        return True
    def _is_special_tool(self, name: str) -> bool:
        return name.lower() in [n.lower() for n in self.special_tool_names]
    async def cleanup(self):
        pass
    async def run(self, request: Optional[str] = None) -> str:
        return await super().run(request) 