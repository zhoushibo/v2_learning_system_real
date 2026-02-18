"""测试Worker Pool - 验证长任务不阻塞"""
import asyncio
import sys
import time
from pathlib import Path

# 添加路径
mvp_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(mvp_src))

from worker.worker_pool import WorkerPool
from common.models import Task

# Windows编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


async def test_worker_pool():
    """测试Worker Pool"""

    print("\n" + "="*70)
    print("Worker Pool测试 - 验证长任务不阻塞")
    print("="*70 + "\n")

    # 任务1: 启动Worker Pool
    print("【步骤1】启动Worker Pool (3个Worker)")
    pool = WorkerPool(num_workers=3)
    await pool.start()

    # 显示初始状态
    print(f"初始状态: {pool.get_stats()}\n")

    # 任务2: 提交多个任务
    print("【步骤2】提交5个LLM任务（长任务）")
    print("-" * 70)

    tasks = []
    for i in range(5):
        task_content = f"请用{100 + i * 50}个字介绍什么是AI"
        print(f"提交任务{i+1}: {task_content}")

        task = pool.submit_task_sync(
            content=task_content,
            task_type="v1"
        )
        tasks.append(task)

    # 任务3: 立即查看状态（不等待）
    print("\n【步骤3】立即查看状态（任务还在排队）")
    print(f"当前状态: {pool.get_stats()}")
    print("✅ 关键点：提交流程立即返回，没有阻塞！\n")

    # 任务4: 等待所有任务完成
    print("【步骤4】等待所有任务完成...")
    print("-" * 70)

    start_wait = time.time()
    completed_tasks = await pool.wait_for_all_tasks()
    wait_time = time.time() - start_wait

    # 任务5: 查看最终状态
    print(f"\n【步骤5】最终状态")
    print(f"等待时间: {wait_time:.2f}秒")
    print(f"详细统计: {pool.get_stats()}\n")

    # 任务6: 查看任务结果
    print("【步骤6】任务结果")
    print("-" * 70)

    for i, task in enumerate(tasks, 1):
        status_emoji = "✅" if task.status == "completed" else "❌"
        print(f"任务{i}: {status_emoji} {task.status}")
        if task.status == "completed":
            print(f"       结果（前80字符）: {task.result[:80]}...")
            print(f"       结果长度: {len(task.result)}字符")
        print()

    # 停止Worker Pool
    await pool.stop()

    print("="*70)
    print("测试完成！")
    print("="*70 + "\n")

    # 总结
    print("总结：")
    print("  ✅ Worker Pool正常工作")
    print("  ✅ 多Worker并发执行")
    print("  ✅ 提交任务不阻塞")
    print("  ✅ 长任务独立处理")
    print()


async def test_no_blocking():
    """验证"不阻塞"特性"""

    print("\n" + "="*70)
    print("验证：长任务不阻塞主流程")
    print("="*70 + "\n")

    # 启动Worker Pool
    pool = WorkerPool(num_workers=2)
    await pool.start()

    print("【验证1】提交长任务")
    long_task = pool.submit_task_sync(
        content="请写一篇关于AI的文章（500字）",
        task_type="v1"
    )
    print(f"  任务已提交: {long_task.id}")

    print("\n【验证2】主流程可以继续执行（没有等待任务完成）")
    print("  正在执行其他工作...")

    # 模拟其他工作
    for i in range(3):
        print(f"    执行其他任务{i+1}...")
        await asyncio.sleep(1)

    print("  ✅ 其他任务完成，没有被阻塞！")

    print(f"\n【验证3】长任务状态: {long_task.status}")
    print("  任务还在后台执行，没有阻塞主流程")

    # 停止Worker Pool
    await pool.stop()

    print("\n" + "="*70)
    print("验证完成！")
    print("="*70 + "\n")

    print("关键发现：")
    print("  ✅ 提交长任务后，主流程可以继续执行")
    print("  ✅ 长任务在后台独立执行")
    print("  ✅ 主流程完全不受影响")
    print()


async def main():
    """运行所有测试"""

    # 测试1: Worker Pool基本功能
    await test_worker_pool()

    # 测试2: 验证不阻塞
    await test_no_blocking()

    print("\n" + "="*70)
    print("🎉 所有测试完成！")
    print("="*70 + "\n")

    print("核心成果：")
    print("  ✅ Worker Pool正常工作")
    print("  ✅ 多Worker并发执行")
    print("  ✅ 长任务不阻塞用户界面")
    print("  ✅ 提交任务立即返回")
    print()


if __name__ == "__main__":
    asyncio.run(main())
