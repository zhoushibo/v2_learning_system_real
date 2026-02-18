"""
学习：三层记忆系统集成到MVP全能AI系统

使用V2学习系统（NVIDIA API + 缓存）
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, "v2_learning_system_real")

from learning_engine import V2LearningSystem
from llm import OpenAIProvider, CachedLLMProvider


async def main():
    """主程序"""
    print("="*70)
    print("🎓 V2学习系统 - 三层记忆系统集成")
    print("="*70)

    # 从配置文件读取
    config_path = "C:/Users/10952/.openclaw/openclaw.cherry.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 提取配置
    provider_config = config["models"]["providers"]["cherry-nvidia"]
    api_key = provider_config["apiKey"]
    base_url = provider_config["baseUrl"]
    model_id = "z-ai/glm4.7"

    print(f"\n配置：")
    print(f"  Model: {model_id}")
    print(f"  Worker数量: 3")
    print(f"  缓存: 已启用")

    # 创建提供者
    llm_provider = OpenAIProvider(
        api_key=api_key,
        base_url=base_url,
        model=model_id
    )

    # 带缓存
    cached_provider = CachedLLMProvider(llm_provider)

    # 创建学习系统
    learning_system = V2LearningSystem(
        num_workers=3,
        llm_provider=cached_provider
    )

    # 学习主题
    topic = """
三层记忆系统集成到MVP全能AI系统

现有资产：
1. V1三层记忆系统 - SQLite + ChromaDB + Redis
   - L1: Redis缓存（最快）
   - L2: ChromaDB向量搜索（语义检索）
   - L3: SQLite持久化存储（最可靠）
   - 代码位置: openclaw_async_architecture/mvp/src/common/v1_memory_integration.py

2. V2 MCP系统
   - Worker Pool（3个Worker并发）
   - Gateway流式对话
   - exec自主工具
   - V2学习系统

3. V2 CLI MVP（OpenClaw替代品）

4. 融合工作流系统

集成目标：
- 将三层记忆系统集成到MVP全能 AI 系统
- Agent系统可以调用记忆系统
- Gateway流式对话可以检索记忆
- 支持上下文回忆和知识问答

请学习如何设计集成架构、API接口、调用流程。
"""

    print(f"\n学习主题：三层记忆系统集成")
    print(f"主题长度：{len(topic)} 字符")
    print(f"\n开始学习...\n")

    # 并行学习
    await learning_system.start_parallel_learning(topic)

    print("\n✅ 学习完成！")
    print("  学习历史已保存到 memory/v2_learning_history.json")
    print("  可以根据学习结果制定集成架构")


if __name__ == "__main__":
    asyncio.run(main())
