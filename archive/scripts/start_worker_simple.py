# -*- coding: utf-8 -*-
"""启动Worker的简化脚本"""
import sys
import os

# Windows编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 切换到mvp目录
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)

# 添加到路径
sys.path.insert(0, mvp_dir)

# 导入并运行
print(f"当前目录: {os.getcwd()}")
print(f"Python路径: {sys.path[:3]}")
print()

from src.worker.main import run_worker
import asyncio
try:
    asyncio.run(run_worker())
except KeyboardInterrupt:
    print("\nWorker已停止")
