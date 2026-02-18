"""演示V2 Worker工具系统使用（修复版）"""

import requests
import json
import time

print("="*60)
print("V2 Worker工具系统使用演示")
print("="*60)

# 提交任务
print("\n【演示1】读取文件")
response = requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": 'TOOL:read_file|{"path":"novel.md"}'}
)
task_id = response.json()["task_id"]
print(f"任务ID: {task_id}")

# 等待完成
time.sleep(3)
response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
task = response.json()

print(f"状态: {task['status']}")
print(f"元数据: {json.dumps(task.get('metadata', {}), indent=2, ensure_ascii=False)}")
if task['status'] == 'completed':
    result_data = json.loads(task['result'])
    print(f"内容: {result_data[:100] if isinstance(result_data, str) else result_data}...")

# 演示2：执行Python代码
print("\n【演示2】执行Python代码")
response = requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": 'TOOL:exec_python|{"code":"for i in range(5):\\n    print(f\'i = {i}\')"}'}
)
task_id = response.json()["task_id"]
print(f"任务ID: {task_id}")

time.sleep(3)
response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
task = response.json()

print(f"状态: {task['status']}")
print(f"元数据: {json.dumps(task.get('metadata', {}), indent=2, ensure_ascii=False)}")
if task['status'] == 'completed':
    output = json.loads(task['result'])
    print(f"输出:\n{output.get('stdout', 'N/A')}")

# 演示3：列出目录
print("\n【演示3】列出目录")
response = requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": 'TOOL:list_directory|{"path":"."}'}
)
task_id = response.json()["task_id"]
print(f"任务ID: {task_id}")

time.sleep(3)
response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
task = response.json()

print(f"状态: {task['status']}")
print(f"元数据: {json.dumps(task.get('metadata', {}), indent=2, ensure_ascii=False)}")
if task['status'] == 'completed':
    files = json.loads(task['result'])
    print(f"找到 {len(files)} 个文件/目录:")
    for f in files[:10]:
        print(f"  - {f['name']} ({f['type']})")

print("\n" + "="*60)
print("演示完成！")
print("="*60)
