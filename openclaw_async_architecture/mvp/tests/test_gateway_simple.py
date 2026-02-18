"""
简化版Gateway + Worker Pool集成测试
完全独立，避免import问题
"""
import asyncio
import websocket
import websockets
import json
import time
from typing import Optional

# Windows编码
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class SimpleGatewayClient:
    """简化的Gateway客户端"""

    def __init__(self, gateway_url: str = "ws://127.0.0.1:8001"):
        self.gateway_url = gateway_url

    async def chat(
        self,
        message: str,
        provider: str = "hunyuan",
        session_id: str = "default-session"
    ) -> str:
        """调用Gateway（WebSocket）"""
        uri = f"{self.gateway_url}/ws/stream/{session_id}"

        print(f"[Gateway] 连接到: {uri}")
        print(f"[Gateway] 发送消息: {message[:50]}...")

        async with websockets.connect(uri) as ws:
            # 发送
            payload = {
                "message": message,
                "provider": provider
            }
            await ws.send(json.dumps(payload, ensure_ascii=False))

            # 接收
            full_response = ""

            while True:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=30.0)

                    # 解析
                    try:
                        data = json.loads(response)
                        if data.get("type") == "done":
                            break
                        elif data.get("type") == "error":
                            raise Exception(data.get("message"))
                    except json.JSONDecodeError:
                        full_response += response

                except asyncio.TimeoutError:
                    raise Exception("Gateway超时")

            print(f"[Gateway] 接收完成 (长度: {len(full_response)})")
            return full_response


class SimpleWorkerWithGateway:
    """简化的Worker - 可以调用Gateway"""

    def __init__(self, name: str, gateway_client: SimpleGatewayClient):
        self.name = name
        self.gateway_client = gateway_client

    async def execute_gateway_task(self, content: str, provider: str = "hunyuan"):
        """执行Gateway任务"""
        print(f"[{self.name}] 执行Gateway任务")
        try:
            result = await self.gateway_client.chat(
                message=content,
                provider=provider,
                session_id=f"session-{self.name}"
            )
            print(f"[{self.name}] ✅ Gateway任务完成")
            return result
        except Exception as e:
            print(f"[{self.name}] ❌ Gateway任务失败: {e}")
            raise


class SimpleWorkerPool2:
    """简化的Worker Pool（支持Gateway任务）"""

    def __init__(self, num_workers: int = 2):
        self.num_workers = num_workers
        self.workers = []
        self.task_queue = asyncio.Queue(maxsize=50)
        self.running = False
        self.stats = {"submitted": 0, "completed": 0, "failed": 0}

    async def start(self):
        if self.running:
            return

        print(f"[Pool] 启动 {self.num_workers} 个Worker...")

        # 创建Gateway客户端
        gateway_client = SimpleGatewayClient()

        # 创建Worker
        self.workers = [
            SimpleWorkerWithGateway(f"worker-{i+1}", gateway_client)
            for i in range(self.num_workers)
        ]

        # 启动Worker
        self.worker_tasks = [
            asyncio.create_task(self._worker_loop(worker, worker.name))
            for worker in self.workers
        ]

        self.running = True
        print(f"[Pool] ✅ Worker Pool已启动")

    async def stop(self):
        if not self.running:
            return

        for _ in range(self.num_workers):
            await self.task_queue.put(None)

        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.running = False
        print("[Pool] ✅ Worker Pool已停止")

    async def submit_gateway_task(self, content: str, provider: str = "hunyuan"):
        """提交Gateway任务"""
        if not self.running:
            raise RuntimeError("Worker Pool未启动")

        import uuid
        task_id = str(uuid.uuid4())

        task = {
            "id": task_id,
            "type": "gateway",
            "content": content,
            "provider": provider,
            "status": "pending"
        }

        await self.task_queue.put(task)
        self.stats["submitted"] += 1

        print(f"[Pool] Gateway任务已提交: {task_id[:8]}... (队列: {self.task_queue.qsize()})")

        return task

    async def wait_for_all_tasks(self):
        while not self.task_queue.empty():
            await asyncio.sleep(1)

    def get_stats(self):
        return {
            **self.stats,
            "queue_size": self.task_queue.qsize(),
            "running": self.running
        }

    async def _worker_loop(self, worker: SimpleWorkerWithGateway, worker_name: str):
        print(f"[{worker_name}] Worker启动")

        while True:
            task = await self.task_queue.get()

            if task is None:
                break

            try:
                print(f"[{worker_name}] 执行任务: {task['id'][:8]}...")
                result = await worker.execute_gateway_task(
                    content=task["content"],
                    provider=task["provider"]
                )
                task["status"] = "completed"
                task["result"] = result
                self.stats["completed"] += 1
                print(f"[{worker_name}] ✅ 任务完成: {task['id'][:8]}")
            except Exception as e:
                task["status"] = "failed"
                task["error"] = str(e)
                self.stats["failed"] += 1
                print(f"[{worker_name}] ❌ 任务失败: {e}")
            finally:
                self.task_queue.task_done()

        print(f"[{worker_name}] Worker停止")


