"""测试Gateway + Worker完整流程"""

import requests
import time
import json

print("提交任务到Gateway...")
response = requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": 'TOOL:write_file|{"path":"gateway_test.txt","content":"通过Gateway提交的任务！"}'}
)
task_id = response.json()["task_id"]
print(f"任务ID: {task_id}")

print("等待Worker处理...")
time.sleep(3)

print("查询任务状态...")
response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
task = response.json()

print(f"状态: {task['status']}")
print(f"元数据: {json.dumps(task.get('metadata', {}), indent=2, ensure_ascii=False)}")

if task['status'] == 'completed':
    print(f"结果: {task['result']}")
