"""Worker执行器"""
import httpx
import sqlite3
from typing import Optional
from ..common.config import settings
from ..common.models import Task


class V2Worker:
    """OpenClaw V2 Worker

    通过HTTP API调用V1 Gateway执行任务
    使用SQLite存储（L3持久化层）以确保可靠性
    """

    def __init__(self):
        self.v1_url = settings.v1_gateway_url
        self.v1_token = settings.v1_gateway_token
        self.v1_agent_id = settings.v1_agent_id
        self.client = httpx.AsyncClient(
            timeout=settings.worker_timeout
        )

        # 初始化SQLite数据库（如果需要）
        self._init_sqlite()

    def _init_sqlite(self):
        """初始化SQLite数据库"""
        try:
            import os
            db_dir = r'C:\Users\10952\.openclaw\workspace\memory'
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'v1_memory.db')

            self.sqlite_conn = sqlite3.connect(
                db_path,
                check_same_thread=False
            )
            # 创建任务表（如果不存在）
            self.sqlite_conn.execute('''
                CREATE TABLE IF NOT EXISTS worker_tasks (
                    task_id TEXT PRIMARY KEY,
                    status TEXT,
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.sqlite_conn.commit()
            print("[Worker] SQLite L3持久化层已初始化 ✅")
        except Exception as e:
            print(f"[Worker] SQLite初始化失败（可选）: {e}")
            self.sqlite_conn = None

    async def execute_task(self, task: Task) -> Task:
        """执行任务（异步调用V1）"""
        try:
            print(f"[Worker] 开始执行任务 {task.id}: {task.content[:50]}...")

            # 更新任务状态为运行中
            task.status = "running"
            task.updated_at = task.updated_at  # 触发更新

            # 构建HTTP请求
            payload = {
                "model": "openclaw",
                "messages": [
                    {"role": "user", "content": task.content}
                ]
            }

            headers = {
                "Authorization": f"Bearer {self.v1_token}",
                "Content-Type": "application/json",
                "x-openclaw-agent-id": self.v1_agent_id
            }

            # 调用V1 Gateway
            response = await self.client.post(
                f"{self.v1_url}/v1/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                task.status = "completed"
                task.result = data["choices"][0]["message"]["content"]
                task.metadata = data.get("usage", {})
                print(f"[Worker] 任务 {task.id} 完成")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            print(f"[Worker] 任务 {task.id} 失败: {e}")

        return task

    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
