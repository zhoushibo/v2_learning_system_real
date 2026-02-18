# -*- coding: utf-8 -*-
"""测试Bug修复"""
import requests
import time
import json


GATEWAY_URL = "http://127.0.0.1:8000"


def test_bug1_working_directory():
    """
    测试Bug 1：Worker工作目录问题

    期望：Worker应该在workspace根目录执行命令
    """
    print("\n" + "="*70)
    print("测试Bug 1：Worker工作目录问题")
    print("="*70)

    # 测试1：验证工作目录
    print("\n测试1：验证Worker工作目录")
    task_data = {
        "content": 'TOOL:exec_command|{"command":"echo %CD%"}'
    }

    response = requests.post(f"{GATEWAY_URL}/tasks", json=task_data)
    task_id = response.json()["task_id"]
    print(f"任务ID: {task_id}")

    # 等待执行
    time.sleep(5)

    # 获取结果
    result = requests.get(f"{GATEWAY_URL}/tasks/{task_id}").json()

    if result["status"] == "completed":
        output = json.loads(result["result"])
        print(f"✅ 执行成功")
        print(f"stdout: {output['stdout'].strip()}")

        # 验证工作目录
        workspace_path = r"C:\Users\10952\.openclaw\workspace"
        if workspace_path in output["stdout"]:
            print(f"✅ Bug 1已修复！工作目录正确")
            return True
        else:
            print(f"❌ Bug 1未修复！工作目录错误")
            print(f"期望: {workspace_path}")
            print(f"实际: {output['stdout'].strip()}")
            return False
    else:
        print(f"❌ 执行失败: {result.get('error', 'Unknown')}")
        return False


def test_bug2_tool_detection():
    """
    测试Bug 2：Worker工具调用检测

    期望：
    - TOOL:开头的内容应该被识别为工具调用
    - 非TOOL:开头的内容应该调用LLM
    """
    print("\n" + "="*70)
    print("测试Bug 2：Worker工具调用检测")
    print("="*70)

    # 测试1：工具调用（应该走工具）
    print("\n测试1：TOOL:格式的工具调用")
    task_data = {
        "content": 'TOOL:exec_command|{"command":"echo test123"}'
    }

    response = requests.post(f"{GATEWAY_URL}/tasks", json=task_data)
    task_id = response.json()["task_id"]
    print(f"任务ID: {task_id}")

    # 等待执行
    time.sleep(5)

    # 获取结果
    result = requests.get(f"{GATEWAY_URL}/tasks/{task_id}").json()

    if result["metadata"]["type"] == "tool":
        print(f"✅ 正确识别为工具调用")
        print(f"  元数据类型: {result['metadata']['type']}")
        print(f"  工具名称: {result['metadata'].get('tool_name')}")
        return True
    else:
        print(f"❌ 错误！应该识别为工具调用，但识别为: {result['metadata']['type']}")
        return False


def test_all():
    """运行所有测试"""
    print("\n" + "="*70)
    print("Bug修复验证测试")
    print("="*70)

    results = {
        "Bug 1（工作目录）": False,
        "Bug 2（工具检测）": False
    }

    # 测试Bug 1
    try:
        results["Bug 1（工作目录）"] = test_bug1_working_directory()
    except Exception as e:
        print(f"\n❌ Bug 1测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 等待一下，避免任务堆积
    time.sleep(2)

    # 测试Bug 2
    try:
        results["Bug 2（工具检测）"] = test_bug2_tool_detection()
    except Exception as e:
        print(f"\n❌ Bug 2测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 总结
    print("\n" + "="*70)
    print("测试结果总结")
    print("="*70)

    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(results.values())

    print()
    if all_passed:
        print("🎉 所有测试通过！Bug修复成功！")
    else:
        print("⚠️ 部分测试失败，需要继续调试")

    print("="*70)

    return all_passed


if __name__ == "__main__":
    try:
        success = test_all()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        exit(1)
