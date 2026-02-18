"""
V2 CLI系统 - 测试脚本

测试CLI的核心功能
"""
import asyncio
from cli import V2CLI


async def test_cli():
    """测试V2 CLI"""
    print("=" * 60)
    print("V2 CLI系统 - 测试")
    print("=" * 60)
    print()

    cli = V2CLI()

    # 测试1：help命令
    print("测试1：help命令")
    cli.route_help("")
    print()

    # 测试2：status命令
    print("测试2：status命令")
    cli.route_status("")
    print()

    # 测试3：chat命令（需要Gateway运行）
    print("测试3：chat命令")
    await cli.route_chat("你好")
    print()

    # 测试4：未知的命令
    print("测试4：未知的命令")
    await cli.route_command("xxx", "args")
    print()

    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_cli())
