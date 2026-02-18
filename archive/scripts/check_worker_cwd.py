"""检查Worker的工作目录"""

import requests
import json

V2_GATEWAY = "http://127.0.0.1:8000"

# 提交一个简单的任务来检查工作目录
task_content = 'TOOL:exec_command|{"command":"echo %CD%"}'

print("提交检查工作目录任务...")
response = requests.post(f"{V2_GATEWAY}/tasks", json={"content": task_content})
task_id = response.json()["task_id"]

print(f"任务ID: {task_id}")

# 等待完成
import time
for i in range(5):
    time.sleep(1)
    response = requests.get(f"{V2_GATEWAY}/tasks/{task_id}")
    task = response.json()

    if task['status'] == 'completed':
        print(f"\nWorker工作目录:")
        print(f"  {task['result']}")
        break
