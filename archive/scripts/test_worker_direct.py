"""直接使用Worker（不通过Gateway）"""

import asyncio
import sys
import os

# 添加完整路径
sys.path.insert(0, r'C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\mvp\src')

from worker.enhanced_worker import get_enhanced_worker
from common.models import Task


async def test_worker_directly():
    """直接测试Worker"""

    print("="*60)
    print("直接测试Worker（不通过Gateway）")
    print("="*60)

    worker = get_enhanced_worker()

    # 测试1：检查工作目录
    print("\n【测试1】检查工作目录")
    task1 = Task(
        id="direct-test-001",
        content='TOOL:exec_command|{"command":"echo %CD%"}'
    )

    result = await worker.execute_task(task1)

    print(f"状态: {result.status}")
    print(f"结果: {result.result}")

    await worker.close()

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_worker_directly())
