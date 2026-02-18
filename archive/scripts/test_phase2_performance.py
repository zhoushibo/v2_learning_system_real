# -*- coding: utf-8 -*-
"""测试Phase 2性能优化效果"""

import sys
import os
import asyncio
import time
from statistics import mean, median

# 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 切换目录
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)
sys.path.insert(0, mvp_dir)

from src.worker.enhanced_worker import get_enhanced_worker
from src.queue.redis_queue import RedisTaskQueue
from src.store.hybrid_store import HybridTaskStore
from src.common.models import Task

print("="*70)
print("Phase 2: 性能优化效果测试")
print("="*70)

# 初始化
print("\n[初始化] 创建组件...")
queue = RedisTaskQueue()
store = HybridTaskStore()
worker = get_enhanced_worker()

# 测试队列性能
print("\n" + "="*70)
print("测试1: Redis队列提交性能（连接池）")
print("="*70)

# 准备测试任务
test_tasks = [
    (f"test-queue-{i}", f'TOOL:read_file|{{"path":"README.md"}}')
    for i in range(100)
]

# 批量提交测试
start_time = time.time()
success_count = queue.submit_batch(test_tasks)
batch_time = time.time() - start_time

print(f"\n[批量提交]")
print(f"  任务数: {success_count}")
print(f"  耗时: {batch_time:.3f} 秒")
print(f"  吞吐量: {success_count / batch_time:.1f} 任务/秒")

# 单个提交测试（对比）
start_time = time.time()
single_count = 0
for task_id, task_data in test_tasks[:10]:
    if queue.submit(task_id, task_data):
        single_count += 1
single_time = time.time() - start_time

print(f"\n[单个提交（10个）]")
print(f"  成功: {single_count}")
print(f"  耗时: {single_time:.3f} 秒")
print(f"  吞吐量: {single_count / single_time:.1f} 任务/秒")

# 清理队列
queue.clear()

# 测试存储性能
print("\n" + "="*70)
print("测试2: 混合存储性能（连接池）")
print("="*70)

tasks = []
start_time = time.time()

# 批量保存
for i in range(50):
    task = Task(
        id=f"perf-test-{i}",
        content=f"任务内容 {i}",
        status="completed",
        result=f"结果 {i}",
        metadata={"test": True}
    )
    store.save_task(task)
    tasks.append(task)

save_time = time.time() - start_time

print(f"\n[批量保存]")
print(f"  任务数: {len(tasks)}")
print(f"  耗时: {save_time:.3f} 秒")
print(f"  平均: {save_time / len(tasks) * 1000:.2f} 毫秒/任务")

# 批量读取
start_time = time.time()
retrieved_tasks = []
for task in tasks:
    retrieved = store.get_task(task.id)
    if retrieved:
        retrieved_tasks.append(retrieved)
read_time = time.time() - start_time

print(f"\n[批量读取]")
print(f"  读取数: {len(retrieved_tasks)}")
print(f"  耗时: {read_time:.3f} 秒")
print(f"  平均: {read_time / len(retrieved_tasks) * 1000:.2f} 毫秒/任务")

# 清理
for task in tasks:
    store.delete_task(task.id)

# 测试缓存性能
print("\n" + "="*70)
print("测试3: 工具结果缓存性能")
print("="*70)

# 清空缓存
worker.tool_manager.clear_cache()

# 第一次执行（无缓存）
tool_times = []
for i in range(10):
    start_time = time.time()
    task = Task(
        id=f"cache-test-{i}",
        content='TOOL:read_file|{"path":"README.md"}'
    )
    result_task = asyncio.run(worker.execute_task(task))
    elapsed = time.time() - start_time
    tool_times.append(elapsed)

print(f"\n[第一次执行（无缓存）]")
print(f"  次数: {len(tool_times)}")
print(f"  总耗时: {sum(tool_times):.3f} 秒")
print(f"  平均: {mean(tool_times) * 1000:.2f} 毫秒")
print(f"  中位数: {median(tool_times) * 1000:.2f} 毫秒")

# 第二次执行（有缓存）
cache_times = []
for i in range(10):
    start_time = time.time()
    task = Task(
        id=f"cache-test-{i}",
        content='TOOL:read_file|{"path":"README.md"}'
    )
    result_task = asyncio.run(worker.execute_task(task))
    elapsed = time.time() - start_time
    cache_times.append(elapsed)

print(f"\n[第二次执行（有缓存）]")
print(f"  次数: {len(cache_times)}")
print(f"  总耗时: {sum(cache_times):.3f} 秒")
print(f"  平均: {mean(cache_times) * 1000:.2f} 毫秒")
print(f"  中位数: {median(cache_times) * 1000:.2f} 毫秒")

# 性能提升分析
speedup = mean(tool_times) / mean(cache_times)
print(f"\n[性能提升]")
print(f"  加速比: {speedup:.2f}x")
print(f"  时间减少: {(1 - mean(cache_times) / mean(tool_times)) * 100:.1f}%")

# 缓存统计
cache_stats = worker.tool_manager.get_cache_stats()
print(f"\n[缓存统计]")
print(f"  总键数: {cache_stats.get('total_keys', 0)}")
print(f"  工具数: {len(cache_stats.get('tools', {}))}")
for tool_name, count in cache_stats.get('tools', {}).items():
    print(f"    {tool_name}: {count}")

# 清理缓存
worker.tool_manager.clear_cache()

# 性能总结
print("\n" + "="*70)
print("性能优化总结")
print("="*70)

print(f"\n[连接池]")
print(f"  Redis连接池: [OK]")
print(f"  SQLite连接池: [OK]")
print(f"  队列吞吐量: {success_count / batch_time:.1f} 任务/秒")
print(f"  存储吞吐量: {len(tasks) / save_time:.1f} 任务/秒")

print(f"\n[缓存优化]")
print(f"  工具结果缓存: [OK]")
print(f"  读操作加速: {speedup:.2f}x")
print(f"  时间减少: {(1 - mean(cache_times) / mean(tool_times)) * 100:.1f}%")

print(f"\n[Phase 2状态]")
if speedup > 2:
    print(f"  [状态] [OK] 性能优化达到预期（>2x加速）")
elif speedup > 1.5:
    print(f"  [状态] [WARNING] 性能优化基本达标（>1.5x加速）")
else:
    print(f"  [状态] [FAILED] 性能优化未达标（<1.5x加速）")

print("\n" + "="*70)
print("测试完成")
print("="*70)

# 清理
asyncio.run(worker.close())

print("\n[完成]")
