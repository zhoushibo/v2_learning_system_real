# -*- coding: utf-8 -*-
"""测试完整的Gateway+Worker工作流"""
import sys
import os
import requests
import time
import json

# Windows编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    os.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

GATEWAY_URL = "http://127.0.0.1:8000"

print("="*70)
print("完整工作流测试")
print("="*70)

# 测试1：检查Gateway健康
print("\n[测试1] 检查Gateway健康状态")
try:
    health = requests.get(f"{GATEWAY_URL}/health", timeout=5)
    print(f"  状态码: {health.status_code}")
    print(f"  响应: {health.json()}")
except Exception as e:
    print(f"  [X] Gateway未运行: {e}")
    sys.exit(1)

# 测试2：提交任务
print("\n[测试2] 提交测试任务")
task_data = {
    "content": 'TOOL:exec_command|{"command":"echo BugFixed!"}'
}

try:
    response = requests.post(f"{GATEWAY_URL}/tasks", json=task_data)
    print(f"  状态码: {response.status_code}")
    response_data = response.json()
    print(f"  响应: {response_data}")
    task_id = response_data["task_id"]
    print(f"  任务ID: {task_id}")
except Exception as e:
    print(f"  [X] 提交失败: {e}")
    sys.exit(1)

# 测试3：等待并获取结果
print("\n[测试3] 等待任务完成（最多20秒）")
for i in range(20):
    time.sleep(1)

    try:
        result = requests.get(f"{GATEWAY_URL}/tasks/{task_id}").json()

        status = result.get("status")
        print(f"  第{i+1}秒: 状态={status}")

        if status in ["completed", "failed"]:
            print(f"\n[结果]")
            print(f"  状态: {status}")
            print(f"  内容: {result.get('content')}")
            print(f"  结果: {result.get('result')}")
            print(f"  错误: {result.get('error')}")
            print(f"  元数据: {result.get('metadata')}")

            # 验证修复
            if status == "completed":
                metadata = result.get('metadata', {})
                if metadata.get('type') == 'tool':
                    print(f"\n[验证1] 工具调用识别: [OK]")

                    output = json.loads(result.get('result', '{}'))
                    stdout = output.get('stdout', '').strip()
                    if stdout == 'BugFixed!':
                        print(f"[验证2] 命令执行成功: [OK]")
                        print(f"  输出: {stdout}")
                    else:
                        print(f"[验证2] 命令执行结果: [{stdout}]")
                else:
                    print(f"[验证1] 任务类型: {metadata.get('type')}")

            break
    except Exception as e:
        print(f"  [X] 获取结果失败: {e}")
        break
else:
    print(f"\n[超时] 任务未在20秒内完成")

print("\n[完成]")
print("="*70)
