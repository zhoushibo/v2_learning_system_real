"""
LLMProvider - LLM提供者抽象基类

所有LLM提供者必须实现此接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """
    LLM提供者抽象基类

    所有具体的LLM提供者（如OpenAI、Claude）都必须继承此类并实现learning方法
    """

    def __init__(self, api_key: str, model: str = None):
        """
        初始化LLM提供者

        Args:
            api_key: API密钥
            model: 模型名称
        """
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def learning(
        self,
        topic: str,
        perspective: str,
        style: str = "deep_analysis"
    ) -> Dict[str, List[str]]:
        """
        学习主题

        Args:
            topic: 学习主题（如：React Hooks）
            perspective: 学习视角（如：架构专家）
            style: 学习风格（如：deep_analysis, quick_overview）

        Returns:
            学习结果字典：
            {
                "lessons": ["课程1", "课程2", ...],
                "key_points": ["要点1", "要点2", ...],
                "recommendations": ["建议1", "建议2", ...]
            }

        Raises:
            APIError: API调用失败
            RateLimitError: 速率限制
            AuthenticationError: 认证失败
        """
        pass

    @abstractmethod
    async def validate_key(self) -> bool:
        """
        验证API密钥是否有效

        Returns:
            密钥是否有效
        """
        pass

    def get_model(self) -> str:
        """
        获取当前模型

        Returns:
            模型名称
        """
        return self.model

    def get_provider_name(self) -> str:
        """
        获取提供者名称

        Returns:
            提供者名称（如：openai, claude）
        """
        return self.__class__.__name__.replace("Provider", "").lower()


class APIError(Exception):
    """API调用错误"""
    pass


class RateLimitError(APIError):
    """速率限制错误"""
    pass


class AuthenticationError(APIError):
    """认证错误"""
    pass


class InvalidResponseError(APIError):
    """响应格式错误"""
    pass
