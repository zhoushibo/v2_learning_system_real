"""
流式响应Gateway启动脚本
"""
import uvicorn
import sys
import os

# 确保可以导入gateway模块
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

if __name__ == "__main__":
    import gateway

    print("\n" + "=" * 60)
    print("OpenClaw流式响应Gateway")
    print("=" * 60 + "\n")

    print("配置:")
    print(f"  主机: 0.0.0.0")
    print(f"  端口: 8001")
    print(f"  WebSocket: ws://0.0.0.0:8001/ws/stream/{{session_id}}")
    print(f"  健康检查: http://0.0.0.0:8001/health")
    print()

    print("=" * 60 + "\n")

    # 启动服务
    uvicorn.run(
        "gateway:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
