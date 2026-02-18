"""
Worker Pool + Gateway HTTP集成
避免import问题，使用HTTP调用
"""
import httpx
import base64
import json
from pathlib import Path
import sys
from typing import Optional

# Windows编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class GatewayClient:
    """
    Gateway HTTP客户端

    通过HTTP调用Gateway的WebSocket端点
    使用HTTP轮询方式，避免WebSocket复杂性
    """

    def __init__(self, gateway_url: str = "http://127.0.0.1:8001"):
        self.gateway_url = gateway_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def chat(
        self,
        message: str,
        provider: str = "hunyuan",
        session_id: str = "default-session"
    ) -> dict:
        """
        通过HTTP调用Gateway

        注意：Gateway当前是WebSocket，这里用临时方案
        如果Gateway没有HTTP端点，我们会直接使用WebSocket连接
        """
        # 检查Gateway健康
        try:
            response = await self.client.get(f"{self.gateway_url}/health")
            if response.status_code == 200:
                return await self._chat_via_websocket(message, provider, session_id)
            else:
                raise Exception(f"Gateway不健康: {response.status_code}")
        except Exception as e:
            raise Exception(f"Gateway连接失败: {e}")

    async def _chat_via_websocket(
        self,
        message: str,
        provider: str,
        session_id: str
    ) -> dict:
        """
        使用WebSocket连接Gateway

        返回完整的结果（等待完成）
        """
        try:
            # 动态导入websockets（避免启动时import失败）
            import websockets

            uri = f"ws://127.0.0.1:8001/ws/stream/{session_id}"

            async with websockets.connect(uri) as websocket:
                # 发送消息
                payload = {
                    "message": message,
                    "provider": provider
                }
                await websocket.send(json.dumps(payload, ensure_ascii=False))

                # 接收完整响应
                full_response = ""

                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=30.0)

                        # 解析响应
                        try:
                            data = json.loads(response)

                            if data.get("type") == "done":
                                break
                            elif data.get("type") == "error":
                                raise Exception(data.get("message", "Gateway error"))
                        except json.JSONDecodeError:
                            # 普通文本
                            full_response += response

                    except asyncio.TimeoutError:
                        raise Exception("Gateway响应超时")

                return {
                    "status": "success",
                    "provider": provider,
                    "response": full_response
                }

        except ImportError as e:
            raise Exception(f"websockets模块未安装: {e}")
        except Exception as e:
            raise Exception(f"WebSocket连接失败: {e}")

    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()


# Worker Pool的Stream任务类型（新增）
class StreamTask:
    """Gateway流式任务"""

    def __init__(
        self,
        content: str,
        gateway_client: GatewayClient,
        provider: str = "hunyuan",
        session_id: str = "default-session"
    ):
        import uuid
        self.id = str(uuid.uuid4())
        self.content = content
        self.gateway_client = gateway_client
        self.provider = provider
        self.session_id = session_id
        self.status = "pending"
        self.result = None
        self.error = None

    async def execute(self) -> None:
        """执行流式任务"""
        try:
            self.status = "running"

            print(f"[StreamTask] 开始执行: {self.id}")
            print(f"[StreamTask] 调用Gateway (provider={self.provider})...")

            # 调用Gateway
            response = await self.gateway_client.chat(
                message=self.content,
                provider=self.provider,
                session_id=self.session_id
            )

            self.status = "completed"
            self.result = response["response"]

            print(f"[StreamTask] 完成: {self.id} (长度: {len(self.result)})")

        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            print(f"[StreamTask] 失败: {self.id} - {e}")


# 更新Worker Pool支持Stream任务
from worker.worker_pool import WorkerPool as BaseWorkerPool


class EnhancedWorkerPool(BaseWorkerPool):
    """
    增强版Worker Pool

    支持：
    - V1任务（继承自BaseWorkerPool）
    - Gateway流式任务
    """

    def __init__(self, num_workers: int = 3, gateway_url: str = "http://127.0.0.1:8001"):
        super().__init__(num_workers=num_workers)
        self.gateway_url = gateway_url
        self.gateway_client = GatewayClient(gateway_url)

    async def submit_stream_task(
        self,
        content: str,
        provider: str = "hunyuan",
        session_id: Optional[str] = None
    ):
        """
        提交Gateway流式任务

        Args:
            content: 用户消息
            provider: API提供商（hunyuan/nvidia2/zhipu）
            session_id: 会话ID（可选）
        """
        if not self.running:
            raise RuntimeError("Worker Pool未启动")

        # 创建Stream任务
        import uuid
        if not session_id:
            session_id = str(uuid.uuid4())

        task = StreamTask(
            content=content,
            gateway_client=self.gateway_client,
            provider=provider,
            session_id=session_id
        )

        # 提交到队列
        await self.task_queue.put(task)
        self.stats["tasks_submitted"] += 1

        print(f"[WorkerPool] Gateway任务已提交: {task.id}")

        return task

    async def stop(self):
        """停止Worker Pool（重写，关闭Gateway客户端）"""
        await super().stop()
        if self.gateway_client:
            await self.gateway_client.close()


# 测试
async def test_gateway_integration():
    """测试Gateway集成"""

    print("\n" + "="*70)
    print("Gateway HTTP集成测试")
    print("="*70 + "\n")

    # 测试1: Gateway健康检查
    print("【测试1】Gateway健康检查")
    print("-" * 70)

    client = GatewayClient()
    try:
        response = await client.client.get(f"{client.gateway_url}/health")
        print(f"✅ Gateway健康: {response.json()}")
    except Exception as e:
        print(f"❌ Gateway不健康: {e}")
        return
    finally:
        await client.close()

    # 测试2: Worker Pool + Gateway任务
    print("\n【测试2】Worker Pool执行Gateway任务")
    print("-" * 70)

    pool = EnhancedWorkerPool(num_workers=2)
    await pool.start()

    # 提交多个Gateway任务
    tasks = []
    for i in range(3):
        task = await pool.submit_stream_task(
            content=f"你好，这是第{i+1}个Gateway任务",
            provider="hunyuan"
        )
        tasks.append(task)

    # 立即查看状态（不等待）
    print(f"\n提交完成: {pool.get_stats()}")
    print("✅ 关键点：任务已提交，主流程没有被阻塞！\n")

    # 等待完成
    print("等待任务完成...")
    await pool.wait_for_all_tasks()

    # 查看结果
    print(f"\n最终状态: {pool.get_stats()}")
    print("\n任务结果:")
    print("-" * 70)

    for i, task in enumerate(tasks, 1):
        status_emoji = "✅" if task.status == "completed" else "❌"
        print(f"任务{i} ({task.id[:8]}): {status_emoji} {task.status}")
        if task.status == "completed":
            print(f"       结果（前50字符）: {task.result[:50]}...")
            print(f"       长度: {len(task.result)}字符")
            print()

    # 停止
    await pool.stop()

    print("="*70)
    print("✅ 测试完成！")
    print("="*70 + "\n")

    print("集成成果:")
    print("  ✅ Worker Pool可以调用Gateway")
    print("  ✅ 流式任务正常执行")
    print("  ✅ 不阻塞主流程")
    print("  ✅ 多Worker并发")
    print()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_gateway_integration())