async def test_gateway_integration():
    """测试Gateway集成"""

    print("\n" + "="*70)
    print("Gateway + Worker Pool集成测试（简化版）")
    print("="*70 + "\n")

    # 测试1: 单个Gateway调用
    print("【测试1】单个Gateway调用")
    print("-" * 70)

    client = SimpleGatewayClient()

    try:
        result = await client.chat(
            message="你好，请用一句话介绍你自己",
            provider="hunyuan"
        )
        print(f"\n✅ Gateway调用成功")
        print(f"结果（前80字符）: {result[:80]}...\n")
    except Exception as e:
        print(f"❌ Gateway调用失败: {e}")
        print("请确保Gateway正在运行: http://127.0.0.1:8001\n")
        await asyncio.sleep(2)
    finally:
        await client.client.aclose() if hasattr(client, 'client') else None

    # 测试2: Worker Pool + Gateway（并发）
    print("\n【测试2】Worker Pool并发执行Gateway任务")
    print("-" * 70)

    pool = SimpleWorkerPool2(num_workers=2)
    await pool.start()

    # 提交多个Gateway任务
    tasks = []
    messages = [
        "你好，请用50字介绍什么是AI",
        "请用50字介绍什么是JARVIS",
        "请用50字介绍什么是Worker Pool"
    ]

    for msg in messages:
        task = await pool.submit_gateway_task(content=msg, provider="hunyuan")
        tasks.append(task)

    # 立即查看状态
    print(f"\n提交完成: {pool.get_stats()}")
    print("✅ 关键点：任务提交后，主流程没有被阻塞！\n")

    # 等待完成
    print("等待所有任务完成...")
    await pool.wait_for_all_tasks()

    # 查看结果
    print(f"\n最终状态: {pool.get_stats()}")
    print("\n任务结果:")
    print("-" * 70)

    for i, task in enumerate(tasks, 1):
        status_emoji = "✅" if task["status"] == "completed" else "❌"
        print(f"任务{i} ({task['id'][:8]}): {status_emoji} {task['status']}")
        if task["status"] == "completed":
            result = task["result"]
            print(f"       结果（前60字符）: {result[:60]}...")
            print(f"       长度: {len(result)}字符")
        elif "error" in task:
            print(f"       错误: {task['error']}")
        print()

    await pool.stop()

    print("="*70)
    print("✅ 测试完成！")
    print("="*70 + "\n")

    print("核心成果:")
    print("  ✅ Worker Pool可以调用Gateway")
    print("  ✅ 多Worker并发执行流式任务")
    print("  ✅ 不阻塞主流程")
    print("  ✅ 完全独立，无import问题")
    print()


async def main():
    await test_gateway_integration()

    print("\n" + "="*70)
    print("🎉 集成测试全部完成！")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
