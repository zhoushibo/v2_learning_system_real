"""测试读取文件"""

import requests
import time
import json

print("提交任务（读取文件）...")
response = requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": 'TOOL:read_file|{"path":"gateway_test.txt"}'}
)
task_id = response.json()["task_id"]
print(f"任务ID: {task_id}")

print("等待处理...")
time.sleep(3)

response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
task = response.json()

print(f"\n状态: {task['status']}")
print(f"工具: {task['metadata']['tool_name']}")

if task['status'] == 'completed':
    result = json.loads(task['result'])
    print(f"文件内容: {result}")
