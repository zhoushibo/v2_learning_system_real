"""Redis任务队列 - Phase 2优化：使用连接池"""
import json
from typing import Optional
from ..common.config import settings
from ..common.connection_pool import redis_pool


class RedisTaskQueue:
    """Redis任务队列管理器（连接池优化版）"""

    def __init__(self):
        """初始化（使用连接池）"""
        self.redis_client = redis_pool.client
        self.queue_key = "openclaw_tasks_queue"

    def submit(self, task_id: str, task_data: str) -> bool:
        """提交任务到队列（使用连接池）"""
        try:
            self.redis_client.lpush(self.queue_key, json.dumps({
                "task_id": task_id,
                "task_data": task_data
            }))
            return True
        except Exception as e:
            print(f"[Queue] 提交任务失败: {e}")
            return False

    def get_task(self, timeout: int = 5) -> Optional[dict]:
        """从队列获取任务（阻塞，使用连接池）"""
        try:
            result = self.redis_client.brpop(self.queue_key, timeout=timeout)
            if result:
                queue_name, task_json = result
                return json.loads(task_json)
            return None
        except Exception as e:
            print(f"[Queue] 获取任务失败: {e}")
            return None

    def get_queue_length(self) -> int:
        """获取队列长度（使用连接池）"""
        try:
            return self.redis_client.llen(self.queue_key)
        except Exception:
            return 0

    def clear(self) -> bool:
        """清空队列（使用连接池）"""
        try:
            self.redis_client.delete(self.queue_key)
            return True
        except Exception as e:
            print(f"[Queue] 清空队列失败: {e}")
            return False

    def test_connection(self) -> bool:
        """测试Redis连接（使用连接池）"""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False

    # ====== 新增：批量操作 ======

    def submit_batch(self, tasks: list[tuple[str, str]]) -> int:
        """批量提交任务（使用pipeline优化）"""
        try:
            pipeline = self.redis_client.pipeline()
            for task_id, task_data in tasks:
                pipeline.lpush(self.queue_key, json.dumps({
                    "task_id": task_id,
                    "task_data": task_data
                }))
            pipeline.execute()
            return len(tasks)
        except Exception as e:
            print(f"[Queue] 批量提交失败: {e}")
            return 0

    def get_tasks_batch(self, count: int = 10, timeout: int = 5) -> list[dict]:
        """批量获取任务"""
        tasks = []
        try:
            for _ in range(count):
                result = self.redis_client.brpop(self.queue_key, timeout=1)
                if not result:
                    break
                queue_name, task_json = result
                tasks.append(json.loads(task_json))
            return tasks
        except Exception as e:
            print(f"[Queue] 批量获取失败: {e}")
            return tasks
