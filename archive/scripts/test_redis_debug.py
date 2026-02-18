# -*- coding: utf-8 -*-
"""测试Redis队列 - 详细调试"""
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

import redis

print("="*70)
print("Redis深度调试测试")
print("="*70)

# 创建普通Redis客户端（非decode_responses）
print("\n[步骤1] 连接Redis（非decode模式）")
redis_raw = redis.Redis(host="127.0.0.1", port=6379, db=0)
redis_raw.ping()
print("  [OK] 连接成功")

print("\n[步骤2] 清空队列")
queue_key = b"tasks:queue"  # bytes类型
redis_raw.delete(queue_key)
print("  [OK] 队列已清空")

print("\n[步骤3] 提交任务（使用lpush）")
test_task = {
    "task_id": "test-debug-001",
    "task_data": "TOOL:exec_command|{\"command\":\"echo test\"}"
}
task_json = json.dumps(test_task)
print(f"  任务JSON: {task_json}")
print(f"  JSON长度: {len(task_json)}")

result = redis_raw.lpush(queue_key, task_json)
print(f"  lpush返回值: {result}")
print(f"  [OK] 任务已提交")

print("\n[步骤4] 检查队列长度")
length = redis_raw.llen(queue_key)
print(f"  队列长度: {length}")

if length > 0:
    print("\n[步骤5] 使用lrange读取所有任务")
    all_tasks = redis_raw.lrange(queue_key, 0, -1)
    print(f"  任务数量: {len(all_tasks)}")
    for i, task in enumerate(all_tasks):
        print(f"  任务{i}: {task[:50]}...")

print("\n[步骤6] 使用rpop获取任务（非阻塞）")
task = redis_raw.rpop(queue_key)
if task:
    print(f"  [OK] 获取成功: {task}")
    task_dict = json.loads(task)
    print(f"  任务ID: {task_dict['task_id']}")
else:
    print(f"  [结果] 队列为空")

print("\n[步骤7] 重新提交任务并使用brpop获取")
redis_raw.lpush(queue_key, task_json)
print(f"  [OK] 任务已重新提交")

print(f"\n  调用 brpop（timeout=2秒）...")
brpop_result = redis_raw.brpop(queue_key, timeout=2)
if brpop_result:
    queue_name, task_data = brpop_result
    print(f"  [OK] brpop获取成功")
    print(f"  队列名称: {queue_name}")
    print(f"  任务数据: {task_data}")
else:
    print(f"  [超时] brpop返回None")

print("\n[步骤8] 检查Redis数据库大小（所有Keys）")
db_size = redis_raw.dbsize()
print(f"  数据库大小: {db_size} keys")

if db_size > 0:
    print(f"\n  列出所有Keys:")
    all_keys = redis_raw.keys(b"*")
    for key in all_keys:
        key_type = redis_raw.type(key)
        print(f"    - {key.decode()} (类型: {key_type.decode()})")

print("\n[完成] Redis调试结束")
print("="*70)
