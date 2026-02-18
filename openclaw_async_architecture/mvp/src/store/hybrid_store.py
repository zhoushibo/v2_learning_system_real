# -*- coding: utf-8 -*-
"""混合存储：SQLite（L3）+ Redis（L1缓存）- Phase 2优化版"""
import json
from typing import Optional
from ..common.config import settings
from ..common.models import Task
from ..common.connection_pool import redis_pool, sqlite_pool


class HybridTaskStore:
    """
    混合任务存储（连接池优化版）

    三层架构：
    - L1: Redis缓存（快速查询）
    - L3: SQLite持久化（可靠存储）

    Phase 2优化：
    - 使用Redis连接池（max_connections=10）
    - 使用SQLite连接复用
    - 添加事务管理
    """

    def __init__(self):
        """初始化（使用连接池）"""
        # L1: Redis连接池
        self.redis_client = redis_pool.client
        self.result_prefix = "tasks:cached:"

        # L3: SQLite连接池
        self.sqlite_pool = sqlite_pool

        try:
            # 预连接SQLite
            self.sqlite_pool.get_connection()
            print("[Store] SQLite L3持久化层已初始化 [OK]")
        except Exception as e:
            print(f"[Store] SQLite初始化失败（降级为仅Redis模式）: {e}")

    def save_task(self, task: Task) -> bool:
        """保存任务（双层写入，使用连接池）"""
        success = True

        # L1: Redis缓存（1小时）
        try:
            self.redis_client.setex(
                f"{self.result_prefix}{task.id}",
                3600,
                task.model_dump_json()
            )
        except Exception as e:
            print(f"[L1-Redis] 保存失败: {e}")
            success = False

        # L3: SQLite持久化（使用事务）
        try:
            with self.sqlite_pool.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO tasks
                    (task_id, content, status, result, error, metadata, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    task.id,
                    task.content,
                    task.status,
                    task.result,
                    task.error,
                    json.dumps(task.metadata, ensure_ascii=False)
                ))
        except Exception as e:
            print(f"[L3-SQLite] 保存失败: {e}")
            success = False

        return success

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务（先查Redis缓存，未命中查SQLite）"""
        # L1: Redis缓存
        try:
            cached = self.redis_client.get(f"{self.result_prefix}{task_id}")
            if cached:
                return Task.model_validate_json(cached)
        except Exception:
            pass

        # L3: SQLite
        try:
            conn = self.sqlite_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT task_id, content, status, result, error, metadata, created_at, updated_at
                FROM tasks WHERE task_id = ?
            ''', (task_id,))
            row = cursor.fetchone()

            if row:
                # 回写Redis缓存
                task_dict = dict(row)
                task_dict['metadata'] = json.loads(task_dict['metadata'])
                task = Task(**task_dict)

                try:
                    self.redis_client.setex(
                        f"{self.result_prefix}{task.id}",
                        3600,
                        task.model_dump_json()
                    )
                except Exception:
                    pass

                return task
        except Exception as e:
            print(f"[L3-SQLite] 查询失败: {e}")

        return None

    def update_task(self, task_id: str, **kwargs) -> bool:
        """更新任务字段（使用连接池和事务）"""
        try:
            with self.sqlite_pool.transaction() as conn:
                cursor = conn.cursor()

                # 构建动态更新语句
                set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
                values = list(kwargs.values()) + [task_id]

                cursor.execute(f'''
                    UPDATE tasks SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = ?
                ''', values)

                # 更新Redis缓存
                try:
                    if 'status' in kwargs or 'result' in kwargs or 'error' in kwargs:
                        self.redis_client.delete(f"{self.result_prefix}{task_id}")
                except Exception:
                    pass

                return True
        except Exception as e:
            print(f"[Store] 更新失败: {e}")
            return False

    def delete_task(self, task_id: str) -> bool:
        """删除任务（双层删除）"""
        success = True

        # L1: Redis
        try:
            self.redis_client.delete(f"{self.result_prefix}{task_id}")
        except Exception as e:
            print(f"[L1-Redis] 删除失败: {e}")
            success = False

        # L3: SQLite
        try:
            with self.sqlite_pool.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
        except Exception as e:
            print(f"[L3-SQLite] 删除失败: {e}")
            success = False

        return success

    def list_tasks(self, status: Optional[str] = None, limit: int = 100) -> list[Task]:
        """列出任务（使用连接池）"""
        try:
            conn = self.sqlite_pool.get_connection()
            cursor = conn.cursor()

            if status:
                cursor.execute('''
                    SELECT task_id, content, status, result, error, metadata, created_at, updated_at
                    FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?
                ''', (status, limit))
            else:
                cursor.execute('''
                    SELECT task_id, content, status, result, error, metadata, created_at, updated_at
                    FROM tasks ORDER BY created_at DESC LIMIT ?
                ''', (limit,))

            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                task_dict = dict(row)
                task_dict['metadata'] = json.loads(task_dict['metadata'])
                tasks.append(Task(**task_dict))

            return tasks
        except Exception as e:
            print(f"[Store] 查询失败: {e}")
            return []

    def clear(self) -> bool:
        """清空所有任务（使用连接池）"""
        success = True

        # L1: Redis
        try:
            # 删除所有缓存任务
            keys = self.redis_client.keys(f"{self.result_prefix}*")
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print(f"[L1-Redis] 清空失败: {e}")
            success = False

        # L3: SQLite
        try:
            with self.sqlite_pool.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM tasks')
        except Exception as e:
            print(f"[L3-SQLite] 清空失败: {e}")
            success = False

        return success

    def get_statistics(self) -> dict:
        """获取存储统计（使用连接池）"""
        stats = {
            "total": 0,
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0
        }

        try:
            conn = self.sqlite_pool.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT status, COUNT(*) as count
                FROM tasks GROUP BY status
            ''')

            for row in cursor.fetchall():
                status = row['status']
                count = row['count']
                stats[status] = count
                stats["total"] += count

        except Exception as e:
            print(f"[Store] 统计失败: {e}")

        return stats

    def close(self):
        """关闭连接池"""
        try:
            self.sqlite_pool.close()
        except Exception as e:
            print(f"[Store] 关闭失败: {e}")
