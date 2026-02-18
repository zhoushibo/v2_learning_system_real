"""
HTTP客户端管理模块
提供共享的AsyncClient，实现HTTP连接复用
"""
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class HTTPClientManager:
    """HTTP客户端管理器（单例）"""

    _instance: Optional['HTTPClientManager'] = None
    _shared_client: Optional[httpx.AsyncClient] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_shared_client(self) -> httpx.AsyncClient:
        """
        获取共享HTTP客户端（连接复用）

        Returns:
            共享的AsyncClient实例
        """
        if HTTPClientManager._shared_client is None:
            HTTPClientManager._shared_client = self._create_client()
            logger.info("[HTTPClientManager] 共享HTTP客户端已创建（支持Keep-Alive连接复用）")

        return HTTPClientManager._shared_client

    def _create_client(self) -> httpx.AsyncClient:
        """
        创建优化的HTTP客户端

        特性：
        - HTTP/2（如果可用）：多路复用
        - Keep-Alive：连接复用
        - 合理的连接限制

        注意：如果h2包未安装，自动降级到HTTP/1.1（Keep-Alive仍然有效）
        """
        # 尝试启用HTTP/2，失败时降级到HTTP/1.1
        try:
            client = httpx.AsyncClient(
                timeout=60.0,
                http2=True,  # 启用HTTP/2
                limits=httpx.Limits(
                    max_keepalive_connections=50,  # 最大保持连接数
                    max_connections=100,  # 最大连接数
                    keepalive_expiry=30.0  # Keep-Alive过期时间（秒）
                )
            )
            logger.debug("[HTTPClientManager] HTTP/2已启用")
            return client
        except ImportError:
            # h2包未安装，降级到HTTP/1.1
            logger.warning("[HTTPClientManager] h2包未安装，降级到HTTP/1.1（Keep-Alive仍然有效）")
            return httpx.AsyncClient(
                timeout=60.0,
                http2=False,
                limits=httpx.Limits(
                    max_keepalive_connections=50,
                    max_connections=100,
                    keepalive_expiry=30.0
                )
            )

    async def close(self):
        """关闭共享HTTP客户端"""
        if HTTPClientManager._shared_client:
            await HTTPClientManager._shared_client.aclose()
            HTTPClientManager._shared_client = None
            logger.info("[HTTPClientManager] 共享HTTP客户端已关闭")


# 全局单例实例
_http_client_manager = HTTPClientManager()


def get_shared_client() -> httpx.AsyncClient:
    """
    获取共享HTTP客户端（便捷函数）

    Returns:
        共享的AsyncClient实例
    """
    return _http_client_manager.get_shared_client()


async def close_shared_client():
    """
    关闭共享HTTP客户端（便捷函数）
    """
    await _http_client_manager.close()
