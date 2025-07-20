import math
import json
import asyncio
from typing import Dict, List, Optional, Union
import aiohttp
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from openmanus_core.config import LLMSettings, config
from openmanus_core.logger import logger
from openmanus_core.schema import (
    ROLE_VALUES,
    TOOL_CHOICE_TYPE,
    TOOL_CHOICE_VALUES,
    Message,
    ToolChoice,
)


class LLM:
    _instances: Dict[str, "LLM"] = {}

    def __new__(
        cls, config_name: str = "default", llm_config: Optional[LLMSettings] = None
    ):
        if config_name not in cls._instances:
            instance = super().__new__(cls)
            instance.__init__(config_name, llm_config)
            cls._instances[config_name] = instance
        return cls._instances[config_name]

    def __init__(
        self, config_name: str = "default", llm_config: Optional[LLMSettings] = None
    ):
        if not hasattr(self, "client"):  # Only initialize if not already initialized
            llm_config = llm_config or config.llm
            llm_config = llm_config.get(config_name, llm_config["default"])
            self.model = llm_config.model
            self.max_tokens = llm_config.max_tokens
            self.temperature = llm_config.temperature
            self.api_type = llm_config.api_type
            self.api_key = llm_config.api_key
            self.api_version = llm_config.api_version
            self.base_url = llm_config.base_url
            
            # Token counting
            self.input_tokens = 0
            self.completion_tokens = 0
            self.total_tokens = 0

    def count_tokens(self, text: str) -> int:
        """简单的token计数（近似）"""
        # 对于中文，大约1个token = 1.5个字符
        # 对于英文，大约1个token = 4个字符
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        english_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + english_chars / 4)

    def count_message_tokens(self, messages: List[dict]) -> int:
        """计算消息列表的token数量"""
        total_tokens = 0
        for message in messages:
            if "content" in message and message["content"]:
                total_tokens += self.count_tokens(message["content"])
        return total_tokens

    def update_token_count(self, input_tokens: int, completion_tokens: int = 0) -> None:
        """更新token计数"""
        self.input_tokens += input_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens = self.input_tokens + self.completion_tokens

    def check_token_limit(self, input_tokens: int) -> bool:
        """检查是否超过token限制"""
        return input_tokens <= self.max_tokens

    def get_limit_error_message(self, input_tokens: int) -> str:
        """获取token限制错误消息"""
        return f"Token limit exceeded: {input_tokens} > {self.max_tokens}"

    @staticmethod
    def format_messages(
        messages: List[Union[dict, Message]], supports_images: bool = False
    ) -> List[dict]:
        """格式化消息列表"""
        formatted_messages = []
        
        for message in messages:
            if isinstance(message, Message):
                msg_dict = {
                    "role": message.role,
                    "content": message.content
                }
                if message.name:
                    msg_dict["name"] = message.name
                if message.tool_call_id:
                    msg_dict["tool_call_id"] = message.tool_call_id
                if message.tool_calls:
                    msg_dict["tool_calls"] = message.tool_calls
                if message.base64_image and supports_images:
                    msg_dict["content"] = [
                        {"type": "text", "text": message.content or ""},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{message.base64_image}"}}
                    ]
                formatted_messages.append(msg_dict)
            else:
                formatted_messages.append(message)
        
        return formatted_messages

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((Exception,)),
    )
    async def ask(
        self,
        messages: List[Union[dict, Message]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
    ) -> str:
        """发送请求到LLM"""
        try:
            # 格式化消息
            formatted_messages = self.format_messages(messages)
            
            # 添加系统消息
            if system_msgs:
                system_formatted = self.format_messages(system_msgs)
                formatted_messages = system_formatted + formatted_messages
            
            # 计算token
            input_tokens = self.count_message_tokens(formatted_messages)
            if not self.check_token_limit(input_tokens):
                raise ValueError(self.get_limit_error_message(input_tokens))
            
            # 准备请求数据
            request_data = {
                "model": self.model,
                "messages": formatted_messages,
                "max_tokens": self.max_tokens,
                "temperature": temperature or self.temperature,
                "stream": stream
            }
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API request failed: {response.status} - {error_text}")
                        raise Exception(f"API request failed: {response.status}")
                    
                    if stream:
                        return await self._handle_stream_response(response)
                    else:
                        return await self._handle_normal_response(response, input_tokens)
                        
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise

    async def _handle_normal_response(self, response, input_tokens: int) -> str:
        """处理正常响应"""
        response_data = await response.json()
        
        if "choices" not in response_data or not response_data["choices"]:
            raise Exception("Invalid response format")
        
        content = response_data["choices"][0]["message"]["content"]
        completion_tokens = response_data.get("usage", {}).get("completion_tokens", 0)
        
        # 更新token计数
        self.update_token_count(input_tokens, completion_tokens)
        
        return content

    async def _handle_stream_response(self, response) -> str:
        """处理流式响应"""
        content = ""
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                data = line[6:]
                if data == '[DONE]':
                    break
                try:
                    json_data = json.loads(data)
                    if "choices" in json_data and json_data["choices"]:
                        delta = json_data["choices"][0].get("delta", {})
                        if "content" in delta:
                            content += delta["content"]
                except json.JSONDecodeError:
                    continue
        
        return content

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((Exception,)),
    )
    async def ask_with_images(
        self,
        messages: List[Union[dict, Message]],
        images: List[Union[str, dict]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
    ) -> str:
        """发送包含图片的请求到LLM"""
        # 对于本地模型，可能不支持图片，这里简化处理
        return await self.ask(messages, system_msgs, stream, temperature)

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((Exception,)),
    )
    async def ask_tool(
        self,
        messages: List[Union[dict, Message]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        timeout: int = 300,
        tools: Optional[List[dict]] = None,
        tool_choice: TOOL_CHOICE_TYPE = ToolChoice.AUTO,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> Optional[dict]:
        """发送工具调用请求到LLM"""
        try:
            # 格式化消息
            formatted_messages = self.format_messages(messages)
            
            # 添加系统消息
            if system_msgs:
                system_formatted = self.format_messages(system_msgs)
                formatted_messages = system_formatted + formatted_messages
            
            # 计算token
            input_tokens = self.count_message_tokens(formatted_messages)
            if not self.check_token_limit(input_tokens):
                raise ValueError(self.get_limit_error_message(input_tokens))
            
            # 准备请求数据
            request_data = {
                "model": self.model,
                "messages": formatted_messages,
                "max_tokens": self.max_tokens,
                "temperature": temperature or self.temperature,
                "stream": False
            }
            
            # 添加工具相关参数
            if tools:
                request_data["tools"] = tools
                request_data["tool_choice"] = tool_choice
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Tool API request failed: {response.status} - {error_text}")
                        raise Exception(f"Tool API request failed: {response.status}")
                    
                    response_data = await response.json()
                    
                    if "choices" not in response_data or not response_data["choices"]:
                        raise Exception("Invalid response format")
                    
                    choice = response_data["choices"][0]
                    message = choice["message"]
                    
                    completion_tokens = response_data.get("usage", {}).get("completion_tokens", 0)
                    self.update_token_count(input_tokens, completion_tokens)
                    
                    return message
                    
        except Exception as e:
            logger.error(f"Tool LLM request failed: {e}")
            raise

    def get_token_usage(self) -> Dict[str, int]:
        """获取token使用情况"""
        return {
            "input_tokens": self.input_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }

    def reset_token_count(self):
        """重置token计数"""
        self.input_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0 