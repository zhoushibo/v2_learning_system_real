"""
带缓存的LLM提供者

自动缓存学习结果，避免重复调用API
"""
import logging
from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.base import LLMProvider
from utils.cache import LearningCache

logger = logging.getLogger(__name__)


class CachedLLMProvider:
    """
    带缓存的LLM提供者包装器

    作用：
    1. 自动缓存学习结果
    2. 避免重复调用API
    3. 节省成本
    4. 降低限流风险
    """

    def __init__(self, provider: LLMProvider, cache_file=None):
        """
        初始化带缓存的提供者

        Args:
            provider: 底层LLM提供者
            cache_file: 缓存文件路径
        """
        self.provider = provider
        self.cache = LearningCache(cache_file)

    async def learning(
        self,
        topic: str,
        perspective: str,
        style: str = "deep_analysis"
    ) -> Dict[str, List[str]]:
        """
        学习主题（带缓存）

        Args:
            topic: 学习主题
            perspective: 学习视角
            style: 学习风格

        Returns:
            学习结果字典
        """
        # 尝试从缓存获取
        cached = self.cache.get(topic, perspective, style)

        if cached is not None:
            # 缓存命中，直接返回
            return cached["result"]

        # 缓存未命中，调用LLM
        result = await self.provider.learning(topic, perspective, style)

        # 存入缓存
        self.cache.set(topic, perspective, result, style)

        return result

    async def validate_key(self) -> bool:
        """验证API密钥"""
        return await self.provider.validate_key()

    def get_model(self) -> str:
        """获取模型名称"""
        return self.provider.get_model()

    def get_provider_name(self) -> str:
        """获取提供者名称"""
        return self.provider.get_provider_name()

    def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        return self.cache.get_stats()

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
