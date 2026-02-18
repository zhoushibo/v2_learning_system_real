"""简化Worker测试"""

import sys
import os
import asyncio

# 编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 切换目录
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)
sys.path.insert(0, mvp_dir)

print("[1] 导入模块...")
from src.worker.enhanced_worker import get_enhanced_worker
from src.queue.redis_queue import RedisTaskQueue
from src.store.hybrid_store import HybridTaskStore
from src.common.models import Task

print("[2] 初始化组件...")
worker = get_enhanced_worker()
queue = RedisTaskQueue()
store = HybridTaskStore()

print("[3] 测试Redis连接...")
if not queue.test_connection():
    print("[X] Redis连接失败!")
    sys.exit(1)

print("[4] 开始任务循环（最多5次）...")
for i in range(5):
    print(f"  尝试获取任务 #{i+1}...")
    task_data = queue.get_task(timeout=2)
    
    if task_data:
        print(f"  [OK] 获取到任务: {task_data['task_id']}")
        
        task = Task(id=task_data['task_id'], content=task_data['task_data'])
        
        print(f"  执行任务...")
        task = asyncio.run(worker.execute_task(task))
        
        print(f"  保存结果...")
        store.save_task(task)
        
        print(f"  完成: {task.status}")
    else:
        print(f"  [空] 队列空，尝试下一个...")

print("[5] 清理...")
asyncio.run(worker.close())
print("[完成] 测试结束")
