"""测试读取文件（重试版）"""

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
for i in range(10):
    time.sleep(1)
    response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
    task = response.json()
    print(f"  [{i+1}/10] 状态: {task['status']}")

    if task['status'] in ['completed', 'failed']:
        break

print(f"\n最终状态: {task['status']}")
print(f"元数据: {json.dumps(task.get('metadata', {}), indent=2, ensure_ascii=False)}")

if task['status'] == 'completed':
    result = json.loads(task['result'])
    print(f"\n文件内容: {result}")
elif task['status'] == 'failed':
    print(f"\n错误: {task.get('error', 'Unknown error')}")
