"""Worker主进程 - 使用LoadBalancer增强版"""
import asyncio
from ..worker.enhanced_worker import get_enhanced_worker
from ..queue.redis_queue import RedisTaskQueue
from ..store.hybrid_store import HybridTaskStore
from ..common.config import settings
from ..common.models import Task


async def run_worker():
    """运行Worker进程（多模型增强版）"""
    print(f"\n{'='*60}")
    print(f"OpenClaw V2 Worker - 多模型增强版")
    print(f"{'='*60}")

    # 初始化组件
    worker = get_enhanced_worker()
    queue = RedisTaskQueue()
    store = HybridTaskStore()

    # 测试连接
    if not queue.test_connection():
        print(f"\n[X] Redis连接失败！")
        return

    # 测试存储连接
    storage_status = store.test_connection()
    print(f"\n[OK] Redis队列连接成功")
    print(f"[OK] 存储模式: {storage_status['storage_mode']}")

    print(f"\n[*] Worker开始监听Redis队列...")
    print(f"[路由] 5模型智能路由已就绪")
    print(f"{'='*60}\n")

    # 任务循环
    while True:
        try:
            # 从队列获取任务（阻塞5秒）
            task_data = queue.get_task(timeout=5)

            if task_data:
                task_id = task_data["task_id"]
                content = task_data["task_data"]

                # 创建任务对象
                task = Task(id=task_id, content=content)

                # 执行任务（使用LoadBalancer）
                task = await worker.execute_task(task)

                # 保存结果
                store.save_task(task)

                print(f"\n[Worker] [OK] 任务 {task_id} 完成: {task.status}")
            else:
                # 队列为空，继续等待
                pass

        except KeyboardInterrupt:
            print(f"\n\n[Worker] 收到停止信号，退出...")
            break
        except Exception as e:
            print(f"\n[Worker] [X] 错误: {e}")
            await asyncio.sleep(1)

    # 清理资源
    await worker.close()
    print(f"[Worker] Worker已停止\n")


if __name__ == "__main__":
    asyncio.run(run_worker())
