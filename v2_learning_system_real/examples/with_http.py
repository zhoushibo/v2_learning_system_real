"""
示例：使用HTTP API进行学习（无需额外配置，直接使用现有LLM）

优势：
- ✅ 无需API密钥
- ✅ 直接使用OpenClaw的LLM
- ✅ 零成本
- ✅ 立即可用
"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_engine import V2LearningSystem
from llm import HTTPProvider


async def main():
    """主程序 - 使用HTTP API（直接复用OpenClaw的LLM）"""
    print("="*70)
    print("🎓 V2学习系统示例 - 使用HTTP API")
    print("="*70)
    print("\n✅ 无需配置API密钥")
    print("✅ 直接使用现有LLM（OpenClaw的cherry-nvidia/z-ai/glm4.7）")
    print("✅ 零成本，立即可用\n")

    # 创建HTTP提供者
    # API端点可以配置为OpenClaw的内部API
    llm_provider = HTTPProvider(
        api_endpoint="http://localhost:5000/api/chat",  # OpenClaw API端点（可配置）
        model="cherry-nvidia/z-ai/glm4.7"  # 模型名称
    )

    # 创建学习系统
    learning_system = V2LearningSystem(
        num_workers=5,
        llm_provider=llm_provider
    )

    # 启动并行学习
    # 可以更换为任何你想学习的主题
    await learning_system.start_parallel_learning("OpenClaw架构深度学习")

    print("\n💡 提示：")
    print("  - 学习历史已保存")
    print("  - 可以尝试学习其他主题")
    print("  - 系统会积累知识，越用越强")
    print("  - 无需任何配置，立即可用！")


if __name__ == "__main__":
    asyncio.run(main())
