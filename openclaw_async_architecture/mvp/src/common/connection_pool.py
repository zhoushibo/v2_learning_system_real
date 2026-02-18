# -*- coding: utf-8 -*-
"""连接池管理 - Phase 2性能优化"""

import redis
import sqlite3
from typing import Optional
from contextlib import contextmanager
from threading import Lock
from .config import settings


class RedisConnectionPool:
    """Redis连接池管理器"""

    _instance = None
    _lock = Lock()
    _pool = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._pool = redis.ConnectionPool(
                        host=settings.redis_host,
                        port=settings.redis_port,
                        db=settings.redis_db,
                        password=settings.redis_password,
                        max_connections=10,  # 最大连接数
                        decode_responses=True,
                        socket_keepalive=True,
                        socket_keepalive_options={
                            1: 1,  # TCP_KEEPIDLE
                            2: 3,  # TCP_KEEPINTVL
                            3: 5   # TCP_KEEPCNT
                        }
                    )
        return cls._instance

    @property
    def client(self) -> redis.Redis:
        """获取Redis客户端（自动从连接池获取）"""
        return redis.Redis(connection_pool=self._pool)

    @contextmanager
    def get_client(self):
        """上下文管理器模式获取客户端"""
        client = self.client
        try:
            yield client
        finally:
            # Connection会自动归还到池
            pass


class SQLiteConnectionPool:
    """SQLite连接池管理器

    SQLite本身不支持真正的连接池，所以我们：
    1. 维护一个连接（线程安全）
    2. 使用连接复用
    3. 提供事务管理
    """

    _instance = None
    _lock = Lock()
    _conn = None
    _db_path = None

    def __new__(cls, db_path: Optional[str] = None):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._db_path = db_path
                    cls._conn = None
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """获取SQLite连接（线程安全）"""
        with self._lock:
            if self._conn is None:
                import os
                if self._db_path is None:
                    db_dir = r'C:\Users\10952\.openclaw\workspace\memory'
                    os.makedirs(db_dir, exist_ok=True)
                    self._db_path = os.path.join(db_dir, 'v1_memory.db')

                self._conn = sqlite3.connect(
                    self._db_path,
                    check_same_thread=False,
                    isolation_level=None  # 自动提交模式（每个语句自动提交）
                )
                self._conn.row_factory = sqlite3.Row  # 返回字典格式
                self._init_tables()

            return self._conn

    def _init_tables(self):
        """初始化表"""
        cursor = self._conn.cursor()

        # 创建任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                result TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT '{}'
            )
        ''')

        self._conn.commit()

    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def close(self):
        """关闭连接"""
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None


# 全局单例
redis_pool = RedisConnectionPool()
sqlite_pool = SQLiteConnectionPool()
