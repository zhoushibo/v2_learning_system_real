"""
流式响应系统测试
测试LLM流式调用和WebSocket服务器（性能监控版）
"""
import asyncio
import sys
import os
import json

# 修复Windows编码问题
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 确保内置queue模块在sys.modules中（避免与项目queue包冲突）
import queue as builtin_queue

# 将src添加到PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from streaming.llm_stream import StreamChatService, OpenAIStreamer


# 加载API配置
def load_api_config():
    """加载API配置"""
    # API_CONFIG_FINAL.json 在 openclaw_async_architecture/ 目录
    workspace_root = os.path.dirname(project_root)
    config_path = os.path.join(
        workspace_root,
        "API_CONFIG_FINAL.json"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["api_configs"]


async def test_openai_streamer():
    """测试OpenAI格式流式调用（NVIDIA）"""
    print("\n" + "=" * 70)
    print("测试1: OpenAI格式流式调用（NVIDIA）")
    print("=" * 70)

    api_configs = load_api_config()
    nvidia_config = api_configs["nvidia2"]  # 使用nvidia2（更快）

    print(f"使用模型: {nvidia_config['name']}")

    streamer = OpenAIStreamer(
        api_url=nvidia_config["url"],
        api_key=nvidia_config["api_key"],
        model=nvidia_config["model"]
    )

    try:
        messages = [{"role": "user", "content": "用一句话介绍什么是人工智能"}]

        print("\n流式输出:")
        print("-" * 70)
        full_response = ""

        # 测试首次调用（冷启动）
        async for chunk in streamer.stream_chat(messages):
            full_response += chunk
            print(chunk, end="", flush=True)

        print("\n" + "-" * 70)
        print(f"\n[OK] 测试通过！总字符数: {len(full_response)}")

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await streamer.close()


async def test_stream_chat_service():
    """测试StreamChatService统一接口（性能监控）"""
    print("\n" + "=" * 70)
    print("测试2: StreamChatService统一接口（含性能监控）")
    print("=" * 70)

    api_configs = load_api_config()
    service = StreamChatService(api_configs)

    try:
        # 测试NVIDIA（首次调用，冷启动）
        print("\n[TEST] NVIDIA（首次调用，冷启动）:")
        messages = [{"role": "user", "content": "1+1等于几？"}]

        full_response = ""
        async for chunk in service.stream_chat(
            "nvidia2",
            messages,
            enable_monitor=True,
            is_first_call=True
        ):
            full_response += chunk
            print(chunk, end="", flush=True)

        print(f"\n")

        # 测试NVIDIA（后续调用，热连接）
        print("\n[TEST] NVIDIA（后续调用，热连接）:")
        messages = [{"role": "user", "content": "2+2等于几？"}]

        full_response = ""
        async for chunk in service.stream_chat(
            "nvidia2",
            messages,
            enable_monitor=True,
            is_first_call=False
        ):
            full_response += chunk
            print(chunk, end="", flush=True)

        print(f"\n")

        # 测试混元（国内API）
        print("\n[TEST] 混元（国内API）:")
        messages = [{"role": "user", "content": "Hello"}]

        full_response = ""
        async for chunk in service.stream_chat(
            "hunyuan",
            messages,
            enable_monitor=True,
            is_first_call=True
        ):
            full_response += chunk
            print(chunk, end="", flush=True)

        print(f"\n")

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await service.close()


async def test_multiple_calls():
    """测试多次调用（验证热连接性能）"""
    print("\n" + "=" * 70)
    print("测试3: 多次调用性能对比（热连接优化）")
    print("=" * 70)

    api_configs = load_api_config()
    service = StreamChatService(api_configs)

    try:
        messages = [{"role": "user", "content": "你好"}]

        print("\n连续调用3次，观察性能变化:")
        print("-" * 70)

        for i in range(3):
            print(f"\n[CALL {i+1}]: ", end="")
            full_response = ""
            is_first = (i == 0)

            async for chunk in service.stream_chat(
                "nvidia2",
                messages,
                enable_monitor=True,
                is_first_call=is_first
            ):
                full_response += chunk
                print(chunk, end="", flush=True)

            print()

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await service.close()


async def main():
    """运行所有测试"""
    print("\n[TEST] 流式响应系统测试（含性能监控）")
    print("=" * 70)

    # 测试1: OpenAI格式流式调用
    await test_openai_streamer()

    # 测试2: StreamChatService统一接口（性能监控）
    await test_stream_chat_service()

    # 测试3: 多次调用性能对比
    await test_multiple_calls()

    print("\n" + "=" * 70)
    print("[DONE] 所有测试完成！")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
