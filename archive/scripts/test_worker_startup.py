# -*- coding: utf-8 -*-
"""直接测试Worker启动"""
import sys
import os

# Windows编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

sys.path.insert(0, 'openclaw_async_architecture/mvp')

# 导入Worker模块
print("导入模块...")
from src.worker.enhanced_worker import EnhancedWorker

print("\n创建Worker实例...")
try:
    worker = EnhancedWorker()
    print("[OK] Worker创建成功")
except Exception as e:
    print(f"[X] Worker创建失败: {e}")
    import traceback
    traceback.print_exc()

print("\n可用工具:")
tools = worker.list_tools()
for tool in tools:
    print(f"  - {tool['name']}: {tool['description']}")
