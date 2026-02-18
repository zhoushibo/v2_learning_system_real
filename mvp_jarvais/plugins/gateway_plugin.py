"""
MVP JARVIS - Gateway 集成插件
提供与 Gateway 流式服务的连接
"""
import asyncio
import websockets
import json
import logging
from typing import Optional, AsyncGenerator

logger = logging.getLogger(__name__)


class GatewayPlugin:
    """
    Gateway 流式对话插件
    连接到 Gateway WebSocket 服务，实现流式对话
    """
    
    def __init__(self, gateway_url: str = "ws://127.0.0.1:8001"):
        """
        初始化 Gateway 插件
        
        Args:
            gateway_url: Gateway WebSocket 地址
        """
        self.gateway_url = gateway_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.session_id: Optional[str] = None
        self.connected = False
    
    async def connect(self, session_id: str = "default") -> bool:
        """
        连接到 Gateway
        
        Args:
            session_id: 会话 ID
        
        Returns:
            是否连接成功
        """
        try:
            self.session_id = session_id
            ws_url = f"{self.gateway_url}/ws/stream/{session_id}"
            
            logger.info(f"正在连接到 Gateway: {ws_url}")
            self.websocket = await websockets.connect(ws_url)
            self.connected = True
            
            logger.info("✅ Gateway 连接成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ Gateway 连接失败：{e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """断开 Gateway 连接"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.connected = False
            logger.info("Gateway 已断开")
    
    async def send_message(self, message: str, provider: str = "nvidia2") -> AsyncGenerator[str, None]:
        """
        发送消息并接收流式响应
        
        Args:
            message: 用户消息
            provider: API 提供者（默认：nvidia2）
        
        Yields:
            流式响应文本块
        """
        if not self.connected or not self.websocket:
            raise ConnectionError("未连接到 Gateway")
        
        # 发送消息
        payload = {
            "message": message,
            "provider": provider
        }
        
        logger.info(f"发送消息：{message[:50]}...")
        await self.websocket.send(json.dumps(payload))
        
        # 接收流式响应
        try:
            async for response in self.websocket:
                # 解析响应
                if response.startswith('{'):
                    data = json.loads(response)
                    
                    # 完成信号
                    if data.get('type') == 'done':
                        logger.info("流式响应完成")
                        break
                    
                    # 错误信号
                    elif data.get('type') == 'error':
                        error_msg = data.get('message', '未知错误')
                        logger.error(f"Gateway 错误：{error_msg}")
                        raise Exception(f"Gateway 错误：{error_msg}")
                else:
                    # 文本块
                    yield response
                    
        except websockets.exceptions.ConnectionClosed:
            logger.error("Gateway 连接意外关闭")
            self.connected = False
            raise
    
    async def chat(self, message: str, provider: str = "nvidia2") -> str:
        """
        发送消息并收集完整响应
        
        Args:
            message: 用户消息
            provider: API 提供者
        
        Returns:
            完整响应文本
        """
        full_response = ""
        
        async for chunk in self.send_message(message, provider):
            full_response += chunk
        
        return full_response
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            Gateway 是否可用
        """
        try:
            # 尝试连接到一个临时会话
            test_session = f"health_check_{id(self)}"
            connected = await self.connect(test_session)
            
            if connected:
                await self.disconnect()
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"健康检查失败：{e}")
            return False


async def main():
    """测试 Gateway 插件"""
    print("=" * 80)
    print("🧪 Gateway 插件测试")
    print("=" * 80)
    
    plugin = GatewayPlugin()
    
    # 测试 1：健康检查
    print("\n1️⃣ 健康检查...")
    healthy = await plugin.health_check()
    print(f"   Gateway 状态：{'✅ 可用' if healthy else '❌ 不可用'}")
    
    if not healthy:
        print("\n⚠️ Gateway 未运行，跳过后续测试")
        print("💡 提示：启动 Gateway 服务：python openclaw_async_architecture/streaming-service/src/gateway.py")
        return
    
    # 测试 2：连接
    print("\n2️⃣ 连接到 Gateway...")
    connected = await plugin.connect("test_session")
    print(f"   连接状态：{'✅ 成功' if connected else '❌ 失败'}")
    
    if not connected:
        return
    
    # 测试 3：发送消息
    print("\n3️⃣ 发送测试消息...")
    try:
        response = await plugin.chat("你好，请用一句话介绍你自己")
        print(f"   响应：{response[:100]}...")
        print("   ✅ 消息发送成功")
    except Exception as e:
        print(f"   ❌ 消息发送失败：{e}")
    
    # 断开连接
    await plugin.disconnect()
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
