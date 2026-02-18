"""
示例：使用NVIDIA API进行学习（与OpenClaw相同的LLM）

优势：
- ✅ 使用OpenClaw相同的LLM（z-ai/glm4.7）
- ✅ 零额外成本（复用NVIDIA API）
- ✅ 3个Worker + 缓存（降低限流风险）

配置：
从 openclaw.cherry.json 读取配置，无需手动配置
"""
import asyncio
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_engine import V2LearningSystem
from llm import OpenAIProvider, CachedLLMProvider


async def main():
    """主程序 - 使用NVIDIA API（与OpenClaw相同的LLM）"""
    print("="*70)
    print("🎓 V2学习系统示例 - 使用NVIDIA API")
    print("="*70)
    print("\n✅ 使用OpenClaw相同的LLM（z-ai/glm4.7）")
    print("✅ 无需配置API密钥（自动读取）")
    print("✅ 零成本，立即可用\n")

    # 从配置文件读取
    config_path = "C:/Users/10952/.openclaw/openclaw.cherry.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 提取配置
    provider_config = config["models"]["providers"]["cherry-nvidia"]
    api_key = provider_config["apiKey"]
    base_url = provider_config["baseUrl"]
    model_id = "z-ai/glm4.7"  # 模型ID（不是完整的cherry-nvidia/z-ai/glm4.7）

    print(f"配置信息：")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model_id}")
    print(f"  API Key: {api_key[:20]}...")

    # 创建NVIDIA提供者
    llm_provider = OpenAIProvider(
        api_key=api_key,
        base_url=base_url,
        model=model_id
    )

    # 创建带缓存的提供者（降低API调用频率）
    cached_provider = CachedLLMProvider(llm_provider)

    print("\n缓存统计：")
    stats = cached_provider.get_cache_stats()
    print(f"  当前缓存: {stats['total_entries']} 条")

    print("\n配置：")
    print("  Worker数量: 3（降低限流风险）")
    print("  缓存: 已启用（相同主题不重复调用）")
    print("\n开始学习...\n")

    # 创建学习系统（3个Worker + 缓存）
    learning_system = V2LearningSystem(
        num_workers=3,  # 使用3个Worker（降低风险）
        llm_provider=cached_provider  # 使用带缓存的提供者
    )

    # 启动并行学习
    # 可以更换为任何你想学习的主题
    await learning_system.start_parallel_learning("OpenClaw架构深度学习")

    print("\n💡 提示：")
    print("  - 学习历史已保存")
    print("  - 可以尝试学习其他主题")
    print("  - 系统会积累知识，越用越强")
    print("  - 相同主题会直接从缓存读取，不再调用API")


if __name__ == "__main__":
    asyncio.run(main())
