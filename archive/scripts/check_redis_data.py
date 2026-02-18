"""检查Redis队列中的数据"""

import redis
import json

# 连接Redis
r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

print("="*60)
print("检查Redis队列数据")
print("="*60)

# 1. 检查队列长度
queue_length = r.llen("tasks:queue")
print(f"\n队列长度: {queue_length}")

# 2. 查看队列前3项
print("\n队列中的任务:")
for i in range(min(3, queue_length)):
    task_json = r.lindex("tasks:queue", i)
    task_data = json.loads(task_json)
    print(f"\n[{i+1}] Task ID: {task_data['task_id']}")
    print(f"    Content: {task_data['task_data'][:100]}...")

# 3. 检查所有key中的tasks相关数据
print("\n\n所有tasks相关的Redis key:")
keys = r.keys("tasks:*")
for key in keys:
    value = r.get(key)
    print(f"\nKey: {key}")
    print(f"Type: {r.type(key)}")

    if key.startswith("tasks:cached:"):
        # 这是缓存的任务
        task = json.loads(value)
        print(f"Status: {task.get('status', 'unknown')}")
        print(f"Content: {task.get('content', 'N/A')[:100]}...")

print("\n" + "="*60)
