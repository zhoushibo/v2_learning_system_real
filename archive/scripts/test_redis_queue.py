# -*- coding: utf-8 -*-
"""测试Redis队列直接操作"""
import sys
import os
import json

# Windows编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 切换到mvp目录
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)
sys.path.insert(0, mvp_dir)

print("[测试1] 导入Redis客户端")
import redis

print("[测试2] 连接Redis")
redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    db=0,
    decode_responses=True
)
redis_client.ping()
print("  [OK] Redis连接成功")

print("[测试3] 检查队列")
queue_key = "tasks:queue"
queue_length = redis_client.llen(queue_key)
print(f"  队列长度: {queue_length}")

# 列出队列中的所有任务
if queue_length > 0:
    print(f"\n[测试4] 列出所有任务")
    tasks = redis_client.lrange(queue_key, 0, -1)
    for i, task_json in enumerate(tasks):
        task = json.loads(task_json)
        print(f"  {i+1}. 任务ID: {task['task_id']}, 内容: {task['task_data'][:50]}...")

print("\n[测试5] 清空队列")
redis_client.delete(queue_key)
print("  [OK] 队列已清空")

print("\n[测试6] 提交新任务")
test_task = {
    "task_id": "test-redis-001",
    "task_data": "TOOL:exec_command|{\"command\":\"echo test\"}"
}
redis_client.lpush(queue_key, json.dumps(test_task))
print(f"  [OK] 任务已提交: {test_task['task_id']}")

print("\n[测试7] 获取任务")
result = redis_client.brpop(queue_key, timeout=2)
if result:
    queue_name, task_json = result
    task = json.loads(task_json)
    print(f"  [OK] 获取成功")
    print(f"  任务ID: {task['task_id']}")
    print(f"  内容: {task['task_data']}")
else:
    print(f"  [超时] 未获取到任务")

print("\n[完成] Redis测试结束")
