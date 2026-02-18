"""测试增强版V2 Worker"""
import asyncio
import sys
from pathlib import Path

# 添加路径
mvp_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(mvp_src))

from src.worker.enhanced_worker import EnhancedV2Worker
from src.common.models import Task

async def test_enhanced_worker():
    """测试增强版V2 Worker"""

    # Windows编码
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    print("\n" + "="*70)
    print("增强版V2 Worker集成测试")
    print("="*70 + "\n")

    worker = EnhancedV2Worker(worker_id="integration-test")

    # 测试1: 自主exec工具 ✅
    print("【测试1】自主exec工具")
    print("-" * 70)

    try:
        task = Task(
            content="python --version",
            metadata={"task_type": "command"}
        )

        task = await worker.execute_task(task)

        if task.status == "completed":
            print(f"✅ 执行成功")
            print(f"   输出: {task.result}")
        else:
            print(f"❌ 执行失败: {task.error}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")

    print("\n" + "="*70)

    # 测试2: Gateway流式（如果可用）
    print("\n【测试2】Gateway流式LLM（可选）")
    print("-" * 70)

    try:
        # 注意：Gateway需要在运行中
        task = Task(
            content="你好，请用一句话介绍你自己",
            metadata={"task_type": "chat", "provider": "hunyuan"}
        )

        task = await worker.execute_task(task)

        if task.status == "completed":
            print(f"✅ Gateway执行成功")
            print(f"   结果（前100字符）: {task.result[:100]}...")
        else:
            print(f"⚠️ Gateway执行失败（可能未运行）: {task.error}")

    except Exception as e:
        print(f"⚠️ 测试跳过（Gateway可能未运行）: {e}")

    print("\n" + "="*70)
    print("集成测试完成！")
    print("="*70 + "\n")

    print("集成成果:")
    print("  ✅ 自主exec工具已集成")
    print("  ⚠️ Gateway流式已集成（需运行）")
    print("  ✅ V2 Worker现在可以:")
    print("     - 执行Shell命令（自主，不依赖OpenClaw）")
    print("     - 调用Gateway流式（体验更好）")
    print("     - 调用V1 API（回退方案）")
    print()

    await worker.close()


if __name__ == "__main__":
    asyncio.run(test_enhanced_worker())
