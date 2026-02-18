"""分步测试Worker初始化"""

import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

print("[步骤1] 切换目录")
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)
sys.path.insert(0, mvp_dir)
print(f"  当前目录: {os.getcwd()}")

print("\n[步骤2] 导入config")
from src.common.config import settings
print("  [OK] config导入成功")

print("\n[步骤3] 导入models")
from src.common.models import Task
print("  [OK] models导入成功")

print("\n[步骤4] 导入redis_queue")
from src.queue.redis_queue import RedisTaskQueue
print("  [OK] redis_queue导入成功")

print("\n[步骤5] 创建RedisQueue实例")
try:
    queue = RedisTaskQueue()
    ok = queue.test_connection()
    print(f"  Redis连接: {'[OK]' if ok else '[X]'}")
except Exception as e:
    print(f"  [X] 创建失败: {e}")
    import traceback
    traceback.print_exc()

print("\n[步骤6] 导入hybrid_store")
from src.store.hybrid_store import HybridTaskStore
print("  [OK] hybrid_store导入成功")

print("\n[步骤7] 创建HybridTaskStore实例")
try:
    store = HybridTaskStore()
    status = store.test_connection()
    print(f"  Redis: {'[OK]' if status.get('redis_connected') else '[X]'}")
    print(f"  SQLite: {'[OK]' if status.get('sqlite_connected') else '[X]'}")
    print(f"  模式: {status.get('storage_mode')}")
except Exception as e:
    print(f"  [X] 创建失败: {e}")
    import traceback
    traceback.print_exc()

print("\n[步骤8] 导入enhanced_worker")
try:
    from src.worker.enhanced_worker import get_enhanced_worker
    print("  [OK] enhanced_worker导入成功")
except Exception as e:
    print(f"  [X] 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n[步骤9] 创建Worker实例")
try:
    worker = get_enhanced_worker()
    print("  [OK] Worker创建成功")
except Exception as e:
    print(f"  [X] 创建失败: {e}")
    import traceback
    traceback.print_exc()

print("\n[完成] 所有步骤完成")
