# -*- coding: utf-8 -*-
"""简化的Bug修复测试"""
import requests
import time
import json
import sys

# Windows编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GATEWAY_URL = "http://127.0.0.1:8000"


def test_simple_task():
    """简单测试：提交任务并获取结果"""
    print("\n" + "="*70)
    print("简单测试：提交任务")
    print("="*70)

    # 提交任务
    task_data = {
        "content": 'TOOL:exec_command|{"command":"echo test"}'
    }

    print(f"\n提交任务...")
    response = requests.post(f"{GATEWAY_URL}/tasks", json=task_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    task_id = response.json()["task_id"]
    print(f"\n任务ID: {task_id}")

    # 等待执行
    print(f"\n等待执行（最多30秒）...")
    for i in range(30):
        time.sleep(1)
        result = requests.get(f"{GATEWAY_URL}/tasks/{task_id}").json()
        print(f"  第{i+1}秒: 状态={result.get('status')}")

        if result.get("status") in ["completed", "failed"]:
            print(f"\n结果:")
            print(f"  状态: {result.get('status')}")
            print(f"  内容: {result.get('content')}")
            print(f"  结果: {result.get('result')}")
            print(f"  错误: {result.get('error')}")
            print(f"  元数据: {result.get('metadata')}")

            if result.get('status') == 'completed':
                # 检查工作目录
                if result.get('metadata', {}).get('type') == 'tool' and result.get('metadata', {}).get('tool_name') == 'exec_command':
                    print(f"\n[测试1] 工具调用识别: 正确")
                    output_data = json.loads(result.get('result', '{}'))
                    stdout = output_data.get('stdout', '').strip()
                    print(f"stdout: {stdout}")
                    if stdout == 'test':
                        print(f"[测试2] 命令执行: 正确")
                return True
            else:
                return False

    print(f"\n超时！任务未完成")
    return False


if __name__ == "__main__":
    try:
        success = test_simple_task()
        if success:
            print(f"\n[成功] 测试通过")
        else:
            print(f"\n[失败] 测试未通过")
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
