"""
V2 学习系统与知识库系统集成模块
学习完成后自动保存到知识库，实现"学习→导入"自动化
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class KnowledgeBaseIntegration:
    """知识库集成器"""
    
    def __init__(self, knowledge_base_path: str = None):
        """
        初始化知识库集成器
        
        Args:
            knowledge_base_path: 知识库系统路径（默认：同级目录）
        """
        if knowledge_base_path is None:
            # 自动查找知识库路径
            current_path = Path(__file__).parent
            workspace_path = current_path.parent
            kb_path = workspace_path / "knowledge_base"
            
            if not kb_path.exists():
                logger.warning(f"知识库路径不存在：{kb_path}")
                kb_path = None
        else:
            kb_path = Path(knowledge_base_path)
        
        self.kb_path = kb_path
        self.initialized = False
        
        # 延迟导入，避免循环依赖
        self.KnowledgeIngest = None
        self.KnowledgeIndex = None
        self.EmbeddingGenerator = None
        self.KnowledgeSearchFTS = None
    
    def _ensure_initialized(self):
        """确保初始化（延迟加载）"""
        if self.initialized:
            return
        
        if not self.kb_path:
            raise RuntimeError("知识库路径未配置")
        
        # 添加知识库路径到 sys.path
        kb_path_str = str(self.kb_path)
        if kb_path_str not in sys.path:
            sys.path.insert(0, kb_path_str)
        
        try:
            # 导入知识库模块
            from core import KnowledgeIngest, KnowledgeIndex, EmbeddingGenerator
            from core.knowledge_search_fts import KnowledgeSearchFTS
            
            self.KnowledgeIngest = KnowledgeIngest
            self.KnowledgeIndex = KnowledgeIndex
            self.EmbeddingGenerator = EmbeddingGenerator
            self.KnowledgeSearchFTS = KnowledgeSearchFTS
            
            self.initialized = True
            logger.info(f"✅ 知识库集成初始化成功：{self.kb_path}")
            
        except ImportError as e:
            logger.error(f"❌ 导入知识库模块失败：{e}")
            raise RuntimeError(f"无法导入知识库模块：{e}")
    
    async def save_learning_result(
        self,
        topic: str,
        learning_data: List[Dict[str, Any]],
        source: str = "v2_learning_system",
        auto_generate_embedding: bool = True
    ) -> Dict[str, Any]:
        """
        保存学习结果到知识库
        
        Args:
            topic: 学习主题
            learning_data: 学习结果列表（来自 parallel_learning）
            source: 来源标识
            auto_generate_embedding: 是否自动生成嵌入向量
        
        Returns:
            保存结果统计
        """
        self._ensure_initialized()
        
        try:
            # 1. 准备知识条目
            knowledge_items = self._prepare_knowledge_items(topic, learning_data, source)
            
            # 2. 初始化组件
            ingest = self.KnowledgeIngest(max_file_size_mb=50)
            embedding_gen = self.EmbeddingGenerator(
                cache_path="./data/embedding_cache.json"
            )
            index = self.KnowledgeIndex(
                chroma_path="./data/chromadb",
                embedding_generator=embedding_gen
            )
            fts = self.KnowledgeSearchFTS(db_path="./data/knowledge_fts.db")
            
            # 3. 添加到 ChromaDB
            logger.info(f"正在保存 {len(knowledge_items)} 个知识条目到 ChromaDB...")
            chroma_count = index.add_documents(knowledge_items, auto_generate=auto_generate_embedding)
            
            # 4. 添加到 FTS5
            logger.info(f"正在保存 {len(knowledge_items)} 个知识条目到 FTS5...")
            fts_docs = [
                {
                    "content": item["content"],
                    "title": item.get("metadata", {}).get("title", ""),
                    "tags": item.get("metadata", {}).get("tags", ""),
                    "source": item.get("metadata", {}).get("source", ""),
                    "metadata": item.get("metadata", {})
                }
                for item in knowledge_items
            ]
            fts_count = fts.add_documents(fts_docs)
            fts.close()
            
            # 5. 返回统计
            result = {
                "success": True,
                "topic": topic,
                "knowledge_items": len(knowledge_items),
                "chroma_count": chroma_count,
                "fts_count": fts_count,
                "timestamp": datetime.now().isoformat(),
                "message": f"✅ 学习结果已保存到知识库：{chroma_count} 条 ChromaDB, {fts_count} 条 FTS5"
            }
            
            logger.info(result["message"])
            return result
            
        except Exception as e:
            logger.error(f"❌ 保存学习结果失败：{e}")
            return {
                "success": False,
                "topic": topic,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "message": f"❌ 保存失败：{str(e)}"
            }
    
    def _prepare_knowledge_items(
        self,
        topic: str,
        learning_data: List[Dict[str, Any]],
        source: str
    ) -> List[Dict]:
        """
        准备知识条目
        
        Args:
            topic: 学习主题
            learning_data: 学习结果
            source: 来源标识
        
        Returns:
            知识条目列表
        """
        knowledge_items = []
        
        for i, data in enumerate(learning_data):
            perspective = data.get("perspective", "unknown")
            result = data.get("result", "")
            timestamp = data.get("timestamp", "")
            
            # 构建内容
            content = f"""# {topic}

