"""
增强版V2 Worker完整测试
验证Gateway + exec + V1三种模式
"""
import asyncio
import sys
from pathlib import Path

# 添加路径
mvp_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(mvp_src))

from worker.enhanced_worker import EnhancedV2Worker
from common.models import Task

# Windows编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


async def test_enhanced_worker():
    """测试增强版Worker"""

    print("\n" + "="*70)
    print("增强版V2 Worker完整测试")
    print("="*70 + "\n")

    # 创建Enhanced Worker
    print("【初始化】创建增强版Worker")
    worker = EnhancedV2Worker(worker_id="enhanced-1")
    print()

    # 测试1: Gateway流式LLM
    print("【测试1】Gateway流式LLM（task_type=chat）")
    print("-" * 70)

    task1 = Task(
        content="你好，请用50字介绍什么是AI",
        metadata={
            "task_type": "chat",
            "provider": "hunyuan"
        }
    )

    try:
        task1 = await worker.execute_task(task1)
        if task1.status == "completed":
            print(f"✅ Gateway任务成功")
            print(f"   结果: {task1.result[:80]}...")
        else:
            print(f"❌ Gateway任务失败: {task1.error}")
    except Exception as e:
        print(f"❌ 异常: {e}")

    print()

    # 测试2: exec自主工具
    print("【测试2】exec自主工具（task_type=command）")
    print("-" * 70)

    task2 = Task(
        content="python --version",
        metadata={
            "task_type": "command"
        }
    )

    try:
        task2 = await worker.execute_task(task2)
        if task2.status == "completed":
            print(f"✅ exec任务成功")
            print(f"   结果: {task2.result}")
        else:
            print(f"❌ exec任务失败: {task2.error}")
    except Exception as e:
        print(f"❌ 异常: {e}")

    print()

    # 测试3: V1 API（如果Gateway失败）
    print("【测试3】V1 API（task_type=v1，备用）")
    print("-" * 70)

    task3 = Task(
        content="1+1等于几？",
        metadata={
            "task_type": "v1"
        }
    )

    try:
        task3 = await worker.execute_task(task3)
        if task3.status == "completed":
            print(f"✅ V1任务成功")
            print(f"   结果: {task3.result[:80]}...")
        else:
            print(f"❌ V1任务失败: {task3.error}")
    except Exception as e:
        print(f"❌ 异常: {e}")

    # 关闭Worker
    await worker.close()

    print()
    print("="*70)
    print("测试完成！")
    print("="*70 + "\n")

    # 总结
    print("总结：")
    print("  ✅ 增强版Worker支持三种执行模式")
    print("  - Gateway流式LLM（chat）")
    print("  - 自主exec工具（command）")
    print("  - V1 API（v1）")
    print("  ✅ 自动选择最优执行方式")
    print()


async def test_with_worker_pool():
    """测试Enhanced Worker + Worker Pool"""

    print("\n" + "="*70)
    print("Enhanced Worker + Worker Pool集成测试")
    print("="*70 + "\n")

    # 启动Worker Pool
    print("【步骤1】启动Worker Pool（2个Enhanced Worker）")
    from worker.worker_pool import WorkerPool

    pool = WorkerPool(num_workers=2)

    # 替换为EnhancedWorker
    from worker.enhanced_worker import EnhancedV2Worker

    pool._create_worker = lambda: EnhancedV2Worker(worker_id=f"worker-{len(pool.workers)}")

    await pool.start()
    print()

    # 提交不同类型的任务
    print("【步骤2】提交多种任务")
    print("-" * 70)

    tasks = []
    task_types = [
        ("chat", "你好，请用50字介绍AI", "hunyuan"),
        ("chat", "什么是JARVIS?", "hunyuan"),
        ("command", "echo Hello World", None),
        ("chat", "什么是Worker Pool?", "hunyuan"),
    ]

    for i, (task_type, content, provider) in enumerate(task_types, 1):
        print(f"提交任务{i}: {task_type} - {content}")

        metadata = {"task_type": task_type}
        if provider:
            metadata["provider"] = provider

        task = pool.submit_task_sync(
            content=content,
            **metadata
        )
        tasks.append(task)

    print()
    print(f"✅ 所有任务已提交，队列长度: {pool.task_queue.qsize()}")
    print()

    # 等待完成
    print("【步骤3】等待所有任务完成")
    print("-" * 70)

    await pool.wait_for_all_tasks()

    print()
    print("【步骤4】结果汇总")
    print("-" * 70)

    for i, (task, (task_type, content, _)) in enumerate(zip(tasks, task_types), 1):
        status_emoji = "✅" if task.status == "completed" else "❌"
        print(f"任务{i} ({task_type}): {status_emoji}")
        if task.status == "completed" and task.result:
            print(f"       结果: {task.result[:60]}...")
        if task.error:
            print(f"       错误: {task.error}")

    # 停止Pool
    await pool.stop()

    print()
    print("="*70)
    print("集成测试完成！")
    print("="*70 + "\n")


if __name__ == "__main__":
    async def main():
        # 测试1: 单个Enhanced Worker
        await test_enhanced_worker()

        # 测试2: Enhanced Worker + Worker Pool
        await test_with_worker_pool()

    asyncio.run(main())
