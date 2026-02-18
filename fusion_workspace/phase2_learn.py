"""
Phase 2: V2学习系统学习 - V2 CLI系统开发

学习主题：
1. prompt_toolkit库使用（10分钟）
2. rich库使用（5分钟）
3. 异步编程最佳实践（10分钟）
4. CLI命令模式设计（5分钟）

总时间：30分钟
"""

import asyncio
import sys
import os

# 添加v2_learning_system_real到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'v2_learning_system_real'))

from learning_engine import V2LearningSystem


async def learn_for_cli_development():
    """为V2 CLI开发学习相关知识"""

    print("\n" + "="*70)
    print("🎓 Phase 2: V2学习系统学习 - V2 CLI系统开发")
    print("="*70)

    # 创建学习系统（5个Worker并行）
    learning_system = V2LearningSystem(num_workers=5)

    # 学习主题列表
    print("\n📚 学习主题：")
    print("  1. prompt_toolkit库使用（10分钟）")
    print("  2. rich库使用（5分钟）")
    print("  3. 异步编程最佳实践（10分钟）")
    print("  4. CLI命令模式设计（5分钟）")
    print("\n总时间：约30分钟\n")

    # 5个Worker并行学习4个主题
    # 根据Phase 1专家会议的分配
    topics = [
        ("prompt_toolkit库基础使用", "worker-1"),
        ("prompt_toolkit高级特性", "worker-2"),
        ("rich库使用和美化输出", "worker-3"),
        ("Python异步编程最佳实践", "worker-4"),
        ("CLI命令模式设计和用户体验", "worker-5"),
    ]

    print("="*70)
    print("🚀 启动5个Worker并行学习...")
    print("="*70)

    # 启动并行学习
    results = await learning_system.start_parallel_learning(topics)

    # 返回结果
    return results


if __name__ == "__main__":
    results = asyncio.run(learn_for_cli_development())

    print("\n💡 下一步（Phase 3）：资产复用评估（10分钟）")
    print("  - 确认V2 MCP复用清单")
    print("  - 确认新开发范围")
