import json
import uuid
from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from openmanus_core.agent.base import BaseAgent
from openmanus_core.logger import logger
from openmanus_core.schema import (
    AgentState,
    Message,
    ToolCall,
    ToolChoice,
    TOOL_CHOICE_TYPE,
)


class ToolCallAgent(BaseAgent):
    """Agent that can call tools and process their results."""

    name: str = "ToolCallAgent"
    description: str = "An agent that can call tools and process their results"

    # Tool-related attributes
    available_tools: List[Dict[str, Any]] = Field(default_factory=list)
    tool_results: List[Dict[str, Any]] = Field(default_factory=list)

    # Prompts
    system_prompt: str = """你是一个智能助手，可以帮助用户完成各种任务。你可以使用可用的工具来完成任务。

可用的工具：
{tools_description}

请根据用户的需求选择合适的工具并执行。如果用户的需求不明确，请询问更多细节。"""

    next_step_prompt: str = """基于当前的情况，请决定下一步行动：

1. 如果任务已完成，请总结结果
2. 如果需要更多信息，请询问用户
3. 如果需要使用工具，请选择合适的工具并执行
4. 如果遇到问题，请说明问题并提供解决方案

请用中文回复。"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tools_description = self._generate_tools_description()

    def _generate_tools_description(self) -> str:
        """生成工具描述"""
        if not self.available_tools:
            return "暂无可用工具"
        
        descriptions = []
        for tool in self.available_tools:
            name = tool.get("name", "未知工具")
            description = tool.get("description", "无描述")
            descriptions.append(f"- {name}: {description}")
        
        return "\n".join(descriptions)

    def add_tool(self, tool: Dict[str, Any]) -> None:
        """添加工具"""
        self.available_tools.append(tool)
        self.tools_description = self._generate_tools_description()

    def add_tools(self, *tools: Dict[str, Any]) -> None:
        """添加多个工具"""
        for tool in tools:
            self.add_tool(tool)

    async def step(self) -> str:
        """执行单个步骤"""
        try:
            # 获取当前消息
            messages = self.memory.get_messages()
            
            # 准备发送给LLM的消息
            llm_messages = []
            
            # 添加系统提示
            if self.system_prompt:
                system_prompt = self.system_prompt.format(
                    tools_description=self.tools_description
                )
                llm_messages.append({"role": "system", "content": system_prompt})
            
            # 添加历史消息
            for msg in messages:
                llm_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # 添加下一步提示
            if self.next_step_prompt:
                llm_messages.append({"role": "user", "content": self.next_step_prompt})
            
            # 准备工具定义
            tools = []
            for tool in self.available_tools:
                tool_def = {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool.get("parameters", {})
                    }
                }
                tools.append(tool_def)
            
            # 调用LLM
            if tools:
                response = await self.llm.ask_tool(
                    messages=llm_messages,
                    tools=tools,
                    tool_choice=ToolChoice.AUTO
                )
            else:
                response = await self.llm.ask(messages=llm_messages)
            
            if response and isinstance(response, dict):
                # 处理工具调用
                if "tool_calls" in response and response["tool_calls"]:
                    return await self._handle_tool_calls(response["tool_calls"])
                else:
                    # 普通回复
                    content = response.get("content", "")
                    self.update_memory("assistant", content)
                    return f"Assistant replied: {content}"
            else:
                # 直接字符串回复
                self.update_memory("assistant", str(response))
                return f"Assistant replied: {response}"
                
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            error_msg = f"执行步骤时出错: {str(e)}"
            self.update_memory("assistant", error_msg)
            return error_msg

    async def _handle_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> str:
        """处理工具调用"""
        results = []
        
        for tool_call in tool_calls:
            try:
                tool_call_id = tool_call.get("id", str(uuid.uuid4()))
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                arguments = function.get("arguments", "{}")
                
                # 解析参数
                try:
                    args = json.loads(arguments) if isinstance(arguments, str) else arguments
                except json.JSONDecodeError:
                    args = {}
                
                # 查找并执行工具
                tool_result = await self._execute_tool(tool_name, args)
                
                # 记录工具调用结果
                self.update_memory("tool", tool_result, tool_call_id=tool_call_id)
                
                results.append(f"Tool {tool_name}: {tool_result}")
                
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                error_result = f"工具执行失败: {str(e)}"
                self.update_memory("tool", error_result, tool_call_id=tool_call.get("id", ""))
                results.append(error_result)
        
        return "; ".join(results)

    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """执行工具"""
        # 查找工具
        tool = None
        for available_tool in self.available_tools:
            if available_tool.get("name") == tool_name:
                tool = available_tool
                break
        
        if not tool:
            return f"工具 {tool_name} 不存在"
        
        # 执行工具
        try:
            if "execute" in tool and callable(tool["execute"]):
                result = await tool["execute"](**args)
                return str(result)
            else:
                return f"工具 {tool_name} 没有可执行的函数"
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return f"工具 {tool_name} 执行失败: {str(e)}"

    def get_tool_results(self) -> List[Dict[str, Any]]:
        """获取工具执行结果"""
        return self.tool_results

    def clear_tool_results(self) -> None:
        """清除工具执行结果"""
        self.tool_results.clear()

    def get_available_tools_info(self) -> List[Dict[str, str]]:
        """获取可用工具信息"""
        return [
            {
                "name": tool.get("name", ""),
                "description": tool.get("description", "")
            }
            for tool in self.available_tools
        ] 