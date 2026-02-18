"""
Fusion Workflow 测试
"""

import asyncio
import sys
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from workflow import WorkflowEngine, Step, create_sequential_workflow, StepStatus


async def test_workflow_engine():
    """测试工作流引擎"""
    print("\n" + "="*60)
    print("测试：工作流引擎基础功能")
    print("="*60)

    # 创建工作流
    workflow = create_sequential_workflow(
        name="Test Workflow",
        description="测试工作流引擎"
    )

    # 添加测试步骤
    async def step1(context):
        print("执行步骤1...")
        await asyncio.sleep(0.5)
        return "步骤1完成"

    async def step2(context):
        print("执行步骤2...")
        await asyncio.sleep(0.3)
        return "步骤2完成"

    async def step3(context):
        print("执行步骤3...")
        await asyncio.sleep(0.2)
        return "步骤3完成"

    workflow.add_step(Step(name="step1", function=step1))
    workflow.add_step(Step(name="step2", function=step2))
    workflow.add_step(Step(name="step3", function=step3))

    # 创建引擎
    engine = WorkflowEngine(fallback_to_mock=True)

    # 执行工作流
    results = await engine.execute(workflow)

    # 验证结果
    assert len(results) == 3, "应该有3个步骤结果"
    assert all(r.status == StepStatus.SUCCESS for r in results.values()), "所有步骤应该成功"

    print("\n✅ 测试通过！")
    print("\n步骤结果：")
    for name, result in results.items():
        print(f"  {name}: {result.status.value}, 输出: {result.output}")


async def test_timeout_with_fallback():
    """测试超时和Fallback机制"""
    print("\n" + "="*60)
    print("测试：超时和Fallback机制")
    print("="*60)

    # 创建工作流
    workflow = create_sequential_workflow(
        name="Timeout Test Workflow",
        description="测试超时和Fallback"
    )

    # 添加会超时的步骤
    async def slow_step(context):
        print("执行慢步骤（会超时）...")
        await asyncio.sleep(5)  # 超过超时时间
        return "不应该到达这里"

    workflow.add_step(Step(name="slow_step", function=slow_step, timeout=1))

    # 添加正常步骤
    async def normal_step(context):
        print("执行正常步骤...")
        await asyncio.sleep(0.1)
        return "正常步骤完成"

    workflow.add_step(Step(name="normal_step", function=normal_step, timeout=5))

    # 创建引擎（启用Fallback）
    engine = WorkflowEngine(fallback_to_mock=True)

    # 执行工作流
    results = await engine.execute(workflow)

    # 验证结果
    # slow_step应该超时但使用Fallback（转为SUCCESS）
    # normal_step应该正常执行
    assert 'slow_step' in results, "应该有slow_step的结果"
    assert 'normal_step' in results, "应该有normal_step的结果"
    assert results['slow_step'].status == StepStatus.SUCCESS, "slow_step应该使用Fallback转为成功"

    print("\n✅ 测试通过！")
    print("\n步骤结果：")
    for name, result in results.items():
        print(f"  {name}: {result.status.value}, Mock={result.output.get('mock', False) if isinstance(result.output, dict) else 'N/A'}")


async def test_learning_integration():
    """测试学习系统集成"""
    print("\n" + "="*60)
    print("测试：学习系统集成")
    print("="*60)

    from integrations import LearningIntegration

    # 创建学习集成（使用模拟）
    learning_integration = LearningIntegration(use_mock=True)

    # 创建工作流
    workflow = create_sequential_workflow(
        name="Learning Integration Test",
        description="测试学习系统集成"
    )

    # 添加学习步骤
    workflow.add_step(
        learning_integration.create_learning_step(
            topic="测试主题：如何提高工作效率",
            timeout=120
        )
    )

    # 创建引擎
    engine = WorkflowEngine(fallback_to_mock=True)

    # 执行工作流
    results = await engine.execute(workflow)

    # 验证结果
    assert len(results) == 1, "应该有1个学习步骤"
    assert results['learning_测试主题：如何提高工作效率'].status == StepStatus.SUCCESS

    print("\n✅ 测试通过！")
    print("\n学习结果：")
    for name, result in results.items():
        if isinstance(result.output, dict):
            print(f"  主题: {result.output.get('topic')}")
            print(f"  课程数: {len(result.output.get('lessons', []))}")
            print(f"  关键点数: {len(result.output.get('key_points', []))}")
        print(f"  状态: {result.status.value}, 耗时: {result.duration:.2f}s")


async def test_executor_integration():
    """测试执行系统集成"""
    print("\n" + "="*60)
    print("测试：执行系统集成")
    print("="*60)

    from integrations import ExecutorIntegration

    # 创建执行集成（使用模拟）
    executor_integration = ExecutorIntegration(use_mock=True)

    # 创建工作流
    workflow = create_sequential_workflow(
        name="Executor Integration Test",
        description="测试执行系统集成"
    )

    # 添加执行步骤
    workflow.add_step(
        executor_integration.create_execution_step(
            command="echo test",
            timeout=10
        )
    )

    # 创建引擎
    engine = WorkflowEngine(fallback_to_mock=True)

    # 执行工作流
    results = await engine.execute(workflow)

    # 验证结果
    assert len(results) == 1, "应该有1个执行步骤"
    assert results['execute_echo_test'].status == StepStatus.SUCCESS

    print("\n✅ 测试通过！")
    print("\n执行结果：")
    for name, result in results.items():
        if isinstance(result.output, dict):
            print(f"  命令: {result.output.get('command')}")
            print(f"  输出: {result.output.get('output', '')[:100]}...")
        print(f"  状态: {result.status.value}, 耗时: {result.duration:.2f}s")


async def test_full_workflow():
    """测试完整工作流（学习 + 执行）"""
    print("\n" + "="*60)
    print("测试：完整工作流（学习 + 执行）")
    print("="*60)

    from integrations import LearningIntegration, ExecutorIntegration

    # 创建集成
    learning_integration = LearningIntegration(use_mock=True)
    executor_integration = ExecutorIntegration(use_mock=True)

    # 创建工作流
    workflow = create_sequential_workflow(
        name="Full Workflow Test",
        description="测试学习 + 执行的完整工作流"
    )

    # 添加学习步骤
    workflow.add_step(
        learning_integration.create_learning_step(
            topic="Python异步编程",
            timeout=120
        )
    )

    # 添加执行步骤
    workflow.add_step(
        executor_integration.create_execution_step(
            command="python --version",
            timeout=5
        )
    )

    # 创建引擎
    engine = WorkflowEngine(fallback_to_mock=True)

    # 执行工作流
    results = await engine.execute(workflow)

    # 验证结果
    assert len(results) == 2, "应该有2个步骤（学习 + 执行）"
    assert all(r.status == StepStatus.SUCCESS for r in results.values()), "所有步骤应该成功"

    print("\n✅ 测试通过！")
    print("\n完整工作流结果：")
    for name, result in results.items():
        print(f"  {name}: {result.status.value}, 耗时: {result.duration:.2f}s")


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Fusion Workflow 测试套件")
    print("="*60)

    tests = [
        ("工作流引擎基础功能", test_workflow_engine),
        ("超时和Fallback机制", test_timeout_with_fallback),
        ("学习系统集成", test_learning_integration),
        ("执行系统集成", test_executor_integration),
        ("完整工作流（学习+执行）", test_full_workflow),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ 测试失败：{test_name}")
            print(f"   错误: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"测试结果：{passed} 通过, {failed} 失败")
    print("="*60)

    if failed == 0:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  {failed} 个测试失败")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
