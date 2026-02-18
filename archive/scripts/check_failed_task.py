"""检查失败任务的详细信息"""

import requests

V2_GATEWAY = "http://127.0.0.1:8000"

# 检查失败的任务
task_id = "2de111a9-c529-4695-aba6-3085d3a60a64"

print(f"检查任务 {task_id}:")
print("="*60)

response = requests.get(f"{V2_GATEWAY}/tasks/{task_id}")
task = response.json()

print(f"状态: {task['status']}")
print(f"内容: {task['content']}")
print(f"错误: {task.get('error', 'None')}")
print(f"结果: {task.get('result', 'None')}")
print(f"\n元数据:")
for key, value in task.get('metadata', {}).items():
    print(f"  {key}: {value}")
