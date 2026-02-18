"""
V2 CLI系统 - Phase 5测试脚本

手动测试所有命令
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加v2_cli路径
v2_cli_dir = Path(__file__).parent / "v2_cli"
sys.path.insert(0, str(Path(__file__).parent / "v2_cli"))

os.chdir(str(Path(__file__).parent / "v2_cli"))

from cli import V2CLI


async def interactive_test():
    """交互式测试V2 CLI"""
    cli = V2CLI()

    # 欢迎信息
    print("=" * 60)
    print("V2 CLI系统 - 交互式测试")
    print("=" * 60)
    print()
    print("测试命令：")
    print("  1. help - 显示帮助")
    print("  2. status - 显示状态")
    print("  3. chat 你好 - 测试Gateway")
    print("  4. chat 用python写快速排序 - 测试流式输出")
    print("  5. history - 查看历史")
    print("  6. exit - 退出")
    print()
    print("可以直接输入命令，或者输入数字快速执行")
    print("=" * 60)
    print()

    # 模拟命令测试
    print("### 测试1：help命令 ###")
    cli.route_help("")
    input("按Enter继续...")

    print("\n### 测试2：status命令 ###")
    cli.route_status("")
    input("按Enter继续...")

    print("\n### 测试3：chat命令（你好）###")
    await cli.route_chat("你好")
    print()
    input("按Enter继续...")

    print("\n### 测试4：chat命令（Python快速排序）###")
    await cli.route_chat("用python写一个快速排序算法，带注释")
    print()
    input("按Enter继续...")

    print("\n### 测试5：history命令 ###")
    cli.route_history("")
    input("按Enter继续...")

    print("\n### 测试6：exit命令 ###")
    await cli.route_exit("")

    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(interactive_test())
