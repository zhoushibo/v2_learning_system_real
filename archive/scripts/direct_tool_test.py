"""直接测试EnhancedWorker工具调用（不通过Gateway）"""

import asyncio
import sys
import os
import json

# 添加项目路径
sys.path.insert(0, r'C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\mvp')

from src.worker.enhanced_worker import get_enhanced_worker
from src.common.models import Task


async def test_direct():
    """直接测试Worker工具调用"""

    print("="*60)
    print("直接测试V2 Worker工具系统")
    print("="*60)

    # 创建Worker
    worker = get_enhanced_worker()

    # 测试1：列出工具
    print("\n【1】列出所有工具:")
    tools = worker.list_tools()
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")

    # 测试2：读取文件
    print("\n【2】读取文件:")
    import json
    task2 = Task(
        id="test-001",
        content='TOOL:read_file|{"path":"novel.md"}'
    )
    result = await worker.execute_task(task2)
    print(f"  状态: {result.status}")
    if result.status == 'completed':
        file_content = json.loads(result.result)
        print(f"  长度: {len(file_content)} 字符")
        print(f"  预览: {file_content[:80]}...")

    # 测试3：执行Python代码
    print("\n【3】执行Python代码:")
    task3 = Task(
        id="test-002",
        content='TOOL:exec_python|{"code":"for i in range(3):\\n    print(f\'Hello {i}\')"}'
    )
    result = await worker.execute_task(task3)
    print(f"  状态: {result.status}")
    if result.status == 'completed':
        output = json.loads(result.result)
        print(f"  输出:\n{output['stdout']}")

    # 测试4：写入文件
    print("\n【4】写入文件:")
    task4 = Task(
        id="test-003",
        content='TOOL:write_file|{"path":"test_output.txt","content":"Hello from V2 Worker Tool System!"}'
    )
    result = await worker.execute_task(task4)
    print(f"  状态: {result.status}")
    if result.status == 'completed':
        print(f"  文件大小: {result.metadata.get('size')} bytes")

    # 测试5：列出目录
    print("\n【5】列出目录:")
    task5 = Task(
        id="test-004",
        content='TOOL:list_directory|{"path":"openclaw_async_architecture/mvp/src"}'
    )
    result = await worker.execute_task(task5)
    print(f"  状态: {result.status}")
    if result.status == 'completed':
        files = json.loads(result.result)
        print(f"  找到 {len(files)} 个项目:")
        for f in files[:5]:
            print(f"    - {f['name']} ({f['type']})")

    # 清理测试文件
    import os
    test_file = r'C:\Users\10952\.openclaw\workspace\test_output.txt'
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\n  ✅ 已清理测试文件: test_output.txt")

    # 关闭Worker
    await worker.close()

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_direct())
