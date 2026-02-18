"""启动Gateway和Worker"""
import subprocess
import sys
import time
import os

# 编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 切换目录
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)

print("[1] 启动Gateway...")
gateway = subprocess.Popen([
    sys.executable, "-m", "uvicorn", "src.gateway.main:app",
    "--host", "127.0.0.1", "--port", "8000"
])

print("[2] 等待Gateway启动...")
time.sleep(3)

print("[3] 启动Worker...")
worker = subprocess.Popen([
    sys.executable, "src/worker/main.py"
])

print("[4] 等待Worker启动...")
time.sleep(5)

print("[完成] Gateway和Worker已启动")
print(f"  Gateway PID: {gateway.pid}")
print(f"  Worker PID: {worker.pid}")
print("\n按Ctrl+C停止...")
try:
    gateway.wait()
    worker.wait()
except KeyboardInterrupt:
    print("\n停止服务...")
    gateway.terminate()
    worker.terminate()
    gateway.wait()
    worker.wait()
    print("已停止")
