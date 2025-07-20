from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class BaseTool(ABC, BaseModel):
    name: str
    description: str
    parameters: Optional[dict] = None
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # 允许额外的字段
    
    def __init__(self, **data):
        super().__init__(**data)
        # 初始化后可以添加动态属性
        self._dynamic_attrs = {}
    
    def __setattr__(self, name, value):
        """支持动态属性设置"""
        if name in ['_dynamic_attrs'] or name in self.__fields__:
            super().__setattr__(name, value)
        else:
            if not hasattr(self, '_dynamic_attrs'):
                self._dynamic_attrs = {}
            self._dynamic_attrs[name] = value
    
    def __getattr__(self, name):
        """支持动态属性获取"""
        if hasattr(self, '_dynamic_attrs') and name in self._dynamic_attrs:
            return self._dynamic_attrs[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    async def __call__(self, **kwargs) -> Any:
        return await self.execute(**kwargs)
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass
    
    def to_param(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
class ToolResult(BaseModel):
    output: Any = Field(default=None)
    error: Optional[str] = Field(default=None)
    base64_image: Optional[str] = Field(default=None)
    system: Optional[str] = Field(default=None)
    class Config:
        arbitrary_types_allowed = True
    def __bool__(self):
        return any(getattr(self, field) for field in self.__fields__)
    def __add__(self, other: "ToolResult"):
        def combine_fields(field: Optional[str], other_field: Optional[str], concatenate: bool = True):
            if field and other_field:
                if concatenate:
                    return field + other_field
                raise ValueError("Cannot combine tool results")
            return field or other_field
        return ToolResult(
            output=combine_fields(self.output, other.output),
            error=combine_fields(self.error, other.error),
            base64_image=combine_fields(self.base64_image, other.base64_image, False),
            system=combine_fields(self.system, other.system),
        )
    def __str__(self):
        return f"Error: {self.error}" if self.error else self.output
    def replace(self, **kwargs):
        return type(self)(**{**self.dict(), **kwargs})
class CLIResult(ToolResult):
    pass
class ToolFailure(ToolResult):
    pass 