"""
流式响应系统基础测试
测试ConnectionManager和StreamServer
"""
import pytest
import asyncio
from src.streaming.connection_manager import ConnectionManager
from src.streaming.stream_server import StreamServer


class MockWebSocket:
    """模拟WebSocket"""

    def __init__(self):
        self.messages = []
        self.closed = False

    async def send_text(self, message: str):
        """发送文本"""
        self.messages.append(message)
        await asyncio.sleep(0)

    async def send_json(self, data: dict):
        """发送JSON"""
        self.messages.append(data)
        await asyncio.sleep(0)

    async def receive_text(self):
        """接收文本"""
        await asyncio.sleep(0.1)
        if not self.messages:
            raise ConnectionError("Closed")
        return self.messages.pop(0)


class TestConnectionManager:
    """ConnectionManager测试"""

    @pytest.mark.asyncio
    async def test_connect(self):
        """测试连接"""
        manager = ConnectionManager()
        ws = MockWebSocket()

        # 添加连接
        await manager.connect("conn1", ws, "127.0.0.1")

        assert manager.is_connected("conn1")
        assert manager.get_active_count() == 1

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """测试断开连接"""
        manager = ConnectionManager()
        ws = MockWebSocket()

        # 添加连接
        await manager.connect("conn1", ws, "127.0.0.1")
        assert manager.is_connected("conn1")

        # 断开连接
        manager.disconnect("conn1", "127.0.0.1")
        assert not manager.is_connected("conn1")

    @pytest.mark.asyncio
    async def test_max_connections(self):
        """测试最大连接数限制"""
        manager = ConnectionManager(max_connections=2)

        ws1 = MockWebSocket()
        ws2 = MockWebSocket()
        ws3 = MockWebSocket()

        # 添加2个连接
        await manager.connect("conn1", ws1, "127.0.0.1")
        await manager.connect("conn2", ws2, "127.0.0.1")

        assert manager.get_active_count() == 2

        # 第3个连接应该失败
        with pytest.raises(ConnectionError):
            await manager.connect("conn3", ws3, "127.0.0.1")

    @pytest.mark.asyncio
    async def test_max_per_ip(self):
        """测试单IP连接数限制"""
        manager = ConnectionManager(max_per_ip=2)

        ws1 = MockWebSocket()
        ws2 = MockWebSocket()
        ws3 = MockWebSocket()

        # 从同一IP添加2个连接
        await manager.connect("conn1", ws1, "192.168.1.1")
        await manager.connect("conn2", ws2, "192.168.1.1")

        # 第3个连接应该失败
        with pytest.raises(ConnectionError):
            await manager.connect("conn3", ws3, "192.168.1.1")

        # 不同IP应该可以
        await manager.connect("conn3", ws3, "192.168.1.2")
        assert manager.get_active_count() == 3


class TestStreamServer:
    """StreamServer测试"""

    @pytest.mark.asyncio
    async def test_stream_response(self):
        """测试流式响应"""
        server = StreamServer()

        # 模拟流式输出
        chunks = []
        async for chunk in server._stream_response("测试消息"):
            chunks.append(chunk)

        # 检查是否逐字符输出
        assert len(chunks) > 0
        assert chunks[0] == "你"
        assert "测试消息" in "".join(chunks)

    @pytest.mark.asyncio
    async def test_send_chunk(self):
        """测试发送响应块"""
        server = StreamServer()
        ws = MockWebSocket()

        # 发送块
        await server._send_chunk(ws, "Hello")

        # 检查消息
        assert len(ws.messages) == 1
        assert ws.messages[0] == "Hello"

    @pytest.mark.asyncio
    async def test_send_error(self):
        """测试发送错误"""
        server = StreamServer()
        ws = MockWebSocket()

        # 发送错误
        await server._send_error(ws, "Test error")

        # 检查消息
        assert len(ws.messages) == 1
        assert ws.messages[0]["type"] == "error"
        assert ws.messages[0]["message"] == "Test error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
