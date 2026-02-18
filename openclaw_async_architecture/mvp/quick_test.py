# -*- coding: utf-8 -*-
"""V2 MVP 快速启动和测试"""
import requests
import time
import json
import sys

# Windows编码修复
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'


def test_v2_mvp():
    """测试V2 MVP"""

    print("="*70)
    print("🧪 V2 MVP 快速测试")
    print("="*70)

    # 1. 健康检查
    print("\n1. 健康检查...")
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        health = response.json()

        print(f"   ✅ Gateway状态: {health['status']}")
        print(f"   ✅ Redis队列: {health['components']['redis_queue']}")
        print(f"   ✅ Redis缓存: {health['components']['redis_cache']}")
        print(f"   ✅ SQLite存储: {health['components']['sqlite_persistence']}")
        print(f"   ✅ 存储模式: {health['components']['storage_mode']}")
        print(f"   ✅ V1兼容: {health['v1_compatible']}")
    except Exception as e:
        print(f"   ❌ 健康检查失败: {e}")
        print(f"   提示: 请先启动Gateway (python launcher.py gateway)")
        return False

    # 2. 提交测试任务
    print("\n2. 提交测试任务...")
    test_tasks = [
        "简单介绍一下你自己",
        "现在马上回答：中国的首都是哪里？",
        "深入分析人工智能对社会的影响"
    ]

    task_ids = []

    for i, task_content in enumerate(test_tasks, 1):
        print(f"   任务{i}: {task_content[:30]}...")

        try:
            response = requests.post(
                "http://127.0.0.1:8000/tasks",
                json={"content": task_content}
            )
            task_id = response.json()["task_id"]
            task_ids.append(task_id)
            print(f"      ✅ 提交成功: {task_id}")
        except Exception as e:
            print(f"      ❌ 提交失败: {e}")
            return False

    # 3. 等待任务完成
    print("\n3. 等待任务处理...")
    results = []

    for i, (task_id, task_content) in enumerate(zip(task_ids, test_tasks), 1):
        print(f"   任务{i}: {task_content[:30]}...")

        max_wait = 30
        for j in range(max_wait):
            try:
                response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
                task = response.json()

                if task["status"] == "completed":
                    print(f"      ✅ 完成！模型: {task['metadata']['model']}, 耗时: {task['metadata']['latency']:.2f}秒")
                    print(f"      结果: {task['result'][:100]}...")
                    results.append(task)
                    break
                elif task["status"] == "failed":
                    print(f"      ❌ 失败: {task.get('error', '未知错误')}")
                    break
                else:
                    if j % 5 == 0:
                        print(f"      ⏳ 处理中... {j+1}/{max_wait}秒")
                    time.sleep(1)
            except Exception as e:
                print(f"      ❌ 查询失败: {e}")
                return False

    # 4. 统计信息
    print("\n4. 统计信息...")
    print(f"   总任务数: {len(results)}")

    if results:
        models = {}
        total_latency = 0
        total_tokens = 0

        for task in results:
            model = task['metadata']['model']
            models[model] = models.get(model, 0) + 1
            total_latency += task['metadata']['latency']
            total_tokens += task['metadata']['usage']['total_tokens']

        print(f"   平均延迟: {total_latency/len(results):.2f}秒")
        print(f"   总Token: {total_tokens}")
        print(f"   模型分布:")
        for model, count in models.items():
            print(f"      {model}: {count}次")

    # 5. 测试总结
    print("\n" + "="*70)
    print("🎉 V2 MVP 测试完成！")
    print("="*70)

    if len(results) == len(task_ids):
        print("\n✅ 所有测试通过！")
        print("   V2 MVP已准备就绪，可以开始实际工作！")
        return True
    else:
        print(f"\n⚠️  部分测试失败 ({len(results)}/{len(task_ids)} 通过)")
        print("   请检查Worker是否正常运行")
        return False


def show_usage_example():
    """显示使用示例"""
    print("="*70)
    print("📖 V2 MVP 使用示例")
    print("="*70)

    example_code = '''
# 示例1: 提交简单任务
import requests

# 提交任务
response = requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": "介绍一下你自己"}
)

task_id = response.json()["task_id"]
print(f"任务ID: {task_id}")

# 查询结果
response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
result = response.json()
print(f"状态: {result['status']}")
print(f"模型: {result['metadata']['model']}")
print(f"结果: {result['result']}")


# 示例2: 提交多个任务
tasks = [
    "什么是AI？",
    "深入分析人工智能的影响",
    "翻译这句话到英文"
]

for task in tasks:
    response = requests.post(
        "http://127.0.0.1:8000/tasks",
        json={"content": task}
    )
    print(f"提交成功: {response.json()['task_id']}")


# 示例3: 查询所有任务
response = requests.get("http://127.0.0.1:8000/tasks")
tasks = response.json()["tasks"]

print(f"总任务数: {len(tasks)}")
for task in tasks:
    print(f"  {task['task_id']}: {task['status']}")
'''

    print("\nPython代码示例:")
    print(example_code)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="V2 MVP 快速启动和测试")
    parser.add_argument("command", choices=["test", "example"], help="命令")

    args = parser.parse_args()

    if args.command == "test":
        success = test_v2_mvp()
        sys.exit(0 if success else 1)
    elif args.command == "example":
        show_usage_example()
