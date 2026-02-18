"""
Semaphore和任务队列验证测试
验证Python asyncio并发控制和队列功能
"""
import asyncio
from typing import Set


async def worker(semaphore: asyncio.Semaphore, worker_id: int, completed: Set[int]):
    """工作协程"""
    async with semaphore:
        await asyncio.sleep(0.1)  # 模拟工作
        completed.add(worker_id)  # 标记完成


async def test_semaphore_basic():
    """基础Semaphore测试"""
    print("=== Semaphore基础测试 ===")

    # 创建信号量：最多2个并发
    sem = asyncio.Semaphore(2)
    completed = set()

    # 启动5个任务
    tasks = [worker(sem, i, completed) for i in range(5)]
    await asyncio.gather(*tasks)

    # 所有任务应该完成
    assert len(completed) == 5, f"应该完成5个任务，实际: {len(completed)}"
    assert completed == {0, 1, 2, 3, 4}, f"所有任务ID应该完成，实际: {completed}"

    print("✓ Semaphore基础测试通过")


async def test_semaphore_concurrent():
    """并发数量测试"""
    print("=== Semaphore并发数量测试 ===")

    sem = asyncio.Semaphore(3)  # 最多3个并发
    active_count = 0
    max_active = 0
    lock = asyncio.Lock()

    async def counted_worker(worker_id: int):
        nonlocal active_count, max_active
        async with sem:
            async with lock:
                active_count += 1
                max_active = max(max_active, active_count)
            await asyncio.sleep(0.2)
            async with lock:
                active_count -= 1

    # 启动10个任务
    tasks = [counted_worker(i) for i in range(10)]
    await asyncio.gather(*tasks)

    print(f"最大并发数: {max_active}")
    assert max_active <= 3, f"最大并发数应该 ≤ 3，实际: {max_active}"

    print("✓ Semaphore并发数量测试通过")


async def test_queue_basic():
    """基础队列测试"""
    print("=== 队列基础测试 ===")

    queue = asyncio.Queue()

    # 异步入队
    await queue.put("task1")
    await queue.put("task2")
    await queue.put("task3")

    # 检查队列大小
    assert queue.qsize() == 3

    # 异步出队
    assert await queue.get() == "task1"
    assert await queue.get() == "task2"
    assert await queue.get() == "task3"

    assert queue.qsize() == 0

    print("✓ 队列基础测试通过")


async def test_queue_priority():
    """优先级队列测试（通过多个队列实现）"""
    print("=== 优先级队列测试 ===")

    # 3个优先级队列
    high_queue = asyncio.Queue()
    medium_queue = asyncio.Queue()
    low_queue = asyncio.Queue()

    # 放入不同优先级的任务
    await high_queue.put("high1")
    await low_queue.put("low1")
    await medium_queue.put("medium1")
    await high_queue.put("high2")
    await low_queue.put("low2")

    # 优先出队：high > medium > low
    results = []

    # 先取出high
    results.append(await high_queue.get())
    results.append(await high_queue.get())

    # 再取medium
    results.append(await medium_queue.get())

    # 最后取low
    results.append(await low_queue.get())
    results.append(await low_queue.get())

    print(f"出队顺序: {results}")
    assert results == ["high1", "high2", "medium1", "low1", "low2"]

    print("✓ 优先级队列测试通过")


async def test_queue_timeout():
    """队列超时测试"""
    print("=== 队列超时测试 ===")

    queue = asyncio.Queue()

    # 尝试从空队列获取（带超时）
    try:
        result = await asyncio.wait_for(queue.get(), timeout=0.1)
        assert False, "应该超时"
    except asyncio.TimeoutError:
        print("✓ 队列超时正常")

    # 入队后应该能够获取
    await queue.put("task")
    result = await asyncio.wait_for(queue.get(), timeout=0.1)
    assert result == "task"

    print("✓ 队列超时测试通过")


async def main():
    """运行所有测试"""
    print("开始 Semaphore 和队列验证测试\n")

    await test_semaphore_basic()
    await test_semaphore_concurrent()
    await test_queue_basic()
    await test_queue_priority()
    await test_queue_timeout()

    print("\n=== 所有测试通过 ✓ ===")


if __name__ == "__main__":
    asyncio.run(main())
