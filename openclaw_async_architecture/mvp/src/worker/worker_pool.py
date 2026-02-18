"""
Worker Pool - 多Worker并发执行器
核心目标：长任务不阻塞
"""
import asyncio
import time
from typing import List, Optional
from ..common.models import Task
from .worker import V2Worker


class WorkerPool:
    """
    Worker Pool - 多Worker并发执行任务

    核心功能：
    - ✅ 多Worker并发（同时处理多个任务）
    - ✅ 任务队列（先进先出）
    - ✅ 长任务不阻塞（异步执行）
    - ✅ Worker复用（减少资源消耗）
    """

    def __init__(
        self,
        num_workers: int = 3,
        max_queue_size: int = 100
    ):
        """
        初始化Worker Pool

        Args:
            num_workers: Worker数量（并发能力）
            max_queue_size: 队列最大长度
        """
        self.num_workers = num_workers
        self.max_queue_size = max_queue_size

        # 任务队列
        self.task_queue: asyncio.Queue[Optional[Task]] = asyncio.Queue(maxsize=max_queue_size)

        # Worker列表
        self.workers: List[V2Worker] = []

        # 运行状态
        self.running = False

        # 统计信息
        self.stats = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_workers": num_workers
        }

    async def start(self):
        """启动Worker Pool"""
        if self.running:
            print("[WorkerPool] 已经在运行")
            return

        print(f"[WorkerPool] 启动 {self.num_workers} 个Worker...")

        # 创建多个Worker
        self.workers = [V2Worker() for _ in range(self.num_workers)]

        # 启动Worker任务
        self.worker_tasks = [
            asyncio.create_task(self._worker_loop(worker, f"worker-{i+1}"))
            for i, worker in enumerate(self.workers)
        ]

        self.running = True
        print(f"[WorkerPool] ✅ {self.num_workers} 个Worker已启动")

    async def stop(self):
        """停止Worker Pool"""
        if not self.running:
            return

        print("[WorkerPool] 停止Worker Pool...")

        # 发送停止信号
        for _ in range(self.num_workers):
            await self.task_queue.put(None)

        # 等待Worker完成
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)

        # 关闭Worker
        for worker in self.workers:
            await worker.close()

        self.running = False
        print("[WorkerPool] ✅ Worker Pool已停止")

    async def submit_task(
        self,
        content: str,
        task_type: str = "v1",
        **metadata
    ) -> Task:
        """
        提交任务到队列（异步，不阻塞）

        Args:
            content: 任务内容
            task_type: 任务类型
            metadata: 额外元数据

        Returns:
            Task对象
        """
        if not self.running:
            raise RuntimeError("Worker Pool未启动")

        # 创建任务
        task = Task(content=content, metadata={"task_type": task_type, **metadata})

        # 提交到队列（异步，不阻塞）
        await self.task_queue.put(task)

        # 更新统计
        self.stats["tasks_submitted"] += 1

        print(f"[WorkerPool] 任务已提交: {task.id} (队列长度: {self.task_queue.qsize()})")

        return task

    def submit_task_sync(
        self,
        content: str,
        task_type: str = "v1",
        **metadata
    ) -> Task:
        """
        提交任务到队列（同步，快速返回）

        Args:
            content: 任务内容
            task_type: 任务类型
            metadata: 额外元数据

        Returns:
            Task对象（异步执行）
        """
        if not self.running:
            raise RuntimeError("Worker Pool未启动")

        # 创建任务
        task = Task(content=content, metadata={"task_type": task_type, **metadata})

        # 提交到队列（非阻塞）
        try:
            self.task_queue.put_nowait(task)
        except asyncio.QueueFull:
            raise RuntimeError("任务队列已满")

        # 更新统计
        self.stats["tasks_submitted"] += 1

        print(f"[WorkerPool] 任务已提交: {task.id} (队列长度: {self.task_queue.qsize()})")

        return task

    async def wait_for_task(self, task: Task, timeout: float = 300.0) -> Task:
        """
        等待特定任务完成

        Args:
            task: 任务对象
            timeout: 超时时间

        Returns:
            完成的Task对象
        """
        # 轮询检查任务状态
        start_time = time.time()

        while True:
            if task.status in ["completed", "failed"]:
                return task

            if time.time() - start_time > timeout:
                raise TimeoutError(f"任务超时: {task.id}")

            await asyncio.sleep(0.5)

    async def wait_for_all_tasks(self, timeout: float = 3600.0) -> List[Task]:
        """
        等待所有任务完成

        Args:
            timeout: 超时时间

        Returns:
            完成的任务列表
        """
        # 等待队列为空
        start_time = time.time()

        while True:
            if self.task_queue.empty():
                # 等待所有Worker空闲
                await asyncio.sleep(1)
                print(f"[WorkerPool] 等待所有任务完成... (队列: {self.task_queue.qsize()})")
                break

            if time.time() - start_time > timeout:
                raise TimeoutError("所有任务超时")

            await asyncio.sleep(1)

        return []

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            "queue_size": self.task_queue.qsize(),
            "running": self.running
        }

    async def _worker_loop(self, worker: V2Worker, worker_name: str):
        """
        Worker循环（每个Worker）

        Args:
            worker: Worker实例
            worker_name: Worker名称
        """
        print(f"[{worker_name}] Worker启动")

        while True:
            # 从队列获取任务
            task = await self.task_queue.get()

            # 停止信号
            if task is None:
                print(f"[{worker_name}] 停止信号")
                break

            # 执行任务
            try:
                print(f"[{worker_name}] 处理任务: {task.id}")
                task = await worker.execute_task(task)

                # 更新统计
                if task.status == "completed":
                    self.stats["tasks_completed"] += 1
                else:
                    self.stats["tasks_failed"] += 1

            except Exception as e:
                print(f"[{worker_name}] 任务执行错误: {e}")
                task.status = "failed"
                task.error = str(e)
                self.stats["tasks_failed"] += 1

            finally:
                # 标记任务完成
                self.task_queue.task_done()

        print(f"[{worker_name}] Worker停止")


# 便捷函数
async def create_worker_pool(num_workers: int = 3) -> WorkerPool:
    """创建并启动Worker Pool"""
    pool = WorkerPool(num_workers=num_workers)
    await pool.start()
    return pool


# 测试
if __name__ == "__main__":
    import sys

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    async def test():
        print("\n" + "="*70)
        print("Worker Pool测试")
        print("="*70 + "\n")

        # 创建Worker Pool（3个Worker）
        pool = await create_worker_pool(num_workers=3)

        # 提交多个任务
        print("提交5个任务...")

        tasks = []
        for i in range(5):
            task_content = f"你好，这是第{i+1}个任务"
            task = pool.submit_task_sync(task_content)
            tasks.append(task)

        # 查看统计
        print(f"\n提交完成: {pool.get_stats()}")

        # 等待所有任务完成
        print("\n等待所有任务完成...")
        await pool.wait_for_all_tasks()

        # 最终统计
        print(f"\n最终统计: {pool.get_stats()}")

        # 查看任务结果
        print("\n任务结果:")
        for i, task in enumerate(tasks, 1):
            status_emoji = "✅" if task.status == "completed" else "❌"
            print(f"  任务{i}: {status_emoji} {task.status}")
            if task.status == "completed":
                print(f"         结果（前50字符）: {task.result[:50]}...")

        # 停止Pool
        await pool.stop()

        print("\n" + "="*70)
        print("测试完成！")
        print("="*70 + "\n")

    asyncio.run(test())
