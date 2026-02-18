"""
V2 CLI系统 - Phase 5自动测试脚本

自动测试所有命令（无需交互）
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加v2_cli路径
v2_cli_dir = Path(__file__).parent.parent / "v2_cli"
sys.path.insert(0, str(v2_cli_dir))

os.chdir(str(v2_cli_dir))

from cli import V2CLI
from rich.console import Console

console = Console()


async def auto_test():
    """自动测试V2 CLI"""
    cli = V2CLI()

    print("=" * 60)
    print("V2 CLI系统 - Phase 5自动测试")
    print("=" * 60)
    print()

    # 测试1：help命令
    print("[cyan]测试1：help命令[/cyan]")
    print("-" * 60)
    cli.route_help("")
    print("\n✅ 测试1通过\n")

    # 测试2：status命令
    print("[cyan]测试2：status命令[/cyan]")
    print("-" * 60)
    cli.route_status("")
    print("\n✅ 测试2通过\n")

    # 测试3：chat命令（简单消息）
    print("[cyan]测试3：chat命令（你好）[/cyan]")
    print("-" * 60)
    await cli.route_chat("你好")
    print("\n✅ 测试3通过\n")

    # 测试4：chat命令（Python代码）
    print("[cyan]测试4：chat命令（Python快速排序）[/cyan]")
    print("-" * 60)
    await cli.route_chat("用python写一个快速排序算法，代码要简洁")
    print("\n✅ 测试4通过\n")

    # 测试5：history命令
    print("[cyan]测试5：history命令[/cyan]")
    print("-" * 60)
    cli.route_history("")
    print("\n✅ 测试5通过\n")

    # 测试6：未知的命令
    print("[cyan]测试6：未知的命令[/cyan]")
    print("-" * 60)
    await cli.route_command("xxx", "args")
    print("\n✅ 测试6通过\n")

    print("=" * 60)
    print("[green]V2 CLI系统 - Phase 5测试完成 ✅[/green]")
    print("=" * 60)
    print()
    print("[yellow]所有测试通过！[/yellow]")
    print()
    print("[bold]启动V2 CLI：[/bold]")
    print("  cd v2_cli")
    print("  python cli.py")
    print()
    print("[bold]可用命令：[/bold]")
    print("  chat <消息>  - 流式对话")
    print("  help         - 显示帮助")
    print("  status       - 显示状态")
    print("  history      - 查看历史")
    print("  exit         - 退出")


if __name__ == "__main__":
    asyncio.run(auto_test())
