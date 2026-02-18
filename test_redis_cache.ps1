import redis
import json

# 连接Redis
r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

# 查看所有的tasks:cached:*键
keys = r.keys('tasks:cached:*')
print(f'Redis缓存中的任务数量: {len(keys)}')
print()

if keys:
    print('缓存的任务:')
    for key in keys[:5]:  # 只显示前5个
        data = r.get(key)
        task = json.loads(data)
        task_id = task['task_id'][:8] + '...'
        status = task['status']
        content = task['content'][:30]
        print(f'  {key}: {task_id} | {status} | {content}')
else:
    print('  缓存中没有任务')
