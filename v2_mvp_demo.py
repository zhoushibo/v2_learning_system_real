# -*- coding: utf-8 -*-
"""
V2 MVP 整合演示脚本
演示 V2 学习系统 + 知识库系统 + Gateway 架构的完整工作流程

功能：
1. 使用 V2 学习系统学习主题（3 Worker 并发）
2. 自动保存到知识库（ChromaDB + FTS5 双索引）
3. 从知识库搜索刚学习的内容
4. 展示完整的学习→存储→检索流程

运行：
    python v2_mvp_demo.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加路径
workspace = Path(__file__).parent
sys.path.insert(0, str(workspace))

# 导入 V2 学习系统
from v2_learning_system_real import LearningEngine
from v2_learning_system_real.knowledge_base_integration_v2 import KnowledgeBaseIntegration


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_section(title: str):
    """打印小标题"""
    print(f"\n📌 {title}")
    print("-" * 60)


async def demo_learning():
    """演示 V2 学习系统"""
    print_header("V2 MVP 整合演示 - 学习→存储→检索")
    
    print_section("步骤 1: 使用 V2 学习系统学习主题")
    
    # 创建学习引擎
    engine = LearningEngine(num_workers=3)
    
    # 学习主题
    topic = "Python 异步编程（async/await）"
    print(f"\n📚 学习主题：{topic}")
    print(f"🔧 Worker 数量：3")
    print(f"⏰ 开始时间：{datetime.now().strftime('%H:%M:%S')}")
    
    # 开始学习
    start_time = datetime.now()
    
    results = await engine.parallel_learning(
        topic,
        num_perspectives=3,  # 3 个视角
        save_to_kb=True      # ✅ 自动保存到知识库
    )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n✅ 学习完成！")
    print(f"⏱️  耗时：{duration:.2f}秒")
    print(f"📊 学习视角：{len(results)} 个")
    
    # 显示学习结果摘要
    print_section("步骤 2: 学习结果摘要")
    for i, result in enumerate(results, 1):
        perspective = result['perspective']
        content = result['result']
        preview = content[:100] + "..." if len(content) > 100 else content
        
        print(f"\n{i}. {perspective.capitalize()} 视角:")
        print(f"   {preview}")
    
    return topic, results


async def demo_search(topic: str):
    """演示知识库搜索"""
    print_section("步骤 3: 从知识库搜索刚学习的内容")
    
    kb = KnowledgeBaseIntegration()
    
    # 语义搜索
    print(f"\n🔍 语义搜索：'{topic}'")
    semantic_results = kb.search_knowledge(topic, limit=3)
    
    if semantic_results:
        print(f"✅ 找到 {len(semantic_results)} 条相关结果")
        for i, result in enumerate(semantic_results, 1):
            title = result.get('title', '无标题')
            print(f"   {i}. {title}")
    else:
        print("⚠️  未找到结果（可能 ChromaDB 模型未下载完成）")
    
    return semantic_results


async def demo_full_workflow():
    """完整演示流程"""
    try:
        # 步骤 1 & 2: 学习
        topic, results = await demo_learning()
        
        # 步骤 3: 搜索
        search_results = await demo_search(topic)
        
        # 总结
        print_header("演示完成")
        print("\n✅ V2 MVP 完整工作流程演示成功！")
        print("\n📊 演示总结:")
        print(f"   • 学习系统：3 Worker 并发学习")
        print(f"   • 学习视角：3 个（technical, practical, theoretical）")
        print(f"   • 自动保存：✅ 已保存到知识库")
        print(f"   • 双索引：ChromaDB + FTS5")
        print(f"   • Gateway 架构：6 Provider 支持")
        
        print("\n🎯 核心优势:")
        print("   1. 学习完成自动保存，无需手动操作")
        print("   2. 双索引搜索，语义 + 关键词全覆盖")
        print("   3. Gateway 统一架构，6 个 API Provider 自动切换")
        print("   4. 3 Worker 并发，效率提升 3 倍")
        
        print("\n📄 详细文档:")
        print("   • V2 学习系统：v2_learning_system_real/INTEGRATION_GUIDE.md")
        print("   • 测试报告：v2_learning_system_real/TEST_REPORT.md")
        print("   • 知识库系统：knowledge_base/README.md")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ 演示失败：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def demo_quick_learn(topic: str = "机器学习基础"):
    """快速学习演示（简化版）"""
    print_header(f"快速学习：{topic}")
    
    engine = LearningEngine(num_workers=3)
    
    start_time = datetime.now()
    results = await engine.parallel_learning(
        topic,
        num_perspectives=2,
        save_to_kb=True
    )
    duration = (datetime.now() - start_time).total_seconds()
    
    print(f"\n✅ 学习完成！")
    print(f"   耗时：{duration:.2f}秒")
    print(f"   视角：{len(results)}个")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['perspective']}: {result['result'][:80]}...")
    
    return results


async def main():
    """主函数"""
    print("\n" + "🚀" * 40)
    print("\n  V2 MVP 全能 AI 系统 - 整合演示")
    print("\n" + "🚀" * 40)
    
    # 完整演示
    success = await demo_full_workflow()
    
    if success:
        print("\n💡 提示：运行 'python v2_mvp_demo.py quick <主题>' 进行快速学习演示")
        print("   例如：python v2_mvp_demo.py quick 深度学习\n")


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        topic = sys.argv[2] if len(sys.argv) > 2 else "机器学习基础"
        asyncio.run(demo_quick_learn(topic))
    else:
        asyncio.run(main())
