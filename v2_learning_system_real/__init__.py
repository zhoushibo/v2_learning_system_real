"""V2 学习系统 - 包初始化"""

from .learning_engine import (
    LearningEngine,
    LearningTask
)

from .llm import (
    LLMProvider,
    OpenAIProvider,
    HTTPProvider,
    APIError
)

__all__ = [
    "LearningEngine",
    "LearningTask",
    "LLMProvider",
    "OpenAIProvider",
    "HTTPProvider",
    "APIError"
]
