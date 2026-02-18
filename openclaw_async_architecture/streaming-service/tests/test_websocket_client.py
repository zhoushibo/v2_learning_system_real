"""
WebSocket流式测试客户端
测试流式Gateway的WebSocket端点
"""
import asyncio
import websockets
import json
import sys
import os

# 修复Windows编码问题
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 确保内置queue模块
import queue as builtin_queue

# 添加上级mvp/src到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, "mvp", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from streaming.llm_stream import StreamChatService

# 配置
GATEWAY_URL = "ws://127.0.0.1:8001"
SESSION_ID = "test-session-001"


async def test_websocket_basic():
    """测试基础WebSocket连接和流式输出"""
    print("\n" + "=" * 70)
    print("测试1: 基础WebSocket连接 + 流式输出")
    print("=" * 70)

    uri = f"{GATEWAY_URL}/ws/stream/{SESSION_ID}"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"\n[OK] 连接成功: {uri}\n")

            # 发送消息
            message = {
                "message": "用一句话介绍什么是人工智能",
                "provider": "nvidia2"
            }

            print(f"发送消息: {message['message']}")
            print("\n流式输出:")
            print("-" * 70)

            await websocket.send(json.dumps(message, ensure_ascii=False))

            # 接收流式响应
            full_response = ""
            while True:
                try:
                    # 设置超时，避免无限等待
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)

                    try:
                        # 尝试解析为JSON
                        data = json.loads(response)

                        if data.get("type") == "done":
                            print("\n[INFO] 收到完成信号")
                            break
                        elif data.get("type") == "error":
                            print(f"\n[ERROR] {data.get('message')}")
                            break
                    except json.JSONDecodeError:
                        # 普通文本，直接输出
                        full_response += response
                        print(response, end="", flush=True)

                except asyncio.TimeoutError:
                    print("\n[TIMEOUT] 响应超时")
                    break
                except Exception as e:
                    print(f"\n[ERROR] 接收错误: {e}")
                    break

            print("\n" + "-" * 70)
            print(f"\n[OK] 测试完成！总字符数: {len(full_response)}")

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_websocket_hunyuan():
    """测试混元API（国内API，预期<1秒）"""
    print("\n" + "=" * 70)
    print("测试2: 混元API（国内API，预期性能更好）")
    print("=" * 70)

    uri = f"{GATEWAY_URL}/ws/stream/{SESSION_ID}-hunyuan"

    try:
        import time
        start_time = time.time()

        async with websockets.connect(uri) as websocket:
            print(f"\n[OK] 连接成功: {uri}\n")

            # 发送消息
            message = {
                "message": "Hello",
                "provider": "hunyuan"  # 使用混元
            }

            print(f"发送消息: {message['message']}")
            print("\n流式输出:")
            print("-" * 70)

            await websocket.send(json.dumps(message, ensure_ascii=False))

            # 接收流式响应
            full_response = ""
            first_chunk_time = None

            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)

                    try:
                        data = json.loads(response)

                        if data.get("type") == "done":
                            print("\n[INFO] 收到完成信号")
                            break
                        elif data.get("type") == "error":
                            print(f"\n[ERROR] {data.get('message')}")
                            break
                    except json.JSONDecodeError:
                        if first_chunk_time is None:
                            first_chunk_time = time.time()
                            elapsed = (first_chunk_time - start_time) * 1000
                            print(f"\n[PERF] 首字输出: {elapsed:.0f}ms")

                        full_response += response
                        print(response, end="", flush=True)

                except asyncio.TimeoutError:
                    print("\n[TIMEOUT] 响应超时")
                    break
                except Exception as e:
                    print(f"\n[ERROR] 接收错误: {e}")
                    break

            total_time = (time.time() - start_time) * 1000

            print("\n" + "-" * 70)
            print(f"\n[STATS] 统计:")
            print(f"   总字符数: {len(full_response)}")
            if first_chunk_time:
                print(f"   首字输出: {(first_chunk_time - start_time)*1000:.0f}ms")
            print(f"   完整响应: {total_time:.0f}ms")

            if first_chunk_time and (first_chunk_time - start_time) < 1.0:
                print(f"\n[OK] 优秀！首字输出 <1秒")
            else:
                print(f"\n[OK] 测试完成")

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_websocket_multiple():
    """测试多次调用（验证热连接）"""
    print("\n" + "=" * 70)
    print("测试3: 多次调用（热连接性能）")
    print("=" * 70)

    try:
        for i in range(3):
            session_id = f"{SESSION_ID}-multi-{i}"
            uri_i = f"{GATEWAY_URL}/ws/stream/{session_id}"

            print(f"\n[CALL {i+1}]")

            async with websockets.connect(uri_i) as websocket:
                # 发送消息
                message = {
                    "message": "你好",
                    "provider": "nvidia2"
                }

                await websocket.send(json.dumps(message, ensure_ascii=False))

                # 接收流式响应
                full_response = ""
                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=30.0)

                        try:
                            data = json.loads(response)

                            if data.get("type") == "done":
                                break
                        except json.JSONDecodeError:
                            full_response += response
                            print(response, end="", flush=True)

                    except asyncio.TimeoutError:
                        print("\n[TIMEOUT] 响应超时")
                        break
                    except Exception as e:
                        print(f"\n[ERROR] {e}")
                        break

                print()

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_gateway_stats():
    """测试Gateway健康检查和统计"""
    print("\n" + "=" * 70)
    print("测试4: Gateway健康检查")
    print("=" * 70)

    # 使用httpx代替requests（避免queue冲突）
    import httpx

    http_url = "http://127.0.0.1:8001"

    # 测试根路径
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{http_url}/")
            print(f"\n[GET /]")
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"\n[FAIL] 根路径测试失败: {e}")

    # 测试健康检查
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{http_url}/health")
            print(f"\n[GET /health]")
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"\n[FAIL] 健康检查失败: {e}")

    # 测试统计
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{http_url}/stats")
            print(f"\n[GET /stats]")
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"\n[FAIL] 统计测试失败: {e}")


async def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("OpenClaw流式响应Gateway - WebSocket测试")
    print("=" * 70)
    print(f"\nGateway URL: {GATEWAY_URL}")
    print(f"确保Gateway已启动: python launcher.py")
    print()

    # 测试4：Gateway健康检查
    await test_gateway_stats()

    # 测试1：基础WebSocket连接
    await test_websocket_basic()

    # 测试2：混元API
    await test_websocket_hunyuan()

    # 测试3：多次调用
    await test_websocket_multiple()

    print("\n" + "=" * 70)
    print("[DONE] 所有测试完成！")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
