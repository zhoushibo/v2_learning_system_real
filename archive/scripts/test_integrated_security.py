# -*- coding: utf-8 -*-
"""测试集成安全框架后的工具"""

import sys
import os
import asyncio

# 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 切换目录
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)
sys.path.insert(0, mvp_dir)

from src.worker.enhanced_worker import get_enhanced_worker
from src.queue.redis_queue import RedisTaskQueue
from src.store.hybrid_store import HybridTaskStore
from src.common.models import Task

print("="*70)
print("集成安全框架测试")
print("="*70)

# 初始化
print("\n[初始化] 创建Worker和组件...")
worker = get_enhanced_worker()
queue = RedisTaskQueue()
store = HybridTaskStore()

# 测试队列
test_queue = []

# 测试1：安全的命令执行
print("\n[测试1] 安全的命令执行")
task1 = Task(
    id="security-test-001",
    content='TOOL:exec_command|{"command":"ls"}'
)
queue.submit(task1.id, task1.content)
test_queue.append((task1.id, task1.content))

# 测试2：危险的命令尝试
print("\n[测试2] 危险的命令尝试 (rm -rf)")
task2 = Task(
    id="security-test-002",
    content='TOOL:exec_command|{"command":"rm -rf /"}'
)
queue.submit(task2.id, task2.content)
test_queue.append((task2.id, task2.content))

# 测试3：路径遍历攻击
print("\n[测试3] 路径遍历攻击")
task3 = Task(
    id="security-test-003",
    content='TOOL:read_file|{"path":"../Windows/System32/drivers/etc/hosts"}'
)
queue.submit(task3.id, task3.content)
test_queue.append((task3.id, task3.content))

# 测试4：危险Python函数
print("\n[测试4] 危险Python函数")
task4 = Task(
    id="security-test-004",
    content='TOOL:exec_python|{"code":"with open(\\"/etc/passwd\\") as f: print(f.read())"}'
)
queue.submit(task4.id, task4.content)
test_queue.append((task4.id, task4.content))

# 测试5：安全的Python代码
print("\n[测试5] 安全的Python代码")
task5 = Task(
    id="security-test-005",
    content='TOOL:exec_python|{"code":"result = 1 + 1; print(result)"}'
)
queue.submit(task5.id, task5.content)
test_queue.append((task5.id, task5.content))

# 测试6：安全的文件读取
print("\n[测试6] 安全的文件读取")
task6 = Task(
    id="security-test-006",
    content='TOOL:read_file|{"path":"test_security.py"}'
)
queue.submit(task6.id, task6.content)
test_queue.append((task6.id, task6.content))

# 模拟Worker处理任务
print("\n[Worker] 开始处理任务...")
results = []

for i, (task_id, content) in enumerate(test_queue, 1):
    print(f"\n[任务 {i}] {task_id}")
    print(f"  内容: {content[:60]}...")

    # 获取任务
    task_data = queue.get_task(timeout=2)
    if task_data:
        # 执行任务
        task_obj = Task(id=task_data['task_id'], content=task_data['task_data'])
        result_task = asyncio.run(worker.execute_task(task_obj))

        results.append((task_id, result_task))

        print(f"  状态: {result_task.status}")
        print(f"  结果: {result_task.result[:100] if result_task.result else 'None'}")
        print(f"  错误: {result_task.error[:100] if result_task.error else 'None'}")
        print(f"  类型: {result_task.metadata.get('type')}")

        # 验证安全性
        if result_task.status == "failed":
            error = result_task.error or ""
            if "安全" in error or "安全" in error:
                print(f"  [安全] 攻击被阻止 ✓")
            else:
                print(f"  [!] 未知错误")
        else:
            print(f"  [危险] 攻击未检测到 ✗")
    else:
        print(f"  [错误] 未获取到任务")

# 总结
print("\n" + "="*70)
print("测试总结")
print("="*70)

safety_tests = [
    ("安全的命令执行", results[0][1].status == "completed"),
    ("危险的命令 (rm -rf)", results[1][1].status == "failed" and "安全" in (results[1][1].error or "")),
    ("路径遍历攻击", results[2][1].status == "failed" and "安全" in (results[2][1].error or "")),
    ("危险Python函数", results[3][1].status == "failed" and "安全" in (results[3][1].error or "")),
    ("安全的Python代码", results[4][1].status == "completed"),
    ("安全的文件读取", results[5][1].status == "completed"),
]

passed = sum(1 for _, success in safety_tests if success)
total = len(safety_tests)

print(f"\n通过: {passed}/{total}")

for name, success in safety_tests:
    status = "[OK] ✓" if success else "[失败] ✗"
    print(f"  {status} {name}")

if passed == total:
    print(f"\n[验证] 所有安全测试通过！✓")
else:
    print(f"\n[失败] 有 {total - passed} 个测试失败 ✗")

# 清理
asyncio.run(worker.close())

print("\n[完成]")
