"""Gateway - FastAPI应用"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import requests

from ..common.models import TaskRequest, TaskResponse, HealthResponse
from ..queue.redis_queue import RedisTaskQueue
from ..store.hybrid_store import HybridTaskStore  # 使用混合存储
from ..common.models import Task


# 创建FastAPI应用
app = FastAPI(
    title="OpenClaw V2 Gateway",
    description="异步任务处理网关（SQLite + Redis混合存储）",
    version="0.1.0"
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件（使用V1兼容的混合存储）
queue = RedisTaskQueue()
store = HybridTaskStore()  # 三层存储：SQLite + Redis


@app.get("/health")
async def health():
    """健康检查（检查三层存储）"""
    # 队列连接
    redis_queue_ok = queue.test_connection()

    # 存储连接（SQLite + Redis）
    storage_status = store.test_connection()

    return {
        "status": "ok",
        "gateway_running": True,
        "components": {
            "redis_queue": redis_queue_ok,
            "redis_cache": storage_status['redis_connected'],
            "sqlite_persistence": storage_status['sqlite_connected'],
            "storage_mode": storage_status['storage_mode']
        },
        "v1_compatible": True
    }


@app.post("/tasks", response_model=TaskResponse)
async def submit_task(request: TaskRequest):
    """提交任务

    立即返回task_id，不等待执行完成（<50ms）
    """
    # 创建任务
    task = Task(content=request.content, status="pending")

    # 保存到存储
    store.save_task(task)

    # 提交到队列
    success = queue.submit(task.id, task.content)

    if not success:
        raise HTTPException(status_code=500, detail="提交任务失败")

    print(f"[Gateway] 收到任务 {task.id}: {task.content[:50]}...")

    # ⚡ 立即返回，不等待执行
    return TaskResponse(
        task_id=task.id,
        status="pending",
        message="任务已提交，正在处理中"
    )


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务状态和结果"""
    task = store.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "task_id": task.id,
        "status": task.status,
        "content": task.content,
        "result": task.result,
        "error": task.error,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "metadata": task.metadata
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "OpenClaw V2 Gateway",
        "version": "0.1.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
