"""增强版V2 Worker - 集成Gateway流式 + 自主exec"""
import httpx
import sqlite3
import asyncio
import sys
from pathlib import Path
from typing import Optional

# 添加路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入配置
try:
    from ..common.config import settings
except ImportError:
    # 直接导入
    from common.config import settings

# 导入Task
try:
    from ..common.models import Task
except ImportError:
    # 直接导入
    from common.models import Task

# 导入自主exec工具（本地路径）
from tools.exec_self import execute


class EnhancedV2Worker:
    """增强版V2 Worker

    功能整合：
    - ✅ Gateway流式LLM调用
    - ✅ 自主exec工具
    - ✅ SQLite持久化
    - ✅ 任务队列支持
    """

    def __init__(self, worker_id: str = "worker-1"):
        self.worker_id = worker_id

        # V1 Gateway配置
        self.v1_url = settings.v1_gateway_url
        self.v1_token = settings.v1_gateway_token
        self.v1_agent_id = settings.v1_agent_id

        # Gateway流式配置
        self.gateway_url = "ws://127.0.0.1:8001"

        # HTTP客户端（用于V1 API调用）
        self.client = httpx.AsyncClient(timeout=settings.worker_timeout)

        # 初始化SQLite
        self._init_sqlite()

    def _init_sqlite(self):
        """初始化SQLite数据库"""
        try:
            import os
            db_dir = r'C:\Users\10952\.openclaw\workspace\memory'
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'v2_worker_tasks.db')

            self.sqlite_conn = sqlite3.connect(
                db_path,
                check_same_thread=False
            )
            # 创建任务表（如果不存在）
            self.sqlite_conn.execute('''
                CREATE TABLE IF NOT EXISTS worker_tasks (
                    task_id TEXT PRIMARY KEY,
                    worker_id TEXT,
                    task_type TEXT,
                    status TEXT,
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            self.sqlite_conn.commit()
            print(f"[Worker {self.worker_id}] SQLite持久化层已初始化 ✅")
        except Exception as e:
            print(f"[Worker {self.worker_id}] SQLite初始化失败: {e}")
            self.sqlite_conn = None

    async def execute_task(self, task: Task) -> Task:
        """
        执行任务（自动路由到合适的执行器）

        任务类型：
        - chat: 使用Gateway流式LLM
        - command: 使用自主exec工具
        - v1: 使用V1 API（默认）
        """
        try:
            print(f"[Worker {self.worker_id}] 开始执行任务 {task.id}: {task.content[:50]}...")

            # 更新状态
            task.status = "running"
            task.updated_at = task.updated_at

            # 判断任务类型
            task_type = task.metadata.get("task_type", "v1") if task.metadata else "v1"

            # 路由到执行器
            if task_type == "chat":
                # 使用Gateway流式
                result = await self._execute_via_gateway(task)
            elif task_type == "command":
                # 使用自主exec
                result = await self._execute_via_self_exec(task)
            else:
                # 使用V1 API
                result = await self._execute_via_v1(task)

            task.status = "completed"
            task.result = result
            print(f"[Worker {self.worker_id}] 任务 {task.id} 完成")

        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            print(f"[Worker {self.worker_id}] 任务 {task.id} 失败: {e}")

        return task

    async def _execute_via_gateway(self, task: Task) -> str:
        """使用Gateway流式执行LLM任务"""
        try:
            import websockets
            import json

            # 选择provider
            provider = task.metadata.get("provider", "hunyuan") if task.metadata else "hunyuan"
            session_id = task.id

            uri = f"{self.gateway_url}/ws/stream/{session_id}"

            async with websockets.connect(uri) as websocket:
                # 发送消息
                payload = {
                    "message": task.content,
                    "provider": provider
                }
                await websocket.send(json.dumps(payload, ensure_ascii=False))

                # 接收流式响应
                full_response = ""

                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=30.0)

                        # 解析响应
                        try:
                            data = json.loads(response)

                            if data.get("type") == "done":
                                break
                            elif data.get("type") == "error":
                                raise Exception(data.get("message", "Gateway error"))
                        except json.JSONDecodeError:
                            # 普通文本
                            full_response += response

                    except asyncio.TimeoutError:
                        raise Exception("Gateway响应超时")

            print(f"[Worker {self.worker_id}] Gateway流式执行成功（{provider}）")
            return full_response

        except ImportError as e:
            print(f"[Worker {self.worker_id}] Gateway模式失败，回退到V1: {e}")
            return await self._execute_via_v1(task)
        except Exception as e:
            print(f"[Worker {self.worker_id}] Gateway执行失败: {e}")
            raise

    async def _execute_via_self_exec(self, task: Task) -> str:
        """使用自主exec工具执行命令"""
        try:
            # 解析命令
            command = task.content
            timeout = task.metadata.get("timeout", 30) if task.metadata else 30
            background = task.metadata.get("background", False) if task.metadata else False

            print(f"[Worker {self.worker_id}] 使用自主exec: {command}")

            # 调用自主exec
            exit_code, stdout, stderr = await execute(
                command=command,
                timeout=timeout,
                background=background
            )

            if exit_code == 0:
                result = stdout
                print(f"[Worker {self.worker_id}] 自主exec执行成功")
            else:
                raise Exception(f"命令失败 (exit={exit_code}): {stderr}")

            return result

        except Exception as e:
            print(f"[Worker {self.worker_id}] 自主exec执行失败: {e}")
            raise

    async def _execute_via_v1(self, task: Task) -> str:
        """使用V1 Gateway API执行任务"""
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
            result = data["choices"][0]["message"]["content"]
            task.metadata = data.get("usage", {})
            print(f"[Worker {self.worker_id}] V1 API执行成功")
            return result
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    def save_task_to_sqlite(self, task: Task):
        """保存任务到SQLite"""
        if not self.sqlite_conn:
            return

        try:
            import uuid
            task_id = task.id or str(uuid.uuid4())

            self.sqlite_conn.execute('''
                INSERT OR REPLACE INTO worker_tasks
                (task_id, worker_id, task_type, status, result, error)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                task_id,
                self.worker_id,
                task.metadata.get("task_type", "v1") if task.metadata else "v1",
                task.status,
                task.result,
                task.error
            ))

            self.sqlite_conn.commit()
            print(f"[Worker {self.worker_id}] 任务已保存到SQLite")
        except Exception as e:
            print(f"[Worker {self.worker_id}] SQLite保存失败: {e}")

    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()
        if self.sqlite_conn:
            self.sqlite_conn.close()


