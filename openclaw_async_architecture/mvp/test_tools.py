"""测试V2 Worker工具系统（修复版）

测试所有工具：
1. 文件系统工具（4个）
2. 命令执行工具（1个）
3. 代码执行工具（1个）
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.worker.enhanced_worker import get_enhanced_worker


async def test_all_tools():
    """测试所有工具"""

    print("="*60)
    print("V2 Worker工具系统测试")
    print("="*60)

    # 创建Worker
    worker = get_enhanced_worker()

    # 列出工具
    tools = worker.list_tools()
    print(f"\n✅ 已注册工具（{len(tools)}个）:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")

    print("\n" + "="*60)
    print("开始测试...")
    print("="*60)

    # 测试计数
    total_tests = 7
    passed_tests = 0

    # ========== 测试1：创建目录 ==========
    print("\n【测试1】创建目录...")
    try:
        import json
        from src.common.models import Task
        task1 = Task(
            id="test-001",
            content=f"TOOL:create_directory|{json.dumps({'path': 'test_dir'})}"
        )
        result = await worker.execute_task(task1)
        if result.status == "completed":
            print("✅ 测试1通过")
            passed_tests += 1
        else:
            print(f"❌ 测试1失败: {result.error}")
    except Exception as e:
        print(f"❌ 测试1异常: {e}")
        import traceback
        traceback.print_exc()

    # ========== 测试2：写入文件 ==========
    print("\n【测试2】写入文件...")
    try:
        from src.common.models import Task
        task2 = Task(
            id="test-002",
            content=f"TOOL:write_file|{json.dumps({'path': 'test_dir/test.txt', 'content': 'Hello from V2 Worker!\n这是一行测试文字。'})}"
        )
        result = await worker.execute_task(task2)
        if result.status == "completed":
            print("✅ 测试2通过")
            print(f"   文件大小: {result.metadata.get('size')} bytes")
            passed_tests += 1
        else:
            print(f"❌ 测试2失败: {result.error}")
    except Exception as e:
        print(f"❌ 测试2异常: {e}")
        import traceback
        traceback.print_exc()

    # ========== 测试3：读取文件 ==========
    print("\n【测试3】读取文件...")
    try:
        from src.common.models import Task
        task3 = Task(
            id="test-003",
            content=f"TOOL:read_file|{json.dumps({'path': 'test_dir/test.txt'})}"
        )
        result = await worker.execute_task(task3)
        if result.status == "completed":
            print("✅ 测试3通过")
            print(f"   内容: {result.result[:50]}...")
            passed_tests += 1
        else:
            print(f"❌ 测试3失败: {result.error}")
    except Exception as e:
        print(f"❌ 测试3异常: {e}")
        import traceback
        traceback.print_exc()

    # ========== 测试4：列出目录 ==========
    print("\n【测试4】列出目录...")
    try:
        from src.common.models import Task
        task4 = Task(
            id="test-004",
            content=f"TOOL:list_directory|{json.dumps({'path': 'test_dir'})}"
        )
        result = await worker.execute_task(task4)
        if result.status == "completed":
            print("✅ 测试4通过")
            # result.data已经是JSON字符串，不需要再次解析
            files = json.loads(result.result)
            for f in files:
                print(f"   - {f['name']} ({f['type']})")
            passed_tests += 1
        else:
            print(f"❌ 测试4失败: {result.error}")
    except Exception as e:
        print(f"❌ 测试4异常: {e}")
        import traceback
        traceback.print_exc()

    # ========== 测试5：执行Python代码 ==========
    print("\n【测试5】执行Python代码...")
    try:
        from src.common.models import Task
        # 使用简单的单行代码
        task5 = Task(
            id="test-005",
            content="TOOL:exec_python|{\"code\": \"print('Hello from Python!')\"}"
        )
        result = await worker.execute_task(task5)
        if result.status == "completed":
            print("✅ 测试5通过")
            # result.data已经是JSON字符串
            output = json.loads(result.result)
            print(f"   输出: {output['stdout'].strip()}")
            passed_tests += 1
        else:
            print(f"❌ 测试5失败: {result.error}")
            print(f"   结果: {result.result}")
    except Exception as e:
        print(f"❌ 测试5异常: {e}")
        import traceback
        traceback.print_exc()

    # ========== 测试6：执行命令（限制） ==========
    print("\n【测试6】执行命令（echo）...")
    try:
        from src.common.models import Task
        task6 = Task(
            id="test-006",
            content="TOOL:exec_command|{\"command\": \"echo Hello from Command!\"}"
        )
        result = await worker.execute_task(task6)
        if result.status == "completed":
            print("✅ 测试6通过")
            # result.data已经是JSON字符串
            output = json.loads(result.result)
            print(f"   输出: {output['stdout'].strip()}")
            passed_tests += 1
        else:
            print(f"❌ 测试6失败: {result.error}")
    except Exception as e:
        print(f"❌ 测试6异常: {e}")
        import traceback
        traceback.print_exc()

    # ========== 测试7：禁用命令（安全检查） ==========
    print("\n【测试7】禁用命令（安全检查）...")
    try:
        from src.common.models import Task
        task7 = Task(
            id="test-007",
            content="TOOL:exec_command|{\"command\": \"rm -rf test_dir\"}"
        )
        result = await worker.execute_task(task7)
        if result.status == "failed":
            print("✅ 测试7通过（正确拒绝危险命令）")
            print(f"   错误: {result.error}")
            passed_tests += 1
        else:
            print("❌ 测试7失败（应该拒绝危险命令）")
    except Exception as e:
        print(f"❌ 测试7异常: {e}")
        import traceback
        traceback.print_exc()

    # ========== 测试结果 ==========
    print("\n" + "="*60)
    print("测试结果")
    print("="*60)
    print(f"通过: {passed_tests}/{total_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")

    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！工具系统正常工作！")
    else:
        print(f"\n⚠️ 有 {total_tests - passed_tests} 个测试失败")

    # 关闭Worker
    await worker.close()

    print("\n测试完成")

    # 删除测试目录（可选）
    print("\n清理测试文件...")
    import shutil
    try:
        if os.path.exists("test_dir"):
            shutil.rmtree("test_dir")
            print("✅ 测试目录已清理")
    except Exception as e:
        print(f"⚠️ 清理失败: {e}")


if __name__ == "__main__":
    asyncio.run(test_all_tools())
