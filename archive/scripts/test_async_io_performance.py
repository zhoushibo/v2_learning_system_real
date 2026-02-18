# -*- coding: utf-8 -*-
"""测试异步I/O性能对比"""

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

print("="*70)
print("异步I/O性能对比测试")
print("="*70)

# 创建测试文件
test_file = "test_async_io.txt"
test_content = "测试内容\n" * 1000  # 10KB

# 写入测试文件
with open(test_file, 'w', encoding='utf-8') as f:
    f.write(test_content)

print(f"\n[测试文件]")
print(f"  路径: {test_file}")
print(f"  大小: {os.path.getsize(test_file)} 字节")

# ====== 同步I/O测试 ======
print("\n" + "="*70)
print("测试1: 同步I/O（open/read）")
print("="*70)

sync_times = []

for i in range(20):
    start_time = time.time()
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        elapsed = time.time() - start_time
        sync_times.append(elapsed)
    except Exception as e:
        print(f"  [错误] 第{i+1}次失败: {e}")
        break

print(f"\n[同步I/O结果]")
print(f"  次数: {len(sync_times)}")
print(f"  总耗时: {sum(sync_times):.3f} 秒")
print(f"  平均: {mean(sync_times) * 1000:.2f} 毫秒")
print(f"  中位数: {median(sync_times) * 1000:.2f} 毫秒")
print(f"  最小: {min(sync_times) * 1000:.2f} 毫秒")
print(f"  最大: {max(sync_times) * 1000:.2f} 毫秒")

# ====== 异步I/O测试 ======
print("\n" + "="*70)
print("测试2: 异步I/O（aiofiles）")
print("="*70)

import aiofiles

async def test_async_read():
    """异步读取测试"""
    async_times = []

    for i in range(20):
        start_time = time.time()
        try:
            async with aiofiles.open(test_file, mode='r', encoding='utf-8') as f:
                content = await f.read()
            elapsed = time.time() - start_time
            async_times.append(elapsed)
        except Exception as e:
            print(f"  [错误] 第{i+1}次失败: {e}")
            break

    return async_times

async_times = asyncio.run(test_async_read())

print(f"\n[异步I/O结果]")
print(f"  次数: {len(async_times)}")
print(f"  总耗时: {sum(async_times):.3f} 秒")
print(f"  平均: {mean(async_times) * 1000:.2f} 毫秒")
print(f"  中位数: {median(async_times) * 1000:.2f} 毫秒")
print(f"  最小: {min(async_times) * 1000:.2f} 毫秒")
print(f"  最大: {max(async_times) * 1000:.2f} 毫秒")

# ====== 性能对比 ======
print("\n" + "="*70)
print("性能对比分析")
print("="*70)

if sync_times and async_times:
    sync_avg = mean(sync_times)
    async_avg = mean(async_times)
    speedup = sync_avg / async_avg
    improvement = (1 - async_avg / sync_avg) * 100

    print(f"\n[平均耗时]")
    print(f"  同步I/O: {sync_avg * 1000:.2f} 毫秒")
    print(f"  异步I/O: {async_avg * 1000:.2f} 毫秒")
    print(f"  加速比: {speedup:.2f}x")
    print(f"  性能提升: {improvement:.1f}%")

    print(f"\n[中位数耗时]")
    sync_med = median(sync_times) * 1000
    async_med = median(async_times) * 1000
    print(f"  同步I/O: {sync_med:.2f} 毫秒")
    print(f"  异步I/O: {async_med:.2f} 毫秒")
    print(f"  加速比: {sync_med / async_med:.2f}x")

    print(f"\n[结论]")
    if speedup > 2:
        print(f"  [OK] 异步I/O性能提升显著（>2x）")
    elif speedup > 1.5:
        print(f"  [WARNING] 异步I/O性能提升一般（>1.5x）")
    else:
        print(f"  [INFO] 异步I/O性能提升不明显（<1.5x）")
        print(f"  原因：小文件读取I/O占比较小，大文件测试会更明显")

# ====== 并发I/O测试 ======
print("\n" + "="*70)
print("测试3: 并发读取性能（10个文件）")
print("="*70)

# 创建10个测试文件
test_files = []
for i in range(10):
    file_path = f"test_async_{i}.txt"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"文件{i}\n" * 100)
    test_files.append(file_path)

# 同步顺序读取
print("\n[同步顺序读取]")
start_time = time.time()
for file_path in test_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
sync_sequential_time = time.time() - start_time
print(f"  耗时: {sync_sequential_time * 1000:.2f} 毫秒")

# 异步并发读取
print("\n[异步并发读取]")
async def read_all_async():
    tasks = []
    for file_path in test_files:
        task = _async_read_file(file_path)
        tasks.append(task)
    return await asyncio.gather(*tasks)

async def _async_read_file(file_path):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        return await f.read()

start_time = time.time()
asyncio.run(read_all_async())
async_concurrent_time = time.time() - start_time
print(f"  耗时: {async_concurrent_time * 1000:.2f} 毫秒")

# 并发加速比
concurrent_speedup = sync_sequential_time / async_concurrent_time
print(f"\n[并发加速比]")
print(f"  加速比: {concurrent_speedup:.2f}x")
print(f"  性能提升: {(1 - async_concurrent_time / sync_sequential_time) * 100:.1f}%")

# 清理测试文件
try:
    for file_path in test_files + [test_file]:
        if os.path.exists(file_path):
            os.remove(file_path)
    print("\n[清理] 测试文件已删除")
except Exception as e:
    print(f"\n[警告] 清理失败: {e}")

print("\n" + "="*70)
print("测试完成")
print("="*70)

print("\n[总结]")
if sync_times and async_times:
    print(f"  单个文件读取加速比: {speedup:.2f}x")
print(f"  并发读取加速比: {concurrent_speedup:.2f}x")
print()

if concurrent_speedup > 2:
    print("  [Phase 2] 异步I/O优化: [OK] 达到预期（>2x加速）")
elif concurrent_speedup > 1.5:
    print("  [Phase 2] 异步I/O优化: [WARNING] 基本达标（>1.5x加速）")
else:
    print("  [Phase 2] 异步I/O优化: [INFO] 小文件场景不明显")

print("\n[完成]")
