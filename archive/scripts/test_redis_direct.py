# -*- coding: utf-8 -*-
"""测试Redis队列 - 使用不同的键名"""
import sys
import os
import json

# Windows编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import redis

print("="*70)
print("测试Redis队列 - 使用直接键名")
print("="*70)

# 创建Redis客户端
redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)
redis_client.ping()
print("[OK] Redis连接成功")

print("\n[测试1] 检查当前数据库")
db_num = redis_client.client_list()[0]['db']
print(f"  当前数据库: db{db_num}")

print("\n[测试2] 列出所有匹配tasks:的键")
all_task_keys = redis_client.keys("tasks*")
print(f"  找到 {len(all_task_keys)} 个keys:")
for key in all_task_keys:
    key_type = redis_client.type(key)
    if key_type == 'list':
        print(f"    - {key} (类型: {key_type}, 长度: {redis_client.llen(key)})")
    else:
        print(f"    - {key} (类型: {key_type})")

print("\n[测试3] 清空所有队列")
for key in all_task_keys:
    if redis_client.type(key) == 'list':
        redis_client.delete(key)
        print(f"  [OK] 清空: {key}")

print("\n[测试4] 测试简单的List操作")
test_list_key = "test_list_123"

# 添加元素
for i in range(3):
    redis_client.lpush(test_list_key, f"item-{i}")

length = redis_client.llen(test_list_key)
print(f"  [OK] 添加3个元素，列表长度: {length}")

# 使用rpop获取
item = redis_client.rpop(test_list_key)
print(f"  [OK] 使用rpop获取: {item}")

print("\n[测试5] 测试brpop")
redis_client.lpush(test_list_key, "item-new")
result = redis_client.brpop(test_list_key, timeout=2)
if result:
    print(f"  [OK] brpop获取成功: {result}")
else:
    print(f"  [超时] brpop返回None")

print("\n[测试6] 使用不同的队列键名")
queue_key = "my_tasks_queue_v1"  # 不使用冒号
test_task = {
    "task_id": "test-final-001",
    "task_data": "TOOL:exec_command|{\"command\":\"echo test\"}"
}

# 清空
print(f"  清空队列...")
redis_client.delete(queue_key)
print(f"  delete命令返回: None")

# 检查key是否存在
exists = redis_client.exists(queue_key)
print(f"  key是否存在: {exists}")

# 添加
print(f"  lpush任务...")
result = redis_client.lpush(queue_key, json.dumps(test_task))
print(f"  lpush返回: {result}")

# 检查key是否存在
exists = redis_client.exists(queue_key)
print(f"  key是否存在: {exists}")

# 检查key类型
key_type = redis_client.type(queue_key)
print(f"  key类型: {key_type}")

# 检查长度
length = redis_client.llen(queue_key)
print(f"  队列长度: {length}")

# 使用lrange检查所有元素
print(f"  使用lrange检查所有元素:")
all = redis_client.lrange(queue_key, 0, -1)
print(f"  元素数量: {len(all)}")
for i, item in enumerate(all):
    print(f"    - 元素{i}: {item}")

# 获取
print(f"  使用rpop获取...")
item = redis_client.rpop(queue_key)
print(f"  rpop获取: {item}")

# 再次检查长度
length_after = redis_client.llen(queue_key)
print(f"  rpop后队列长度: {length_after}")

print("\n[完成]")
