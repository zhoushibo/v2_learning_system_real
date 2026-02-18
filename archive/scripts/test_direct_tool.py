"""直接测试V2工具执行（绕开LLM）"""

import requests
import time
import json

V2_GATEWAY = "http://127.0.0.1:8000"


def test_direct_tool():
    """直接提交工具调用任务（纯工具格式）"""

    print("="*60)
    print("直接测试V2工具执行")
    print("="*60)

    # 纯工具格式（没有任何多余文字）
    task_content = 'TOOL:exec_command|{"command":"echo Hello V2 Worker!"}'

    print(f"\n提交任务:")
    print(f"内容: {task_content}")

    # 提交任务
    response = requests.post(
        f"{V2_GATEWAY}/tasks",
        json={"content": task_content}
    )

    task_id = response.json()["task_id"]
    print(f"✅ 任务ID: {task_id}")
    print(f"✅ 状态: {response.json()['status']}")

    # 等待结果
    print("\n等待处理...")
    for i in range(20):
        time.sleep(1)

        response = requests.get(f"{V2_GATEWAY}/tasks/{task_id}")
        task = response.json()

        status = task["status"]
        print(f"  [{i+1}/20] 状态: {status}")

        if status == "completed":
            print("\n✅ 任务完成!")
            print(f"结果: {task.get('result', 'N/A')}")
            print(f"元数据: {json.dumps(task.get('metadata', {}), indent=2, ensure_ascii=False)}")
            return task
        elif status == "failed":
            print(f"\n❌ 任务失败: {task.get('error', 'Unknown error')}")
            return task

    print("\n⏱️  超时")
    return None


if __name__ == "__main__":
    test_direct_tool()
