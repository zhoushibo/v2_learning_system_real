"""工具基类定义

所有Worker工具必须继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """工具输入格式（基类）"""
    pass


class ToolOutput(BaseModel):
    """工具输出格式（统一格式）"""
    success: bool = Field(..., description="是否成功")
    data: Optional[Any] = Field(None, description="输出数据（成功时）")
    error: Optional[str] = Field(None, description="错误信息（失败时）")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="元数据（调试信息、耗时等）"
    )


class BaseTool(ABC):
    """工具基类

    所有Worker工具必须继承此类

    核心特性：
    - 统一的输入/输出格式
    - 内置输入验证
    - 内置异常处理
    - 元数据支持
    """

    # 工具名称（必须唯一）
    name: str

    # 工具描述（告诉LLM这个工具做什么）
    description: str

    # 输入Schema（Pydantic模型）
    input_schema: ToolInput

    @abstractmethod
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """
        执行工具

        Args:
            input_data: 输入数据（必须是ToolInput或其子类）

        Returns:
            ToolOutput: 输出结果
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据

        Args:
            input_data: 输入数据（字典格式）

        Returns:
            bool: 是否验证通过
        """
        pass

    def get_tool_info(self) -> Dict[str, str]:
        """
        获取工具信息

        Returns:
            dict: 工具名称和描述
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema.schema()
        }
