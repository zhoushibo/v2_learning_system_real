# -*- coding: utf-8 -*-
"""逐步测试Worker初始化"""
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

print("="*70)
print("步骤1：切换目录")
print("="*70)
print(f"当前目录: {os.getcwd()}")
print()

print("="*70)
print("步骤2：导入模块")
print("="*70)
try:
    print("导入 queue.redis_queue...")
    from src.queue.redis_queue import RedisTaskQueue
    print("[OK] RedisQueue导入成功")

    print("导入 store.hybrid_store...")
    from src.store.hybrid_store import HybridTaskStore
    print("[OK] HybridTaskStore导入成功")

    print("导入 worker.enhanced_worker...")
    from src.worker.enhanced_worker import get_enhanced_worker
    print("[OK] EnhancedWorker导入成功")

    print("导入 common.models.Task...")
    from src.common.models import Task
    print("[OK] Task导入成功")
except Exception as e:
    print(f"[X] 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("="*70)
print("步骤3：初始化组件")
print("="*70)
try:
    print("初始化 RedisQueue...")
    queue = RedisTaskQueue()
    redis_ok = queue.test_connection()
    print(f"  Redis连接: {'[OK]' if redis_ok else '[X]'}")

    print("初始化 HybridTaskStore...")
    store = HybridTaskStore()
    storage_status = store.test_connection()
    print(f"  存储模式: {storage_status.get('storage_mode')}")

    print("初始化 EnhancedWorker...")
    worker = get_enhanced_worker()
    print(f"  Worker实例创建: [OK]")
except Exception as e:
    print(f"[X] 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("="*70)
print("步骤4：测试Redis队列")
print("="*70)
try:
    # 测试提交任务
    test_task = Task(id="test-001", content="测试内容")
    print(f"提交测试任务...")
    success = queue.submit(test_task.id, test_task.content)
    print(f"  提交结果: {'[OK]' if success else '[X]'}")

    # 测试获取任务
    print(f"获取测试任务...")
    task_data = queue.get_task(timeout=2)
    if task_data:
        print(f"  获取结果: [OK]")
        print(f"  任务ID: {task_data['task_id']}")
    else:
        print(f"  获取结果: [超时或空]")
except Exception as e:
    print(f"[X] 队列测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)
print("[完成] 所有初始化步骤完成")
print("="*70)
