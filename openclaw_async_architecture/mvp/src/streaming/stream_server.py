"""
WebSocket流式服务器
实现流式LLM响应
"""
import asyncio
import json
import logging
from typing import AsyncGenerator, Optional
from .connection_manager import ConnectionManager
from .llm_stream import StreamChatService

logger = logging.getLogger(__name__)


class StreamServer:
    """WebSocket流式服务器"""

    def __init__(
        self,
        connection_manager: ConnectionManager = None,
        stream_chat_service: StreamChatService = None,
        default_provider: str = "nvidia2"  # 默认使用nvidia2（更快）
    ):
        """
        初始化流式服务器

        Args:
            connection_manager: 连接管理器（可选）
            stream_chat_service: 流式聊天服务（可选）
            default_provider: 默认API提供商
        """
        self.connection_manager = connection_manager or ConnectionManager()
        self.stream_chat_service = stream_chat_service
        self.default_provider = default_provider

    def set_stream_chat_service(self, stream_chat_service: StreamChatService):
        """
        设置流式聊天服务

        Args:
            stream_chat_service: 流式聊天服务实例
        """
        self.stream_chat_service = stream_chat_service

    async def handle_connection(self, websocket: object, connection_id: str, client_ip: str = "unknown"):
        """
        处理WebSocket连接

        Args:
            websocket: WebSocket对象
            connection_id: 连接ID
            client_ip: 客户端IP
        """
        try:
            # 添加连接
            await self.connection_manager.connect(connection_id, websocket, client_ip)

            # 处理消息
            async for message in self._receive_messages(websocket):
                logger.info(f"收到消息: {message[:100]}...")

                # 解析provider（如果指定）
                try:
                    msg_data = json.loads(message)
                    user_message = msg_data.get("message", message)
                    provider = msg_data.get("provider", self.default_provider)
                except json.JSONDecodeError:
                    user_message = message
                    provider = self.default_provider

                # 处理消息并流式响应
                try:
                    async for chunk in self._stream_response(user_message, provider):
                        await self._send_chunk(websocket, chunk)

                    # 发送完成信号
                    await self._send_done(websocket)

                except Exception as e:
                    logger.error(f"流式响应错误: {e}")
                    await self._send_error(websocket, f"Error: {e}")
                    break

        except Exception as e:
            logger.error(f"连接处理错误: {e}")

        finally:
            # 断开连接
            self.connection_manager.disconnect(connection_id, client_ip)

    async def _receive_messages(self, websocket: object) -> AsyncGenerator[str, None]:
        """
        接收消息

        Args:
            websocket: WebSocket对象

        Yields:
            消息文本
        """
        while True:
            # 接收文本消息
            message = await websocket.receive_text()

            # 检查连接是否关闭
            if message is None:
                break

            yield message

    async def _stream_response(self, message: str, provider: str) -> AsyncGenerator[str, None]:
        """
        流式响应（真实LLM调用）

        Args:
            message: 用户消息
            provider: API提供商

        Yields:
            响应块
        """
        # 检查流式聊天服务
        if not self.stream_chat_service:
            raise RuntimeError("StreamChatService未配置")

        # 构建消息列表
        messages = [{"role": "user", "content": message}]

        # 调用流式LLM
        async for chunk in self.stream_chat_service.stream_chat(provider, messages):
            yield chunk

    async def _send_chunk(self, websocket: object, chunk: str):
        """
        发送响应块

        Args:
            websocket: WebSocket对象
            chunk: 响应块
        """
        # 发送文本
        await websocket.send_text(chunk)

    async def _send_error(self, websocket: object, error: str):
        """
        发送错误消息

        Args:
            websocket: WebSocket对象
            error: 错误消息
        """
        # 发送错误
        await websocket.send_json({
            "type": "error",
            "message": error
        })

    async def _send_done(self, websocket: object):
        """
        发送完成信号

        Args:
            websocket: WebSocket对象
        """
        # 发送完成信号
        await websocket.send_json({
            "type": "done"
        })

    def get_active_connections_count(self) -> int:
        """
        获取活跃连接数

        Returns:
            活跃连接数
        """
        return self.connection_manager.get_active_count()
