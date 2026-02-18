"""测试V2执行备份命令"""

import requests
import time

V2_GATEWAY = "http://127.0.0.1:8000"


def test_backup_via_v2():
    """测试V2执行备份"""

    print("="*60)
    print("测试V2执行备份命令")
    print("="*60)

    # 提交简单的备份任务
    task_content = """
    执行V2项目备份：
    TOOL:exec_command|{"command":"python backup_by_project.py"}
    """

    print("\n提交任务到V2...")
    response = requests.post(
        f"{V2_GATEWAY}/tasks",
        json={"content": task_content.strip()}
    )

    task_id = response.json()["task_id"]
    print(f"✅ 任务ID: {task_id}")
    print(f"✅ 状态: {response.json()['status']}")

    # 等待结果
    print("\n等待备份完成（最多2分钟）...")
    for i in range(60):
        time.sleep(2)

        response = requests.get(f"{V2_GATEWAY}/tasks/{task_id}")
        task = response.json()

        status = task["status"]
        print(f"  [{i+1}/60] 状态: {status}")

        if status == "completed":
            print("\n✅ 备份完成!")
            print(f"结果: {task.get('result', 'N/A')}")
            print(f"元数据: {task.get('metadata', {})}")
            break

        elif status == "failed":
            print(f"\n❌ 备份失败: {task.get('error', 'Unknown error')}")
            break

    print("\n" + "="*60)


if __name__ == "__main__":
    test_backup_via_v2()