# 便捷函数
async def execute_with_enhanced_worker(
    content: str,
    task_type: str = "v1",
    **metadata
) -> tuple[bool, str, Optional[str]]:
    """
    使用增强版Worker执行任务

    Args:
        content: 任务内容
        task_type: 任务类型 (chat/command/v1)
        metadata: 额外元数据

    Returns:
        (success, result, error)
    """
    from common.models import Task

    worker = EnhancedV2Worker()

    try:
        task = Task(content=content, metadata={"task_type": task_type, **metadata})
        task = await worker.execute_task(task)

        if task.status == "completed":
            return True, task.result, None
        else:
            return False, None, task.error
    finally:
        await worker.close()


# 测试
if __name__ == "__main__":
    import sys

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    async def test():
        print("\n" + "="*70)
        print("增强版V2 Worker测试")
        print("="*70 + "\n")

        worker = EnhancedV2Worker(worker_id="test")

        # 测试1: V1 API
        print("[测试1] V1 API")
        try:
            success, result, error = await worker._execute_via_v1(
                Task(content="你好，请用一句话介绍什么是你？")
            )
            print(f"✅ {result[:50]}...")
        except Exception as e:
            print(f"❌ {e}")

        # 测试2: 自主exec
        print("\n[测试2] 自主exec")
        try:
            result = await worker._execute_via_self_exec(
                Task(content="python --version")
            )
            print(f"✅ {result}")
        except Exception as e:
            print(f"❌ {e}")

        print("\n" + "="*70)
        print("测试完成")
        print("="*70 + "\n")

        await worker.close()

    asyncio.run(test())
