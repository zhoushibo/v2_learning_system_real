"""
测试Gateway自动启动功能

1. 停止现有的Gateway服务（如果有）
2. 启动V2 CLI，观察是否自动启动Gateway
3. 验证Gateway是否可访问
"""
import asyncio
import time
import requests


async def test_gateway_auto_start():
    """测试Gateway自动启动"""
    print("=" * 60)
    print("测试Gateway自动启动功能")
    print("=" * 60)
    print()

    # 1. 检查Gateway是否在运行
    print("步骤1：检查Gateway服务状态")
    print("-" * 60)

    try:
        response = requests.get("http://127.0.0.1:8001/health", timeout=2)
        if response.status_code == 200:
            print("✅ Gateway服务已在运行")
            print("   请先手动停止Gateway服务，然后重新运行此测试")
            return
    except:
        print("✅ Gateway服务未运行（这是预期状态）")

    print()

    # 2. 导入并调用ensure_gateway
    print("步骤2：测试ensure_gateway函数")
    print("-" * 60)

    from gateway_manager import ensure_gateway

    result = await ensure_gateway()

    if result:
        print("✅ Gateway启动成功")
    else:
        print("❌ Gateway启动失败")
        return

    print()

    # 3. 验证Gateway是否可访问
    print("步骤3：验证Gateway健康检查")
    print("-" * 60)

    time.sleep(1)  # 等待一秒

    try:
        response = requests.get("http://127.0.0.1:8001/health", timeout=2)
        if response.status_code == 200:
            print("✅ Gateway健康检查通过")
            print(f"   响应：{response.json()}")
        else:
            print(f"❌ Gateway健康检查失败：{response.status_code}")
    except Exception as e:
        print(f"❌ Gateway访问失败：{e}")

    print()

    # 4. 测试流式对话
    print("步骤4：测试Gateway流式对话")
    print("-" * 60)

    try:
        # 切换到streaming-service目录
        import os
        import sys
        from pathlib import Path

        gateway_dir = Path.cwd().parent / "openclaw_async_architecture" / "streaming-service"
        os.chdir(str(gateway_dir))

        from use_gateway import StreamingChat

        client = StreamingChat(gateway_url="ws://127.0.0.1:8001")
        print("你：测试Gateway")

        response = await client.chat(message="测试Gateway自动启动功能，回复'自动启动成功'", provider="nvidia2")

        if "自动启动成功" in response or "成功" in response:
            print("✅ Gateway流式对话成功")
        else:
            print("⚠️ Gateway流式对话可能有问题")

    except Exception as e:
        print(f"❌ Gateway流式对话失败：{e}")

    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_gateway_auto_start())
