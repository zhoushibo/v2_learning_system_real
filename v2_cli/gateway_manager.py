"""
V2 CLI - Gateway自动启动功能

自动检测并启动Gateway服务
"""
import asyncio
import subprocess
import sys
from pathlib import Path


def check_gateway_running():
    """检查Gateway服务是否在运行"""
    try:
        import requests
        # 健康检查端点
        response = requests.get("http://127.0.0.1:8001/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_gateway():
    """启动Gateway服务"""
    gateway_dir = Path(__file__).parent.parent / "openclaw_async_architecture" / "streaming-service"
    launcher = gateway_dir / "launcher.py"

    if not launcher.exists():
        print(f"[yellow]Gateway启动脚本不存在：{launcher}[/yellow]")
        return None

    # 后台启动Gateway
    process = subprocess.Popen(
        [sys.executable, str(launcher)],
        cwd=str(gateway_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )

    return process


async def ensure_gateway():
    """确保Gateway服务在运行"""
    from rich.console import Console
    console = Console()

    # 检查Gateway是否在运行
    if check_gateway_running():
        console.print("[green]Gateway服务已在运行 ✅[/green]")
        return True

    # 启动Gateway
    console.print("[yellow]Gateway服务未运行，正在自动启动...[/yellow]")

    process = start_gateway()

    if process is None:
        console.print("[red]Gateway启动失败[/red]")
        return False

    # 等待Gateway启动
    console.print("[cyan]等待Gateway启动...[/cyan]")

    for i in range(20):  # 最多等待20秒
        await asyncio.sleep(1)
        if check_gateway_running():
            console.print(f"[green]Gateway启动成功 ✅ (耗时 {i+1}秒)[/green]")
            return True

    console.print("[red]Gateway启动超时[/red]")
    return False


if __name__ == "__main__":
    asyncio.run(ensure_gateway())
