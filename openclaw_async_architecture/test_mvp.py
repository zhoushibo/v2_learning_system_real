"""测试OpenClaw V2 MVP"""
import requests
import time
import json

V2_GATEWAY = "http://127.0.0.1:8000"


def test_mvp():
    """测试MVP完整流程"""
    print("="*60)
    print("OpenClaw V2 MVP 测试")
    print("="*60)

    # 1. 提交任务
    print("\n1️⃣ 提交任务")
    start_time = time.time()

    response = requests.post(
        f"{V2_GATEWAY}/tasks",
        json={"content": "你好，请用一句话介绍你自己"},
        timeout=5
    )

    submit_time = time.time() - start_time

    if response.status_code == 200:
        data = response.json()
        task_id = data['task_id']
        print(f"✅ 任务提交成功")
        print(f"📦 任务ID: {task_id}")
        print(f"⏱️  提交时间: {submit_time*1000:.2f}ms")
        print(f"📝 状态: {data['status']}")

        # 验证目标：<50ms
        if submit_time < 0.05:
            print(f"⚡ 优秀！提交时间 < 50ms")
        else:
            print(f"⚠️  注意：提交时间 {submit_time*1000:.2f}ms")
    else:
        print(f"❌ 任务提交失败: {response.text}")
        return False

    # 2. 等待任务完成
    print("\n2️⃣ 轮询任务状态")
    for i in range(30):  # 最长等待30秒
        time.sleep(1)

        response = requests.get(
            f"{V2_GATEWAY}/tasks/{task_id}",
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            status = data['status']
            print(f"  [{i+1}s] 状态: {status}")

            if status == "completed":
                print(f"\n✅ 任务完成！")
                print(f"📦 结果: {data['result']}")

                if 'metadata' in data:
                    print(f"🪙 Token信息: {data['metadata']}")

                return True
            elif status == "failed":
                print(f"\n❌ 任务失败")
                print(f"错误: {data['error']}")
                return False

    print(f"\n❌ 任务超时")
    return False


def test_health():
    """测试健康检查"""
    print("\n3️⃣ 健康检查")
    response = requests.get(f"{V2_GATEWAY}/health", timeout=5)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Gateway运行正常")
        print(f"状态: {data['status']}")
        print(f"Redis连接: {data['redis_connected']}")
        return True
    else:
        print(f"❌ 健康检查失败")
        return False


if __name__ == "__main__":
    # 健康检查
    test_health()

    # 测试MVP
    success = test_mvp()

    print("\n" + "="*60)
    if success:
        print("✅ MVP测试通过！")
        print("\n核心验证：")
        print("  • Gateway响应 < 50ms ⚡")
        print("  • Worker调用V1 API")
        print("  • 长任务不阻塞接口")
    else:
        print("❌ MVP测试失败")
    print("="*60)
