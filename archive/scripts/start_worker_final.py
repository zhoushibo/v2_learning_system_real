"""启动Worker并输出完整日志"""

# 修复编码
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 切换目录
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)
sys.path.insert(0, mvp_dir)

# 导入并启动
from src.worker.main import run_worker
import asyncio

try:
    asyncio.run(run_worker())
except KeyboardInterrupt:
    print("\nWorker已停止")
