# -*- coding: utf-8 -*-
"""启动Worker并输出所有日志"""
import sys
import os
import asyncio

# Windows编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    print(f"[调试] 编码已修复为UTF-8")

# 切换到mvp目录
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)
sys.path.insert(0, mvp_dir)

print(f"[调试] 当前目录: {os.getcwd()}")
print(f"[调试] Python路径第一项: {sys.path[0]}")
print()

# 导入并运行
print("[调试] 开始导入Worker模块...")
from src.worker.main import run_worker

print("[调试] Worker模块导入成功，开始运行...")
try:
    asyncio.run(run_worker())
except KeyboardInterrupt:
    print("\n[调试] Worker被中断")
except Exception as e:
    print(f"\n[调试] Worker运行错误: {e}")
    import traceback
    traceback.print_exc()
