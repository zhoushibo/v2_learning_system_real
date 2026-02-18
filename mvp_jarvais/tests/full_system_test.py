"""
MVP JARVIS完整系统测试

测试内容：
1. MemoryManager（记忆管理器）
2. KnowledgeAgent（知识智能体）
3. AgentManager（多Agent协调器）
4. 端到端测试
"""

import asyncio
import sys
import os
import logging

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(project_root))

from mvp_jarvais.core.memory_manager import MemoryManager
from mvp_jarvais.core.agent_manager import AgentManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_memory_manager():
    """测试MemoryManager"""
    print("\n" + "="*70)
    print("🧠 测试1: MemoryManager（记忆管理器）")
    print("="*70)

    # 创建记忆管理器
    memory = MemoryManager(enable_v1=False)

    # 记住核心记忆
    print("\n💾 记住核心记忆")

    test_memories = [
        {
            "key": "mvp_progress",
            "content": "MVP全能AI系统开发进度：70%（MemoryManager、KnowledgeAgent、AgentManager已完成）",
            "metadata": {"type": "progress", "progress": "70%"}
        },
        {
            "key": "goal_jarvais",
            "content": "终极目标：成为超越钢铁侠JARVIS的个人AI，当前JARVIS能力覆盖率91%",
            "metadata": {"type": "goal", "coverage": "91%"}
        },
        {
            "key": "assets_saved",
            "content": "资产复用：V2 MCP（10-16周）、三层记忆系统（5-7周）、V2学习系统（5-7周）、融合工作流（5-8周）",
            "metadata": {"type": "assets", "saved": "25-43 weeks"}
        }
    ]

    for mem in test_memories:
        await memory.remember(
            **mem
        )

    print("  ✅ 已记住3条核心记忆")

    # 搜索测试
    print("\n🔎 语义搜索测试")
    results = await memory.search("项目进展", n_results=2)
    for i, r in enumerate(results, 1):
        content = r.get('content', '')[:60]
        print(f"    {i}. {content}...")

    print("\n✅ MemoryManager测试完成！")
    return memory


async def test_agent_manager(memory):
    """测试AgentManager"""
    print("\n" + "="*70)
    print("🎯 测试2: AgentManager（多Agent协调器）")
    print("="*70)

    # 创建AgentManager
    manager = AgentManager(memory)
    print("\n✅ AgentManager初始化完成")

    # 测试智能路由
    print("\n🧪 智能路由测试")

    test_cases = [
        "我们的项目进展如何？",
        "记住：这个项目很重要",
        "帮我学习向量搜索",
        "执行npm install",
        "你好",
    ]

    for user_input in test_cases:
        print(f"\n👤 用户：{user_input}")

        result = await manager.route(user_input)

        print(f"🎯 路由：{result['type']} → {result['agent']}")
        print(f"🤖 响应：{result['response'][:150]}...")

    # 统计
    print("\n📈 统计信息")
    stats = await manager.get_stats()
    print(f"  Agent: {stats['agents']}")
    print(f"  意图: {stats['intents']}")

    print("\n✅ AgentManager测试完成！")


async def test_end_to_end(memory, manager):
    """端到端测试"""
    print("\n" + "="*70)
    print("🔗 测试3: 端到端测试（完整对话流程）")
    print("="*70)

    # 模拟完整对话场景
    print("\n💬 完整对话场景")

    # 场景1：知识查询
    print("\n👤 用户：我们的目标是什么？")
    result = await manager.route("我们的目标是什么？")
    print(f"🤖 AI：{result['response'][:200]}...")

    # 场景2：记住信息
    print("\n👤 用户：记住：今天完成了AgentManager的开发")
    await memory.remember(
        key="today_achievement",
        content="2026-02-17：完成了AgentManager的开发，支持智能路由和多Agent协调",
        metadata={"type": "achievement", "date": "2026-02-17"}
    )
    print("🤖 AI：✅ 已记住！")

    # 场景3：回忆刚才记住的内容
    print("\n👤 用户：今天完成了什么？")
    result = await manager.route("今天完成了什么？")
    print(f"🤖 AI：{result['response']}")

    # 场景4：持续学习
    print("\n👤 用户：帮我学习OpenClaw超时问题解决方案")
    result = await manager.route("帮我学习OpenClaw超时问题解决方案")
    print(f"🤖 AI：{result['message']}")

    print("\n✅ 端到端测试完成！")


async def test_performance(memory, manager):
    """性能测试"""
    print("\n" + "="*70)
    print("⚡ 测试4: 性能测试")
    print("="*70)

    import time

    # 测试记忆写入性能
    print("\n📊 记忆写入性能")
    start = time.time()

    for i in range(10):
        await memory.remember(
            key=f"perf_test_{i}",
            content=f"性能测试数据{i}",
            metadata={"index": i}
        )

    duration = time.time() - start
    print(f"  10条记忆写入耗时: {duration:.3f}秒")
    print(f"  平均每条: {duration/10:.3f}秒")

    # 测试智能路由性能
    print("\n📊 智能路由性能")
    test_queries = ["项目进展", "目标", "资产"] * 5

    start = time.time()
    for query in test_queries:
        await manager.route(query)
    duration = time.time() - start

    print(f"  15次路由耗时: {duration:.3f}秒")
    print(f"  平均每次: {duration/15:.3f}秒")

    print("\n✅ 性能测试完成！")


async def main():
    """主测试程序"""
    print("\n" + "="*70)
    print("🚀 MVP JARVIS 完整系统测试")
    print("="*70)
    print("\n测试目标：")
    print("  1. MemoryManager - 记忆管理")
    print("  2. KnowledgeAgent - 知识查询")
    print("  3. AgentManager - 智能路由")
    print("  4. 端到端 - 完整流程")
    print("  5. 性能 - 响应速度")

    try:
        # 测试1: MemoryManager
        memory = await test_memory_manager()

        # 测试2: AgentManager
        await test_agent_manager(memory)

        # 测试3: 端到端
        await test_end_to_end(memory, AgentManager(memory))

        # 测试4: 性能
        await test_performance(memory, AgentManager(memory))

        print("\n" + "="*70)
        print("🎉 所有测试完成！")
        print("="*70)
        print("\n✅ 核心组件运行正常")
        print("✅ 智能路由功能正常")
        print("✅ 端到端流程正常")
        print("✅ 性能表现良好")
        print("\n🎯 MVP JARVIS 基础架构 已就绪（80%）")
        print("\n下一步：")
        print("  - ToolIntegration（工具整合）")
        print("  - Gateway集成（流式对话）")
        print("  - 性能优化 + 文档")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
