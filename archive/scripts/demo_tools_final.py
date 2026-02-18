"""演示V2 Worker工具系统使用（最终版）"""

import asyncio
import sys
import os
import json

# 添加项目路径
sys.path.insert(0, r'C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\mvp')

from src.worker.enhanced_worker import get_enhanced_worker
from src.common.models import Task


async def demo():
    """演示工具系统使用"""

    print("="*60)
    print("V2 Worker工具系统使用演示")
    print("="*60)

    # 创建Worker
    worker = get_enhanced_worker()

    # 测试1：创建测试文件（单行文本）
    print("\n【演示1】写入测试文件:")
    task1 = Task(
        id="demo-001",
        content='TOOL:write_file|{"path":"demo_test.txt","content":"Hello V2 Worker工具系统！这是测试文件。"}'
    )
    result = await worker.execute_task(task1)
    print(f"  ✅ 状态: {result.status}")
    print(f"  文件大小: {result.metadata.get('size')} bytes")

    # 测试2：读取刚才创建的文件
    print("\n【演示2】读取文件:")
    task2 = Task(
        id="demo-002",
        content='TOOL:read_file|{"path":"demo_test.txt"}'
    )
    result = await worker.execute_task(task2)
    print(f"  ✅ 状态: {result.status}")
    if result.status == 'completed':
        file_content = json.loads(result.result)
        print(f"  内容: {file_content}")

    # 测试3：执行Python代码（简单计算）
    print("\n【演示3】执行Python代码（计算）:")
    task3 = Task(
        id="demo-003",
        content='TOOL:exec_python|{"code":"import math; print(math.pi)"}'
    )
    result = await worker.execute_task(task3)
    print(f"  ✅ 状态: {result.status}")
    if result.status == 'completed':
        output = json.loads(result.result)
        print(f"  π = {output['stdout'].strip()}")

    # 测试4：列出目录
    print("\n【演示4】列出目录:")
    task4 = Task(
        id="demo-004",
        content='TOOL:list_directory|{"path":".","recursive":false}'
    )
    result = await worker.execute_task(task4)
    print(f"  ✅ 状态: {result.status}")
    if result.status == 'completed':
        files = json.loads(result.result)
        print(f"  找到 {len(files)} 个项目（显示前8个）:")
        for f in files[:8]:
            icon = "📁" if f['type'] == 'directory' else "📄"
            print(f"    {icon} {f['name'][:20]:20s}")

    # 测试5：创建目录
    print("\n【演示5】创建目录:")
    task5 = Task(
        id="demo-005",
        content='TOOL:create_directory|{"path":"demo_dir/sub_dir","parents":true}'
    )
    result = await worker.execute_task(task5)
    print(f"  ✅ 状态: {result.status}")

    # 列出创建的目录
    if result.status == 'completed':
        task6 = Task(
            id="demo-006",
            content='TOOL:list_directory|{"path":"demo_dir"}'
        )
        result6 = await worker.execute_task(task6)
        if result6.status == 'completed':
            files = json.loads(result6.result)
            content_list = ', '.join([f['name'] for f in files])
            print(f"  创建的内容: {content_list}")

    # 清理
    print("\n【清理】删除测试文件和目录:")
    import shutil
    try:
        if os.path.exists("demo_test.txt"):
            os.remove("demo_test.txt")
            print("  ✅ 已删除: demo_test.txt")
        if os.path.exists("demo_dir"):
            shutil.rmtree("demo_dir")
            print("  ✅ 已删除: demo_dir")
    except Exception as e:
        print(f"  ⚠️ 清理失败: {e}")

    # 关闭Worker
    await worker.close()

    print("\n" + "="*60)
    print("🎉 演示完成！V2 Worker工具系统工作正常！")
    print("="*60)
    print("\n工具调用格式：")
    print("  TOOL:工具名称|{\"参数\":\"值\"}")
    print("\n可用工具（6个）：")
    print("  - read_file: 读取文件")
    print("  - write_file: 写入文件")
    print("  - list_directory: 列出目录")
    print("  - create_directory: 创建目录")
    print("  - exec_command: 执行命令")
    print("  - exec_python: 执行Python代码")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(demo())
