"""
V1 MemorySystem三层记忆系统集成到V2 MVP

V1技术栈：
1. SQLite - 主存储（持久化）
2. ChromaDB - 向量存储（语义搜索）
3. Redis - 缓存层（快速访问）
"""

import sqlite3
import redis
import chromadb
from typing import Optional, Dict, Any
from datetime import datetime
import json


class V1MemorySystemIntegration:
    """
    集成V1的三层记忆系统到V2 MVP

    三层架构：
    - L1: Redis (缓存，最快)
    - L2: ChromaDB (向量搜索，语义检索)
    - L3: SQLite (持久化存储，最可靠)
    """

    def __init__(self):
        # L1: Redis缓存
        self.redis_client = redis.Redis(
            host='127.0.0.1',
            port=6379,
            db=0,
            decode_responses=True
        )

        # L2: ChromaDB向量数据库
        self.chroma_client = chromadb.Client()
        try:
            # 尝试获取已存在的集合
            self.chroma_collection = self.chroma_client.get_collection(name="openclaw_memory")
        except:
            # 创建新集合
            self.chroma_collection = self.chroma_client.create_collection(
                name="openclaw_memory",
                metadata={"description": "OpenClaw三层记忆系统 - L2向量层"}
            )

        # L3: SQLite持久化存储
        self.sqlite_conn = sqlite3.connect(
            'C:\\Users\\10952\\.openclaw\\workspace\\memory\\v1_memory.db',
            check_same_thread=False
        )
        self._init_sqlite()

    def _init_sqlite(self):
        """初始化SQLite表"""
        cursor = self.sqlite_conn.cursor()

        # 创建记忆表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                embedding TEXT,  # JSON格式存储向量
                metadata TEXT,   # JSON格式存储元数据
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        ''')

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
                metadata TEXT
            )
        ''')

        self.sqlite_conn.commit()

    # ==================== L1: Redis层 ====================

    def save_to_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """保存到Redis缓存（L1）"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            self.redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            print(f"[L1-Redis] 保存失败: {e}")
            return False

    def get_from_cache(self, key: str) -> Optional[Any]:
        """从Redis缓存获取（L1）"""
        try:
            value = self.redis_client.get(key)
            if value:
                # 尝试解析JSON
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            print(f"[L1-Redis] 获取失败: {e}")
            return None

    # ==================== L2: ChromaDB层 ====================

    def save_to_vector_db(self, doc_id: str, content: str, metadata: Optional[Dict] = None):
        """保存到ChromaDB向量数据库（L2）"""
        try:
            # 这里需要调用SiliconFlow Embeddings API获取向量
            from tools.memory_search_siliconflow import get_embedding

            # 获取向量
            embedding = get_embedding(content)

            # 保存到ChromaDB
            self.chroma_collection.add(
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )

            return True
        except Exception as e:
            print(f"[L2-ChromaDB] 保存失败: {e}")
            return False

    def search_vector_db(self, query: str, n_results: int = 5) -> list:
        """从ChromaDB向量搜索（L2）"""
        try:
            from tools.memory_search_siliconflow import get_embedding

            # 获取查询向量
            query_embedding = get_embedding(query)

            # 向量搜索
            results = self.chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            return results['documents'][0] if results['documents'] else []

        except Exception as e:
            print(f"[L2-ChromaDB] 搜索失败: {e}")
            return []

    # ==================== L3: SQLite层 ====================

    def save_to_sqlite(self, table: str, data: Dict) -> bool:
        """保存到SQLite（L3）"""
        try:
            cursor = self.sqlite_conn.cursor()

            if table == "tasks":
                cursor.execute('''
                    INSERT OR REPLACE INTO tasks
                    (task_id, content, status, result, error, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    data['task_id'],
                    data['content'],
                    data.get('status', 'pending'),
                    data.get('result'),
                    data.get('error'),
                    json.dumps(data.get('metadata', {}), ensure_ascii=False)
                ))
            elif table == "memories":
                cursor.execute('''
                    INSERT OR REPLACE INTO memories
                    (id, content, embedding, metadata, tags)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    data['id'],
                    data['content'],
                    json.dumps(data.get('embedding', [])),
                    json.dumps(data.get('metadata', {}), ensure_ascii=False),
                    data.get('tags', '')
                ))

            self.sqlite_conn.commit()
            return True

        except Exception as e:
            print(f"[L3-SQLite] 保存失败: {e}")
            return False

    def get_from_sqlite(self, table: str, key: str, key_field: str = "id") -> Optional[Dict]:
        """从SQLite获取（L3）"""
        try:
            cursor = self.sqlite_conn.cursor()

            query = f"SELECT * FROM {table} WHERE {key_field} = ?"
            cursor.execute(query, (key,))
            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                result = dict(zip(columns, row))
                # 解析JSON字段
                if 'metadata' in result and result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                return result

            return None

        except Exception as e:
            print(f"[L3-SQLite] 获取失败: {e}")
            return None

    # ==================== 三层统一接口 ====================

    def save(self, key: str, value: Any, content_for_vector: Optional[str] = None):
        """
        三层保存

        1. L1: Redis保存（快）
        2. L2: ChromaDB保存（向量搜索）
        3. L3: SQLite保存（持久化）
        """
        # L1: Redis
        self.save_to_cache(key, value, ttl=3600)

        # L2: ChromaDB
        if content_for_vector:
            self.save_to_vector_db(key, content_for_vector, metadata={"key": key})

        # L3: SQLite
        if isinstance(value, dict) and 'task_id' in value:
            self.save_to_sqlite("tasks", value)

    def get(self, key: str) -> Optional[Any]:
        """
        三层获取

        1. L1: Redis查询（快）
        2. L2/L3: 如果L1没有，从SQLite获取
        """
        # L1: Redis
        value = self.get_from_cache(key)
        if value:
            print(f"[L1命中] 从Redis获取")
            return value

        # L3: SQLite
        value = self.get_from_sqlite("tasks", key, "task_id")
        if value:
            print(f"[L3命中] 从SQLite获取")
            # 回写L1
            self.save_to_cache(key, value, ttl=3600)
            return value

        print("[三层未中] 未找到")
        return None

    def search(self, query: str, n_results: int = 5) -> list:
        """
        语义搜索（使用L2: ChromaDB）

        这是V1记忆搜索的核心能力
        """
        return self.search_vector_db(query, n_results)

    # ==================== 健康检查 ====================

    def health_check(self) -> Dict:
        """健康检查"""
        redis_ok = False
        sqlite_ok = False
        chroma_ok = False

        # L1: Redis
        try:
            self.redis_client.ping()
            redis_ok = True
        except:
            pass

        # L2: ChromaDB
        try:
            self.chroma_client.get_collection(name="openclaw_memory")
            chroma_ok = True
        except:
            pass

        # L3: SQLite
        try:
            self.sqlite_conn.cursor().execute("SELECT 1")
            sqlite_ok = True
        except:
            pass

        return {
            "l1_redis": redis_ok,
            "l2_chroma": chroma_ok,
            "l3_sqlite": sqlite_ok,
            "all_ok": redis_ok and sqlite_ok and chroma_ok
        }


# 单例
memory_system = None

def get_memory_system():
    """获取记忆系统实例"""
    global memory_system
    if memory_system is None:
        memory_system = V1MemorySystemIntegration()
    return memory_system


if __name__ == "__main__":
    print("="*60)
    print("V1 MemorySystem三层记忆系统集成测试")
    print("="*60)

    # 初始化
    memory = V1MemorySystemIntegration()

    # 健康检查
    print("\n1️⃣ 健康检查")
    health = memory.health_check()
    print(f"  Redis (L1):    {'✅' if health['l1_redis'] else '❌'}")
    print(f"  ChromaDB (L2): {'✅' if health['l2_chroma'] else '❌'}")
    print(f"  SQLite (L3):   {'✅' if health['l3_sqlite'] else '❌'}")

    if not health['l3_sqlite']:
        print("\n⚠️  注意：SQLite初始化需要，ChromaDB可选")
        print("   MVP可以只使用 SQLite + Redis")
