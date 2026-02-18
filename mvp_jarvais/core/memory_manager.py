"""
MemoryManager - 三层记忆系统管理器

在MVP全能AI系统中负责：
1. 封装V1三层记忆系统（SQLite + ChromaDB + Redis）
2. 提供统一API给Agent使用
3. 三层查询优化（Redis → ChromaDB → SQLite）
4. 持久化和缓存管理
"""

import sys
import os

# 添加V1记忆系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'openclaw_async_architecture', 'mvp', 'src', 'common'))

try:
    from v1_memory_integration import V1MemorySystemIntegration
    V1_AVAILABLE = True
except ImportError:
    V1_AVAILABLE = False
    print("⚠️ 警告：V1记忆系统未找到，将使用简化版")

from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    三层记忆系统管理器
    
    架构：
    - L1: Redis（快速缓存，TTL=3600秒）
    - L2: ChromaDB（向量搜索，语义检索）
    - L3: SQLite（持久化存储，永久保留）
    """
    
    def __init__(self, enable_v1: bool = True):
        """
        初始化记忆管理器
        
        Args:
            enable_v1: 是否使用V1三层记忆系统
        """
        if enable_v1 and V1_AVAILABLE:
            self.v1_memory = V1MemorySystemIntegration()
            self.mode = "full"  # 全功能模式
            logger.info("✅ MemoryManager初始化：全功能模式（Redis + ChromaDB + SQLite）")
        else:
            self.v1_memory = None
            self.mode = "simple"  # 简化模式
            # 使用内存字典作为Fallback
            self._simple_cache = {}
            logger.info("⚠️  MemoryManager初始化：简化模式（内存缓存）")
    
    # ==================== 核心API ====================
    
    async def remember(self, key: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """
        记住内容（三层存储）
        
        1. L1: Redis缓存（快速访问）
        2. L2: ChromaDB向量（语义搜索）
        3. L3: SQLite持久化（长期存储）
        
        Args:
            key: 唯一标识符
            content: 要记住的内容
            metadata: 元数据（类型、时间等）
            
        Returns:
            bool: 是否成功
        """
        try:
            if self.mode == "full":
                # 使用V1三层记忆系统
                full_data = {
                    "key": key,
                    "content": content,
                    "metadata": metadata or {},
                    "timestamp": datetime.now().isoformat()
                }
                
                # 保存到三层存储
                self.v1_memory.save(
                    key=key,
                    value=full_data,
                    content_for_vector=content  # 用于向量搜索
                )
                
                logger.debug(f"[L1+L2+L3] 记住: {key}")
                return True
            
            else:
                # 简化模式（内存缓存）
                self._simple_cache[key] = {
                    "content": content,
                    "metadata": metadata or {},
                    "timestamp": datetime.now().isoformat()
                }
                logger.debug(f"[缓存] 记住: {key}")
                return True
                
        except Exception as e:
            logger.error(f"记忆失败 [{key}]: {e}")
            return False
    
    async def recall(self, key: str) -> Optional[Dict[str, Any]]:
        """
        回忆内容（三层查询）
        
        查询顺序：
        1. L1: Redis（最快）
        2. L3: SQLite（fallback）
        
        Args:
            key: 唯一标识符
            
        Returns:
            记忆内容（字典格式），如果不存在返回None
        """
        try:
            if self.mode == "full":
                # 使用V1三层记忆系统
                result = self.v1_memory.get(key)
                if result:
                    logger.debug(f"[L1/L3] 回忆命中: {key}")
                    return result
                    
                logger.debug(f"[未命中] 回忆: {key}")
                return None
            
            else:
                # 简化模式
                result = self._simple_cache.get(key)
                if result:
                    logger.debug(f"[缓存] 回忆命中: {key}")
                    return result
                    
                logger.debug(f"[缓存未命中] 回忆: {key}")
                return None
                
        except Exception as e:
            logger.error(f"回忆失败 [{key}]: {e}")
            return None
    
    async def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        语义搜索（向量检索）
        
        使用L2: ChromaDB进行向量搜索，返回最相关的记忆
        
        Args:
            query: 搜索查询（自然语言）
            n_results: 返回结果数量
            
        Returns:
            搜索结果列表（字典格式）
        """
        try:
            if self.mode == "full":
                # 使用V1的ChromaDB搜索
                documents = self.v1_memory.search_vector_db(query, n_results)
                
                results = []
                for i, doc in enumerate(documents):
                    results.append({
                        "content": doc,
                        "rank": i + 1,
                        "relevance": 1.0 - (i * 0.1)  # 简化相关度计算
                    })
                
                logger.debug(f"[L2-ChromaDB] 搜索: {query} -> 返回{len(results)}条")
                return results
            
            else:
                # 简化模式（关键词匹配）
                query_lower = query.lower()
                results = []
                
                for key, data in self._simple_cache.items():
                    content = data.get("content", "")
                    if query_lower in content.lower():
                        results.append({
                            "key": key,
                            "content": content,
                            "relevance": 1.0
                        })
                
                results.sort(key=lambda x: x["relevance"], reverse=True)
                results = results[:n_results]
                
                logger.debug(f"[缓存搜索] 搜索: {query} -> 返回{len(results)}条")
                return results
                
        except Exception as e:
            logger.error(f"搜索失败 [{query}]: {e}")
            return []
    
    # ==================== 批量操作 ====================
    
    async def remember_batch(self, items: List[Dict[str, str]]) -> int:
        """
        批量记住
        
        Args:
            items: [{"key": "...", "content": "...", "metadata": {...}}, ...]
            
        Returns:
            int: 成功保存的数量
        """
        success_count = 0
        for item in items:
            success = await self.remember(
                key=item["key"],
                content=item["content"],
                metadata=item.get("metadata", {})
            )
            if success:
                success_count += 1
        
        logger.info(f"批量记住: {success_count}/{len(items)} 条")
        return success_count
    
    async def search_batch(self, queries: List[str], n_results: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量搜索
        
        Args:
            queries: 搜索查询列表
            n_results: 每个查询返回结果数
            
        Returns:
            Dict: {query: [results]}
        """
        results = {}
        for query in queries:
            results[query] = await self.search(query, n_results)
        
        return results
    
    # ==================== 辅助功能 ====================
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            Dict: 各层状态
        """
        if self.mode == "full":
            return {
                "mode": "full",
                "v1_memory": self.v1_memory.health_check() if self.v1_memory else {},
                "status": "healthy" if self.v1_memory else "degraded"
            }
        else:
            return {
                "mode": "simple",
                "cache_size": len(self._simple_cache),
                "status": "limited"
            }
    
    async def clear_cache(self):
        """清空缓存层（L1: Redis）"""
        if self.mode == "full" and self.v1_memory:
            # 清空Redis
            try:
                self.v1_memory.redis_client.flushdb()
                logger.info("✅ L1缓存已清空")
            except Exception as e:
                logger.error(f"清空缓存失败: {e}")
        else:
            self._simple_cache.clear()
            logger.info("✅ 内存缓存已清空")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 记忆统计
        """
        health = self.health_check()
        
        return {
            "mode": self.mode,
            "health": health,
            "timestamp": datetime.now().isoformat()
        }


# ==================== 单例模式 ====================

_memory_manager_instance: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """获取MemoryManager单例"""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance


# ==================== 测试代码 ====================

async def main():
    """测试MemoryManager"""
    print("="*60)
    print("🧠 MemoryManager测试")
    print("="*60)
    
    # 创建管理器
    memory = MemoryManager(enable_v1=True)
    
    # 健康检查
    print("\n1️⃣ 健康检查")
    health = memory.health_check()
    print(f"  模式: {health['mode']}")
    print(f"  状态: {health['status']}")
    
    # 记住
    print("\n2️⃣ 记住测试")
    await memory.remember(
        key="test_1",
        content="这是一个测试记忆内容",
        metadata={"type": "test", "source": "test"}
    )
    
    await memory.remember(
        key="test_2", 
        content="今天完成了三层记忆系统集成",
        metadata={"type": "achievement", "date": "2026-02-17"}
    )
    
    # 回忆
    print("\n3️⃣ 回忆测试")
    result = await memory.recall("test_1")
    if result:
        print(f"  ✅ 回忆成功: {result['content']}")
    else:
        print(f"  ❌ 回忆失败")
    
    # 搜索
    print("\n4️⃣ 语义搜索测试")
    results = await memory.search("测试内容", n_results=2)
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r.get('content', '')[:50]}...")
    
    # 统计
    print("\n5️⃣ 统计信息")
    stats = await memory.get_stats()
    print(f"  模式: {stats['mode']}")
    print(f"  状态: {stats['health']['status']}")
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
