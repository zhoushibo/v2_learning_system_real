"""OpenClaw V2 MVP Launcher"""
import subprocess
import sys
import os

# Windows UTF-8编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


def start_gateway():
    """启动Gateway"""
    print("🚀 启动 Gateway (http://127.0.0.1:8000)")
    subprocess.run([sys.executable, "-m", "uvicorn", "src.gateway.main:app", "--host", "127.0.0.1", "--port", "8000"])


def start_worker():
    """启动Worker"""
    print("🔧 启动 Worker")
    subprocess.run([sys.executable, "-m", "src.worker.main"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw V2 MVP")
    parser.add_argument("command", choices=["gateway", "worker"], help="启动组件")

    args = parser.parse_args()

    if args.command == "gateway":
        start_gateway()
    elif args.command == "worker":
        start_worker()
