"""立即可用的工具演示 - 用户体验提升"""
import asyncio
import sys
from pathlib import Path

# Windows编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def demo_exec_tool():
    """演示exec自主工具"""

    print("\n" + "="*70)
    print("🎯 工具2：exec自主工具 - 立即演示")
    print("="*70 + "\n")

    try:
        from openclaw_async_architecture.mvp.src.tools.exec_self import execute

        print("执行: python --version")
        print("-" * 70)

        exit_code, stdout, stderr = await execute(
            "python --version",
            timeout=5
        )

        if exit_code == 0:
            print(f"✅ 成功！\n{stdout}")
        else:
            print(f"❌ 失败: {stderr}")

    except ImportError as e:
        print(f"❌ 导入失败（路径问题）: {e}")
        print("\n💡 解决方案：直接在项目目录运行")

    print("\n" + "="*70)


def demo_gateway_guide():
    """演示Gateway流式对话指南"""

    print("\n" + "="*70)
    print("🎯 工具1：Gateway流式对话 - 立即使用")
    print("="*70 + "\n")

    print("📌 在命令行运行以下命令：\n")
    print("cd C:\\Users\\10952\\.openclaw\\workspace\\openclaw_async_architecture\\streaming-service")
    print("python use_gateway.py --interactive\n")

    print("或者单次测试：\n")
    print("python use_gateway.py --message \"你好\" --provider hunyuan\n")

    print("特点：")
    print("  ✅ 流式输出 - 边生边出")
    print("  ✅ 首字661ms - 超快响应")
    print("  ✅ 交互模式 - 连续对话")
    print("  ✅ 多API支持 - hunyuan推荐 ⭐")

    print("\n" + "="*70)


async def main():
    """主演示"""

    print("\n" + "="*70)
    print("🚀 立即可用工具演示")
    print("="*70)

    # 工具1指南
    demo_gateway_guide()

    # 工具2演示
    await demo_exec_tool()

    print("\n" + "="*70)
    print("✅ 演示完成！")
    print("="*70 + "\n")

    print("立即开始使用：")
    print("  1. 打开命令行，运行Gateway交互对话")
    print("  2. 在Python代码中使用exec自主工具")
    print("  3. 感受效率和质量提升！")
    print("\n详细文档: openclaw_async_architecture/QUICK_START.md")
    print()


if __name__ == "__main__":
    asyncio.run(main())
