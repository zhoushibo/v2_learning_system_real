"""简单测试"""
import requests, time, json, sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GATEWAY = "http://127.0.0.1:8000"

# 提交任务
response = requests.post(f"{GATEWAY}/tasks", json={"content": "TOOL:exec_command|{\"command\":\"echo BugFixed!\"}"})
task_id = response.json()["task_id"]
print(f"Task ID: {task_id}")

# 等待完成
for i in range(15):
    time.sleep(i+1)
    result = requests.get(f"{GATEWAY}/tasks/{task_id}").json()
    status = result.get("status")
    print(f"{i+1}s: {status}")
    
    if status in ["completed", "failed"]:
        print(f"Result: {result.get('result')}")
        print(f"Metadata: {result.get('metadata')}")
        break
