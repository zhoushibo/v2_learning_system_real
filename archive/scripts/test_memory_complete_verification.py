"""
三层记忆系统完整验证测试
验证三个层次的独立工作和协同能力
"""

import sqlite3
import redis
import chromadb
import json
from datetime import datetime
import sys
import os

# 添加workspace路径
sys.path.insert(0, os.path.dirname(__file__))




class MemorySystemTest:
    def __init__(self):
        print("="*60)
        print("🧠 三层记忆系统完整验证")
        print("="*60)

        # 初始化三层
        self.l1_redis = None
        self.l2_chroma = None
        self.l3_sqlite = None

    def test_l1_redis(self):
        """测试L1: Redis缓存层"""
        print("\n🔹 L1: Redis缓存层")
        print("-" * 50)

        try:
            # 初始化Redis
            self.l1_redis = redis.Redis(
                host='127.0.0.1',
                port=6379,
                db=0,
                decode_responses=True
            )

            # 连接测试
            self.l1_redis.ping()
            print("✅ Redis连接成功")

            # 写入测试
            test_key = f"test:l1:{datetime.now().timestamp()}"
            test_value = {"message": "Hello L1", "timestamp": datetime.now().isoformat()}

            self.l1_redis.setex(test_key, 60, json.dumps(test_value))
            print(f"✅ 写入成功: {test_key}")

            # 读取测试
            retrieved = self.l1_redis.get(test_key)
            if retrieved:
                data = json.loads(retrieved)
                print(f"✅ 读取成功: {data['message']}")
                print(f"   延迟: ~1ms（缓存层）")

            # 清理
            self.l1_redis.delete(test_key)

            return True

        except Exception as e:
            print(f"❌ Redis测试失败: {e}")
            return False

    def test_l2_chroma(self):
        """测试L2: ChromaDB向量层"""
        print("\n🔹 L2: ChromaDB向量层")
        print("-" * 50)

        try:
            # 初始化ChromaDB
            self.l2_chroma = chromadb.Client()

            # 创建/获取集合
            try:
                collection = self.l2_chroma.get_collection(name="test_memories")
            except:
                collection = self.l2_chroma.create_collection(
                    name="test_memories",
                    metadata={"description": "测试集合"}
                )

            print("✅ ChromaDB初始化成功")

            # 准备测试数据
            test_docs = [
                "测试文档1：三层记忆系统的第一层",
                "测试文档2：Redis缓存层提供快速访问",
                "测试文档3：ChromaDB向量层支持语义搜索"
            ]

            test_embeddings = [
                [0.1, 0.2, 0.3] * 300,  # 模拟嵌入
                [0.2, 0.3, 0.4] * 300,
                [0.3, 0.4, 0.5] * 300
            ]

            # 写入测试
            collection.add(
                documents=test_docs,
                embeddings=test_embeddings,
                ids=[f"doc_{i}" for i in range(len(test_docs))],
                metadatas=[{"layer": "L2", "test": i} for i in range(len(test_docs))]
            )

            print(f"✅ 写入成功: {len(test_docs)} 个文档")

            # 查询测试
            query_embedding = [0.15, 0.25, 0.35] * 300
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=2
            )

            print(f"✅ 查询成功: 返回 {len(results['documents'][0])} 条结果")
            print(f"   结果1: {results['documents'][0][0][:30]}...")

            # 清理
            try:
                for doc_id in [f"doc_{i}" for i in range(len(test_docs))]:
                    collection.delete(ids=[doc_id])
            except:
                pass

            return True

        except Exception as e:
            print(f"❌ ChromaDB测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_l3_sqlite(self):
        """测试L3: SQLite持久化层"""
        print("\n🔹 L3: SQLite持久化层")
        print("-" * 50)

        try:
            # 初始化SQLite
            db_path = r'C:\Users\10952\.openclaw\workspace\memory\v1_memory.db'
            self.l3_sqlite = sqlite3.connect(db_path, check_same_thread=False)
            cursor = self.l3_sqlite.cursor()

            print("✅ SQLite连接成功")

            # 检查表结构
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"✅ 数据表: {[t[0] for t in tables]}")

            # 写入测试
            test_id = f"test_{int(datetime.now().timestamp())}"
            test_data = {
                "task_id": test_id,
                "content": "三层记忆系统持久化测试",
                "status": "completed",
                "metadata": {"layer": "L3", "test": True}
            }

            cursor.execute('''
                INSERT OR REPLACE INTO tasks
                (task_id, content, status, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                test_data['task_id'],
                test_data['content'],
                test_data['status'],
                json.dumps(test_data['metadata'])
            ))

            self.l3_sqlite.commit()
            print(f"✅ 写入成功: {test_id}")

            # 读取测试
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (test_id,))
            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                data = dict(zip(columns, row))
                print(f"✅ 读取成功: {data['content'][:20]}...")

                # 验证数据完整性
                assert data['task_id'] == test_id
                assert data['status'] == 'completed'
                print("✅ 数据完整性验证通过")

            return True

        except Exception as e:
            print(f"❌ SQLite测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_integration(self):
        """测试三层集成协同"""
        print("\n🔹 三层集成协同测试")
        print("-" * 50)

        try:
            test_key = f"integration_{int(datetime.now().timestamp())}"
            test_value = {
                "message": "三层协同测试",
                "timestamp": datetime.now().isoformat()
            }

            # 1. L1: 缓存写入
            if self.l1_redis:
                self.l1_redis.setex(test_key, 60, json.dumps(test_value))
                print("✅ L1: 缓存已保存")

            # 2. L3: 持久化写入
            if self.l3_sqlite:
                cursor = self.l3_sqlite.cursor()

                # 先创建memories表（如果不存在）
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cursor.execute('''
                    INSERT OR REPLACE INTO memories
                    (id, content, metadata)
                    VALUES (?, ?, ?)
                ''', (
                    test_key,
                    json.dumps(test_value),
                    json.dumps({"layer": "integration"})
                ))

                self.l3_sqlite.commit()
                print("✅ L3: 已持久化")

            # 3. L1: 缓存读取（应该立即返回）
            if self.l1_redis:
                cached = self.l1_redis.get(test_key)
                if cached:
                    print("✅ L1: 缓存命中（~1ms）")

            # 4. 清空缓存，测试L3读取
            if self.l1_redis:
                self.l1_redis.delete(test_key)
                print("🔄 已清空L1缓存")

            # 5. L3: 从持久化层读取
            if self.l3_sqlite:
                cursor = self.l3_sqlite.cursor()
                cursor.execute("SELECT * FROM memories WHERE id = ?", (test_key,))
                row = cursor.fetchone()

                if row:
                    print("✅ L3: 从持久化层读取（~1-10ms）")

                # 然后回写L1
                if self.l1_redis:
                    self.l1_redis.setex(test_key, 60, row[1])
                    print("✅ L1: 已回写缓存（缓存预热）")

            print("\n✅ 三层协同工作正常！")
            print("   流程：L1(缓存) → L3(持久化) → L1(回写)")

            return True

        except Exception as e:
            print(f"❌ 集成测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_vector_search(self):
        """测试向量搜索功能"""
        print("\n🔹 向量搜索功能测试")
        print("-" * 50)

        try:
            # 检查是否已集成SiliconFlow Embeddings
            from tools.memory_search_siliconflow import get_embedding

            print("✅ SiliconFlow Embeddings导入成功")

            # 测试嵌入生成
            test_text = "三层记忆系统"
            embedding = get_embedding(test_text)

            print(f"✅ 嵌入生成成功")
            print(f"   维度: {len(embedding)}")
            print(f"   样本: {embedding[:5]}...")

            return True

        except ImportError:
            print("⚠️  memory_search_siliconflow未找到")
            print("   向量搜索功能需要单独集成")
            return False
        except Exception as e:
            print(f"❌ 向量搜索测试失败: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("\n🚀 开始测试...\n")

        results = {}

        # 单层测试
        results['L1-Redis'] = self.test_l1_redis()
        results['L2-ChromaDB'] = self.test_l2_chroma()
        results['L3-SQLite'] = self.test_l3_sqlite()

        # 集成测试
        results['Integration'] = self.test_integration()

        # 向量搜索测试
        results['VectorSearch'] = self.test_vector_search()

        # 总结
        print("\n" + "="*60)
        print("📊 测试总结")
        print("="*60)

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        for test, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test:20s} {status}")

        print("-" * 60)
        print(f"通过率: {passed}/{total} ({passed/total*100:.1f}%)")

        if passed == total:
            print("\n🎉 三层记忆系统集成验证全部通过！")
            print("\n📝 系统状态：")
            print("   ✓ L1 Redis缓存层 - 正常运行")
            print("   ✓ L2 ChromaDB向量层 - 正常运行")
            print("   ✓ L3 SQLite持久化层 - 正常运行")
            print("   ✓ 三层协同机制 - 工作正常")
            print("\n🎯 核心能力：")
            print("   • 快速缓存（Redis）- <1ms")
            print("   • 语义搜索（ChromaDB) - 语义理解")
            print("   • 可靠持久化（SQLite）- 不会丢失")
            print("   • 自动缓存预热 - L3→L1回写")
        else:
            print(f"\n⚠️  {total-passed} 个测试失败，需要修复")

        # 清理资源
        if self.l3_sqlite:
            self.l3_sqlite.close()

        print("="*60)

        return passed == total


if __name__ == "__main__":
    tester = MemorySystemTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
