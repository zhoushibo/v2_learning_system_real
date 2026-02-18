# -*- coding: utf-8 -*-
"""测试Worker主循环"""
import sys
import os
import asyncio

# Windows编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 切换到mvp目录
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)
sys.path.insert(0, mvp_dir)

print("[测试1] 导入模块")
from src.worker.enhanced_worker import get_enhanced_worker
from src.queue.redis_queue import RedisTaskQueue
from src.store.hybrid_store import HybridTaskStore
from src.common.models import Task

print("[测试2] 初始化组件")
worker = get_enhanced_worker()
queue = RedisTaskQueue()
store = HybridTaskStore()

print("[测试3] 提交测试任务")
test_task = Task(id="test-loop-001", content='TOOL:exec_command|{"command":"echo test"}')
queue.submit(test_task.id, test_task.content)
store.save_task(test_task)

print(f"[测试4] 模拟Worker主循环（只运行一次）")
print(f"[测试5] 获取任务...")
task_data = queue.get_task(timeout=2)

if task_data:
    task_id = task_data["task_id"]
    content = task_data["task_data"]
    task = Task(id=task_id, content=content)

    print(f"[测试6] 执行任务 {task_id}")
    task = asyncio.run(worker.execute_task(task))

    print(f"[测试7] 保存结果")
    store.save_task(task)

    print(f"[结果]")
    print(f"  状态: {task.status}")
    print(f"  结果: {task.result[:100] if task.result else ''}")
    print(f"  错误: {task.error}")
    print(f"  元数据: {task.metadata}")
else:
    print("[结果] 未获取到任务（超时）")

print("\n[测试8] 清理...")
asyncio.run(worker.close())
print("[完成] 测试结束")
