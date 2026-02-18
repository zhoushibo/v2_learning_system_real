"""快速验证Worker完整流程"""

import sys
import os
import asyncio
import json

# 编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 切换目录
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)
sys.path.insert(0, mvp_dir)

print("[快速验证] Worker完整流程")
print("="*70)

# 导入
from src.worker.enhanced_worker import get_enhanced_worker
from src.queue.redis_queue import RedisTaskQueue
from src.store.hybrid_store import HybridTaskStore
from src.common.models import Task

# 初始化
print("\n[初始化] 创建组件...")
worker = get_enhanced_worker()
queue = RedisTaskQueue()
store = HybridTaskStore()

# 提交任务
print("\n[提交] 手动提交任务...")
task = Task(id="quick-test-001", content='TOOL:exec_command|{"command":"echo BugFixed!"}')
queue.submit(task.id, task.content)
store.save_task(task)
print(f"  任务ID: {task.id}")

# 模拟Worker主循环
print("\n[Worker] 获取任务...")
task_data = queue.get_task(timeout=2)

if task_data:
    print(f"  [OK] 获取成功: {task_data['task_id']}")
    
    # 执行
    print(f"\n[Worker] 执行任务...")
    task_obj = Task(id=task_data['task_id'], content=task_data['task_data'])
    result_task = asyncio.run(worker.execute_task(task_obj))
    
    print(f"\n[结果]")
    print(f"  状态: {result_task.status}")
    print(f"  结果: {result_task.result}")
    
    if result_task.status == "completed" and result_task.result:
        output_data = json.loads(result_task.result)
        stdout = output_data.get('stdout', '').strip()
        print(f"  输出: {stdout}")
        
        # 验证
        if result_task.metadata.get('type') == 'tool' and stdout == 'BugFixed!':
            print(f"\n[验证] Bug修复成功!")
        else:
            print(f"\n[验证] Bug修复结果: {result_task.metadata}")
    else:
        print(f"\n[错误] 任务执行失败：{result_task.error}")
else:
    print(f"  [错误] 未获取到任务")

# 清理
asyncio.run(worker.close())
print("\n[完成]")
