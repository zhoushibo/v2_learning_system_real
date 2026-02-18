"""
V2 CLI系统 - Phase 2: V2学习系统学习

学习主题：
1. prompt_toolkit库使用（10分钟）
2. rich库使用（5分钟）
3. 异步编程最佳实践（10分钟）
4. CLI命令模式设计（5分钟）

预计时间：30分钟
"""
import asyncio
import json
from pathlib import Path
import sys

# 添加V2学习系统路径（同级目录）
sys.path.insert(0, str(Path(__file__).parent.parent / "v2_learning_system_real"))

from learning_engine import LearningEngine, LearningTask

async def phase2_learning():
    """Phase 2: 学习项目相关技术"""

    print("=" * 60)
    print("Phase 2: V2 CLI系统技术学习")
    print("=" * 60)
    print()

    # 读取配置
    with open("C:/Users/10952/.openclaw/openclaw.cherry.json", 'r', encoding='utf-8') as f:
        config = json.load(f)

    provider_config = config["models"]["providers"]["cherry-nvidia"]
    api_key = provider_config["apiKey"]
    base_url = provider_config["baseUrl"]

    # 创建LLM提供者
    from llm import OpenAIProvider

    llm_provider = OpenAIProvider(
        api_key=api_key,
        base_url=base_url,
        model="z-ai/glm4.7",
        timeout=180
    )

    # 创建学习引擎
    learning_engine = LearningEngine(
        llm_provider=llm_provider,
        learning_style="deep_analysis"
    )

    # 学习主题集合
    learning_tasks = [
        {
            "id": "task1",
            "topic": "Python CLI开发：prompt_toolkit库核心API和使用方法",
            "worker_id": "worker1"
        },
        {
            "id": "task2",
            "topic": "Python终端美化：rich库的使用方法和最佳实践",
            "worker_id": "worker2"
        },
        {
            "id": "task3",
            "topic": "Python异步编程：asyncio最佳实践和常见陷阱",
            "worker_id": "worker3"
        },
        {
            "id": "task4",
            "topic": "CLI命令模式设计：命令解析、参数处理、路由设计",
            "worker_id": "worker4"
        },
        {
            "id": "task5",
            "topic": "V2 CLI系统：如何集成V2MCP、Gateway、WorkerPool等现有资产",
            "worker_id": "worker5"
        }
    ]

    print(f"准备学习 {len(learning_tasks)} 个主题...\n")

    # 提交多个学习任务并并行执行
    tasks = []
    for task_info in learning_tasks:
        task = await learning_engine.submit_learning_task(
            topic=task_info["topic"],
            worker_id=task_info["worker_id"]
        )
        tasks.append(task)

    # 并行执行所有学习任务
    print("开始并行学习（5个Worker）...\n")
    print("-" * 60)

    # 创建协程列表并并行执行
    learning_coroutines = [learning_engine.execute_learning(task) for task in tasks]
    results = await asyncio.gather(*learning_coroutines)

    # 将结果转换为字典（按task id）
    result_dict = {task.id: task for task in results}

    print("\n" + "=" * 60)
    print("学习完成！")
    print("=" * 60)
    print()

    # 输出学习总结
    print("📚 学习总结：\n")

    for task_id, task in result_dict.items():
        print(f"任务 {task_id}: {task.topic}")
        print(f"  Worker: {task.worker_id}")
        print(f"  状态: {task.status}")
        print(f"  知识点数量: {len(task.key_points)}")
        print(f"  建议数量: {len(task.recommendations)}")

        if task.key_points:
            print(f"  关键知识点（前3个）:")
            for kp in task.key_points[:3]:
                print(f"    - {kp}")

        print()

    # 保存学习结果
    output_file = "v2_cli_phase2_learning_result.json"
    learning_data = {
        "timestamp": str(asyncio.get_event_loop().time()),
        "tasks": {tid: task.to_dict() for tid, task in result_dict.items()}
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(learning_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 学习结果已保存到: {output_file}")

    return results

if __name__ == "__main__":
    asyncio.run(phase2_learning())
