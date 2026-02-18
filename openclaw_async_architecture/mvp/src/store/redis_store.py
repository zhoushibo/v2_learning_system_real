"""Redis结果存储"""
import redis
import json
from typing import Optional
from ..common.config import settings
from ..common.models import Task


class RedisTaskStore:
    """Redis任务结果存储"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True
        )
        self.result_prefix = "tasks:result:"

    def save_task(self, task: Task) -> bool:
        """保存任务"""
        try:
            key = f"{self.result_prefix}{task.id}"
            self.redis_client.setex(
                key,
                3600,  # 1小时过期
                task.model_dump_json()
            )
            return True
        except Exception as e:
            print(f"保存任务失败: {e}")
            return False

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        try:
            key = f"{self.result_prefix}{task_id}"
            task_json = self.redis_client.get(key)
            if task_json:
                return Task.model_validate_json(task_json)
            return None
        except Exception as e:
            print(f"获取任务失败: {e}")
            return None

    def test_connection(self) -> bool:
        """测试Redis连接"""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False