## 视角 {i+1}: {perspective.capitalize()}

{result}

---
*学习时间：{timestamp}*
*来源：{source}*
"""
            
            # 构建元数据
            metadata = {
                "title": f"{topic} - {perspective}视角",
                "tags": f"{topic},{perspective},v2_learning",
                "source": source,
                "topic": topic,
                "perspective": perspective,
                "learning_time": timestamp,
                "item_index": i + 1,
                "total_items": len(learning_data)
            }
            
            knowledge_items.append({
                "content": content,
                "metadata": metadata
            })
        
        logger.info(f"已准备 {len(knowledge_items)} 个知识条目")
        return knowledge_items
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """
        搜索知识库（快速查询）
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        self._ensure_initialized()
        
        try:
            fts = self.KnowledgeSearchFTS(db_path="./data/knowledge_fts.db")
            results = fts.search(query=query, limit=limit, highlight=True)
            fts.close()
            return results
        except Exception as e:
            logger.error(f"搜索失败：{e}")
            return []


# 使用示例
async def main():
    """测试知识库集成"""
    print("=" * 80)
    print("🧪 知识库集成测试")
    print("=" * 80)
    
    # 1. 初始化集成器
    kb = KnowledgeBaseIntegration()
    
    # 2. 模拟学习结果
    topic = "Python 编程语言"
    learning_data = [
        {
            "perspective": "technical",
            "result": "Python 是一种高级、解释型、通用编程语言，由 Guido van Rossum 于 1991 年创建。",
            "timestamp": "2026-02-18T19:00:00"
        },
        {
            "perspective": "practical",
            "result": "Python 广泛应用于 Web 开发、数据分析、人工智能、自动化脚本等领域。",
            "timestamp": "2026-02-18T19:01:00"
        }
    ]
    
    # 3. 保存到知识库
    print(f"\n📚 保存学习结果：{topic}")
    result = await kb.save_learning_result(topic, learning_data)
    
    if result["success"]:
        print(f"\n✅ {result['message']}")
    else:
        print(f"\n❌ {result['message']}")
    
    # 4. 搜索测试
    print(f"\n🔍 搜索 'Python'...")
    search_results = kb.search_knowledge("Python", limit=3)
    
    if search_results:
        print(f"✅ 找到 {len(search_results)} 条结果")
        for i, res in enumerate(search_results, 1):
            title = res.get("title", "")
            content = res.get("content", "")[:100]
            print(f"\n{i}. {title}")
            print(f"   {content}...")
    else:
        print("❌ 未找到结果")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
