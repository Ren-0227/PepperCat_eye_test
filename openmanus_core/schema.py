from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class AgentState(str, Enum):
    """Agent execution states"""
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"


class ROLE_TYPE(str, Enum):
    """Message role types"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class TOOL_CHOICE_TYPE(str, Enum):
    """Tool choice types"""
    AUTO = "auto"
    NONE = "none"
    REQUIRED = "required"


TOOL_CHOICE_VALUES = Literal["auto", "none", "required"]


class ToolChoice(str, Enum):
    """Tool choice enumeration"""
    AUTO = "auto"
    NONE = "none"
    REQUIRED = "required"


ROLE_VALUES = Literal["user", "assistant", "system", "tool"]


class Message(BaseModel):
    """Message model for agent communication"""
    role: ROLE_VALUES
    content: Optional[str] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    base64_image: Optional[str] = None

    @classmethod
    def user_message(cls, content: str, base64_image: Optional[str] = None) -> "Message":
        """Create a user message"""
        return cls(role="user", content=content, base64_image=base64_image)

    @classmethod
    def assistant_message(cls, content: str) -> "Message":
        """Create an assistant message"""
        return cls(role="assistant", content=content)

    @classmethod
    def system_message(cls, content: str) -> "Message":
        """Create a system message"""
        return cls(role="system", content=content)

    @classmethod
    def tool_message(cls, content: str, tool_call_id: str) -> "Message":
        """Create a tool message"""
        return cls(role="tool", content=content, tool_call_id=tool_call_id)


class Memory(BaseModel):
    """Agent memory for storing conversation history"""
    messages: List[Message] = Field(default_factory=list)

    def add_message(self, message: Message) -> None:
        """Add a message to memory"""
        self.messages.append(message)

    def get_messages(self) -> List[Message]:
        """Get all messages from memory"""
        return self.messages

    def clear(self) -> None:
        """Clear all messages from memory"""
        self.messages.clear()

    def get_last_message(self) -> Optional[Message]:
        """Get the last message from memory"""
        return self.messages[-1] if self.messages else None

    def get_user_messages(self) -> List[Message]:
        """Get all user messages from memory"""
        return [msg for msg in self.messages if msg.role == "user"]

    def get_assistant_messages(self) -> List[Message]:
        """Get all assistant messages from memory"""
        return [msg for msg in self.messages if msg.role == "assistant"]

    def get_system_messages(self) -> List[Message]:
        """Get all system messages from memory"""
        return [msg for msg in self.messages if msg.role == "system"]

    def get_tool_messages(self) -> List[Message]:
        """Get all tool messages from memory"""
        return [msg for msg in self.messages if msg.role == "tool"]


class ToolCall(BaseModel):
    """Tool call model"""
    id: str
    type: str = "function"
    function: Dict[str, Any]


class ToolResult(BaseModel):
    """Tool execution result"""
    tool_call_id: str
    content: str
    status: str = "success"
    error: Optional[str] = None


class AgentResponse(BaseModel):
    """Agent response model"""
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    status: str = "success"
    error: Optional[str] = None


class ToolDefinition(BaseModel):
    """Tool definition model"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: Optional[List[str]] = None


class AgentConfig(BaseModel):
    """Agent configuration model"""
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    max_steps: int = 10
    temperature: float = 0.7
    max_tokens: int = 4096
    tools: Optional[List[ToolDefinition]] = None


class ConversationTurn(BaseModel):
    """Single conversation turn"""
    user_input: str
    agent_response: AgentResponse
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationHistory(BaseModel):
    """Conversation history model"""
    turns: List[ConversationTurn] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None

    def add_turn(self, turn: ConversationTurn) -> None:
        """Add a conversation turn"""
        self.turns.append(turn)

    def get_last_turn(self) -> Optional[ConversationTurn]:
        """Get the last conversation turn"""
        return self.turns[-1] if self.turns else None

    def clear(self) -> None:
        """Clear conversation history"""
        self.turns.clear()


class ExecutionContext(BaseModel):
    """Execution context for agents"""
    agent_id: str
    session_id: str
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    conversation_history: ConversationHistory = Field(default_factory=ConversationHistory)


class ToolExecutionRequest(BaseModel):
    """Tool execution request"""
    tool_name: str
    parameters: Dict[str, Any]
    context: Optional[ExecutionContext] = None


class ToolExecutionResponse(BaseModel):
    """Tool execution response"""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentExecutionRequest(BaseModel):
    """Agent execution request"""
    user_input: str
    context: Optional[ExecutionContext] = None
    config: Optional[AgentConfig] = None


class AgentExecutionResponse(BaseModel):
    """Agent execution response"""
    success: bool
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 