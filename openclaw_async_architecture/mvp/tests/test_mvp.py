"""MVP测试脚本"""
import time
import requests
import json


def test_gateway():
    """测试Gateway"""
    print("\n=== 测试1: Gateway健康检查 ===")
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        data = response.json()
        print(f"✅ Gateway状态: {data['status']}")
        print(f"✅ Redis连接: {data['redis_connected']}")
        return True
    except Exception as e:
        print(f"❌ Gateway未运行或无法连接: {e}")
        return False


def test_submit_task():
    """测试提交任务"""
    print("\n=== 测试2: 提交任务 ===")
    try:
        # 记录开始时间
        start_time = time.time()

        # 提交任务
        response = requests.post(
            "http://127.0.0.1:8000/tasks",
            json={"content": "什么是人工智能？简短回答。"}
        )

        # 计算响应时间
        response_time = (time.time() - start_time) * 1000
        data = response.json()

        print(f"✅ 任务已提交")
        print(f"✅ Task ID: {data['task_id']}")
        print(f"⚡ 响应时间: {response_time:.2f}ms")

        if response_time < 50:
            print(f"✅ 响应时间 < 50ms（符合预期）")
        else:
            print(f"⚠️ 响应时间 > 50ms（需要优化）")

        return data["task_id"]
    except Exception as e:
        print(f"❌ 提交任务失败: {e}")
        return None


def test_get_task(task_id):
    """测试查询任务"""
    print(f"\n=== 测试3: 查询任务 {task_id} ===")

    if not task_id:
        print("❌ 没有有效的task_id")
        return False

    max_wait = 30  # 最多等待30秒
    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
            data = response.json()

            print(f"状态: {data['status']}", end="\r")

            if data["status"] == "completed":
                print(f"\n✅ 任务完成")
                print(f"✅ 结果: {data['result'][:100]}...")
                return True
            elif data["status"] == "failed":
                print(f"\n❌ 任务失败: {data.get('error', 'Unknown')}")
                return False

            time.sleep(1)

        except Exception as e:
            print(f"\n❌ 查询任务失败: {e}")
            return False

    print(f"\n⏰ 超时：任务在30秒内未完成")
    return False


def test_blocking():
    """测试长任务不阻塞界面"""
    print("\n=== 测试4: 长任务不阻塞界面 ===")

    try:
        # 提交长任务
        long_task_response = requests.post(
            "http://127.0.0.1:8000/tasks",
            json={"content": "帮我写一个完整的Python异步HTTP服务器实现，代码要详细，包含注释"}
        )
        task_id = long_task_response.json()["task_id"]
        print(f"✅ 长任务已提交: {task_id}")

        # 立即提交另一个任务
        start_time = time.time()
        short_task_response = requests.post(
            "http://127.0.0.1:8000/tasks",
            json={"content": "1+1等于几？"}
        )
        response_time = (time.time() - start_time) * 1000

        print(f"✅ 短任务立即提交")
        print(f"⚡ 短任务响应时间: {response_time:.2f}ms")

        if response_time < 100:
            print("✅ 短任务未阻塞界面")
        else:
            print("⚠️ 短任务响应时间较长，可能存在阻塞")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*50)
    print("OpenClaw V2 MVP 测试")
    print("="*50)

    # 检查Gateway
    if not test_gateway():
        print("\n❌ 请先启动Gateway: python launcher.py gateway")
        print("❌ 请先启动Worker: python launcher.py worker")
        return

    # 提交任务
    task_id = test_submit_task()

    # 查询任务结果
    test_get_task(task_id)

    # 测试不阻塞
    test_blocking()

    print("\n" + "="*50)
    print("测试完成！")
    print("="*50)


if __name__ == "__main__":
    main()
