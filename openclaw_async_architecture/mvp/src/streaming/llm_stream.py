"""
LLM流式调用模块
支持多个API提供商的流式响应
"""
import httpx
import json
import logging
from typing import AsyncGenerator, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# 避免循环导入
if TYPE_CHECKING:
    from .performance_monitor import PerformanceMonitorContext


class BaseLLMStreamer(ABC):
    """LLM流式调用基类"""

    def __init__(self, api_url: str, api_key: str, model: str, use_shared_client: bool = True):
        """
        初始化流式调用器

        Args:
            api_url: API URL
            api_key: API Key
            model: 模型名称
            use_shared_client: 是否使用共享HTTP客户端（默认True）
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.use_shared_client = use_shared_client

        # 延迟加载客户端（避免导入时初始化）
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """获取HTTP客户端（延迟加载）"""
        if self._client is None:
            if self.use_shared_client:
                from .http_client import get_shared_client
                self._client = get_shared_client()
            else:
                self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    @abstractmethod
    async def stream_chat(self, messages: list, monitor: 'PerformanceMonitorContext' = None) -> AsyncGenerator[str, None]:
        """
        流式聊天

        Args:
            messages: 消息列表
            monitor: 性能监控上下文（可选）

        Yields:
            响应块（文本）
        """
        pass

    async def close(self):
        """
        关闭HTTP客户端

        注意：如果是共享客户端，不会关闭（由管理器统一关闭）
        """
        if not self.use_shared_client and self._client:
            await self._client.aclose()
            self._client = None


class OpenAIStreamer(BaseLLMStreamer):
    """OpenAI风格流式调用（NVIDIA, 混元等）"""

    async def stream_chat(self, messages: list, monitor: 'PerformanceMonitorContext' = None) -> AsyncGenerator[str, None]:
        """
        OpenAI格式流式调用

        Args:
            messages: 消息列表
            monitor: 性能监控上下文（可选）

        Yields:
            响应块（文本）
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True  # 启用流式
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with self.client.stream(
                "POST",
                self.api_url,
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()

                # 逐行解析SSE格式
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue

                    data = line[6:]  # 去掉 "data: " 前缀

                    # 检查结束标记
                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                        # 提取 delta.content
                        choices = chunk.get("choices", [])
                        if not choices:  # 处理空choices（结束chunk）
                            continue

                        delta = choices[0].get("delta", {})
                        content = delta.get("content", "")

                        if content:
                            # 记录性能
                            if monitor:
                                monitor.record_chunk(content)

                            yield content

                    except json.JSONDecodeError as e:
                        logger.warning(f"解析chunk失败: {e}")
                        continue

        except httpx.HTTPError as e:
            logger.error(f"流式调用HTTP错误: {e}")
            raise
        except Exception as e:
            logger.error(f"流式调用错误: {e}")
            raise


class ZhipuStreamer(BaseLLMStreamer):
    """智谱GLM流式调用"""

    async def stream_chat(self, messages: list, monitor: 'PerformanceMonitorContext' = None) -> AsyncGenerator[str, None]:
        """
        智谱格式流式调用（incremental=True）

        Args:
            messages: 消息列表
            monitor: 性能监控上下文（可选）

        Yields:
            响应块（文本）
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True  # 智谱也支持stream
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with self.client.stream(
                "POST",
                self.api_url,
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue

                    data = line[6:]

                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                        # 智谱的delta格式
                        choices = chunk.get("choices", [])
                        if not choices:
                            continue

                        delta = choices[0].get("delta", {})
                        content = delta.get("content", "")

                        if content:
                            # 记录性能
                            if monitor:
                                monitor.record_chunk(content)

                            yield content

                    except json.JSONDecodeError as e:
                        logger.warning(f"解析chunk失败: {e}")
                        continue

        except httpx.HTTPError as e:
            logger.error(f"智谱流式调用HTTP错误: {e}")
            raise
        except Exception as e:
            logger.error(f"智谱流式调用错误: {e}")
            raise


def create_streamer(
    provider: str,
    api_url: str,
    api_key: str,
    model: str,
    use_shared_client: bool = True
) -> BaseLLMStreamer:
    """
    创建流式调用器工厂函数

    Args:
        provider: API提供商（nvidia, zhipu, tencent等）
        api_url: API URL
        api_key: API Key
        model: 模型名称
        use_shared_client: 是否使用共享HTTP客户端

    Returns:
        流式调用器实例
    """
    streamer_map = {
        "nvidia": OpenAIStreamer,
        "tencent": OpenAIStreamer,  # 混元也是OpenAI格式
        "zhipu": ZhipuStreamer,
    }

    streamer_class = streamer_map.get(provider, OpenAIStreamer)
    return streamer_class(api_url, api_key, model, use_shared_client)


class StreamChatService:
    """流式聊天服务（封装多模型）"""

    def __init__(self, api_configs: dict, use_shared_client: bool = True):
        """
        初始化流式聊天服务

        Args:
            api_configs: API配置字典
            use_shared_client: 是否使用共享HTTP客户端
        """
        self.api_configs = api_configs
        self.use_shared_client = use_shared_client
        self.active_streamers: dict[str, BaseLLMStreamer] = {}

    async def stream_chat(
        self,
        provider: str,
        messages: list,
        enable_monitor: bool = True,
        is_first_call: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天

        Args:
            provider: API提供商
            messages: 消息列表
            enable_monitor: 是否启用性能监控
            is_first_call: 是否首次调用（冷启动）

        Yields:
            响应块（文本）
        """
        config = self.api_configs.get(provider)
        if not config:
            raise ValueError(f"未找到provider配置: {provider}")

        # 创建性能监控上下文
        from .performance_monitor import PerformanceMonitorContext
        monitor = None
        if enable_monitor:
            monitor = PerformanceMonitorContext(provider, is_first_call)

        try:
            if monitor:
                monitor.__enter__()

            # 创建或获取流式调用器
            if provider not in self.active_streamers:
                self.active_streamers[provider] = create_streamer(
                    provider=provider,
                    api_url=config["url"],
                    api_key=config["api_key"],
                    model=config["model"],
                    use_shared_client=self.use_shared_client
                )

            streamer = self.active_streamers[provider]

            # 流式调用（传入monitor）
            async for chunk in streamer.stream_chat(messages, monitor):
                yield chunk

        except Exception as e:
            logger.error(f"流式聊天失败 ({provider}): {e}")
            raise
        finally:
            if monitor:
                monitor.__exit__(None, None, None)

    async def close(self):
        """关闭所有流式调用器"""
        for streamer in self.active_streamers.values():
            await streamer.close()
        self.active_streamers.clear()

        # 关闭共享客户端
        if self.use_shared_client:
            from .http_client import close_shared_client
            await close_shared_client()
