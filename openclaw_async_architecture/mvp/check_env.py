"""快速测试：检查MVP组件是否可以运行"""
import subprocess
import sys
import time


def test_redis():
    """测试Redis连接"""
    print("\n=== 1. 检查Redis ===")
    try:
        result = subprocess.run(
            ["redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if "PONG" in result.stdout:
            print("✅ Redis运行正常")
            return True
        else:
            print("❌ Redis未运行")
            print("💡 启动命令: redis-server")
            return False
    except Exception as e:
        print(f"❌ Redis未安装或未运行: {e}")
        print("💡 启动命令: redis-server")
        return False


def test_v1_gateway():
    """测试V1 Gateway"""
    print("\n=== 2. 检查V1 Gateway ===")
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "Listening:" in result.stdout or "Listening" in result.stdout:
            print("✅ V1 Gateway运行正常")
            return True
        else:
            print("❌ V1 Gateway未运行")
            print("💡 启动命令: openclaw gateway")
            return False
    except Exception as e:
        print(f"❌ V1 Gateway未运行: {e}")
        print("💡 启动命令: openclaw gateway")
        return False


def test_dependencies():
    """测试Python依赖"""
    print("\n=== 3. 检查Python依赖 ===")
    required = [
        "fastapi",
        "uvicorn",
        "httpx",
        "redis",
        "pydantic",
        "requests"
    ]

    all_installed = True
    for package in required:
        try:
            subprocess.run(
                [sys.executable, "-c", f"import {package}"],
                capture_output=True,
                check=True
            )
            print(f"✅ {package}")
        except Exception:
            print(f"❌ {package} 未安装")
            all_installed = False

    if not all_installed:
        print("\n💡 安装命令: pip install -r requirements.txt")

    return all_installed


def main():
    """运行所有检查"""
    print("="*50)
    print("OpenClaw V2 MVP 环境检查")
    print("="*50)

    # 检查依赖
    deps_ok = test_dependencies()

    # 检查Redis
    redis_ok = test_redis()

    # 检查V1 Gateway
    v1_ok = test_v1_gateway()

    print("\n" + "="*50)
    print("检查结果")
    print("="*50)

    all_ok = deps_ok and redis_ok and v1_ok

    if all_ok:
        print("✅ 所有检查通过！可以启动MVP")
        print("\n启动命令:")
        print("  启动Gateway: python launcher.py gateway")
        print("  启动Worker:  python launcher.py worker")
        print("  运行测试:    python tests/test_mvp.py")
    else:
        print("❌ 部分检查失败，请先解决问题")

    print("="*50)


if __name__ == "__main__":
    main()
