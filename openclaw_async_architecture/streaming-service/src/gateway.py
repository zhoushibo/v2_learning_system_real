"""
流式响应Gateway服务
提供WebSocket端点，实现实时流式LLM对话
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
import uuid
from typing import Optional
import sys
import os

# 添加上级目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "mvp", "src"))

from streaming.stream_server import StreamServer
from streaming.connection_manager import ConnectionManager
from streaming.llm_stream import StreamChatService
from streaming.performance_monitor import PerformanceMonitorContext

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="OpenClaw流式响应Gateway",
    description="实时流式LLM对话服务",
    version="1.0.0"
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
# 加载API配置
import json
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config_path = os.path.join(workspace_root, "API_CONFIG_FINAL.json")
with open(config_path, "r", encoding="utf-8") as f:
    api_config = json.load(f)["api_configs"]

# 创建组件
connection_manager = ConnectionManager(max_connections=1000, max_per_ip=10)
stream_chat_service = StreamChatService(api_config, use_shared_client=True)
stream_server = StreamServer(
    connection_manager=connection_manager,
    stream_chat_service=stream_chat_service,
    default_provider="nvidia2"  # 默认使用nvidia2（更快）
)

# 存储活跃连接的provider配置（可选，允许每个连接使用不同的API）
active_connections_config = {}


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "OpenClaw流式响应Gateway",
        "version": "1.0.0",
        "status": "running",
        "active_connections": connection_manager.get_active_count(),
        "services": {
            "websocket_endpoint": "/ws/stream/{session_id}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "gateway_running": True,
        "active_connections": connection_manager.get_active_count(),
        "api_providers": list(stream_chat_service.api_configs.keys()),
        "default_provider": stream_server.default_provider
    }


@app.get("/stats")
async def stats():
    """统计信息"""
    return {
        "active_connections": connection_manager.get_active_count(),
        "max_connections": connection_manager.max_connections,
        "api_providers_available": list(stream_chat_service.api_configs.keys()),
        "default_provider": stream_server.default_provider
    }


@app.websocket("/ws/stream/{session_id}")
async def websocket_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket流式聊天端点

    消息格式（客户端→服务器）：
    ```json
    {
        "message": "用户消息",
        "provider": "nvidia2"  // 可选，默认为nvidia2
    }
    ```

    输出格式（服务器→客户端）：
    - 文本块：直接发送文本
    - 完成信号：{"type": "done"}
    - 错误消息：{"type": "error", "message": "错误信息"}
    """
    # 接受WebSocket连接
    await websocket.accept()

    # 获取客户端IP
    client_ip = websocket.client.host if websocket.client else "unknown"

    connection_id = f"{session_id}_{uuid.uuid4().hex[:8]}"

    logger.info(f"[Gateway] 新连接: {connection_id} (IP: {client_ip})")

    try:
        # 使用StreamServer处理连接
        await stream_server.handle_connection(websocket, connection_id, client_ip)

    except WebSocketDisconnect:
        logger.info(f"[Gateway] 连接断开: {connection_id}")
    except Exception as e:
        logger.error(f"[Gateway] 连接错误 ({connection_id}): {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Error: {str(e)}"
            })
        except:
            pass

    finally:
        # ConnectionManager会在handle_connection中自动处理断开
        pass


@app.on_event("shutdown")
async def shutdown():
    """关闭时清理资源"""
    logger.info("[Gateway] 正在关闭...")

    # 关闭流式聊天服务（关闭共享HTTP客户端）
    await stream_chat_service.close()

    logger.info("[Gateway] 已关闭")


if __name__ == "__main__":
    import uvicorn
    
    # ⭐ P2 优化：增加超时时间，防止长任务中断
    uvicorn.run(
        app,  # 直接传入 app 对象
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info",
        timeout_keep_alive=300,  # 5 分钟（默认 60 秒）
        ws_ping_interval=30,  # WebSocket 心跳 30 秒
        ws_ping_timeout=30  # WebSocket 心跳超时 30 秒
    )
