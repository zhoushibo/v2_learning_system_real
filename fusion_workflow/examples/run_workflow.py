"""
Fusion Workflow示例 - 演示如何使用融合工作流引擎

这个示例展示了如何：
1. 创建工作流
2. 添加学习步骤
3. 添加执行步骤
4. 执行工作流
5. 获取结果
"""

import asyncio
import sys
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from workflow import WorkflowEngine, create_sequential_workflow
from integrations import LearningIntegration, ExecutorIntegration


async def example_1_simple_learning():
    """示例1：简单的学习工作流"""
    print("\n" + "="*60)
    print("示例1：简单的学习工作流")
    print("="*60)

    # 创建工作流
    workflow = create_sequential_workflow(
        name="Simple Learning Workflow",
        description="演示如何创建并执行一个简单的学习工作流"
    )

    # 创建学习集成
    learning_integration = LearningIntegration()

    # 添加学习步骤
    workflow.add_step(
        learning_integration.create_learning_step(
            topic="OpenClaw架构深度学习",
            timeout=300
        )
    )

    # 创建工作流引擎
    engine = WorkflowEngine(fallback_to_mock=True)

    # 执行工作流
    results = await engine.execute(workflow)

    # 输出结果
    print("\n" + "-"*60)
    print("工作流执行结果：")
    print("-"*60)

    for step_name, result in results.items():
        print(f"\n步骤: {step_name}")
        print(f"  状态: {result.status.value}")
        print(f"  耗时: {result.duration:.2f}s")
        if result.output:
            print(f"  输出: {result.output}")


async def example_2_learning_and_execution():
    """示例2：学习 + 执行工作流"""
    print("\n" + "="*60)
    print("示例2：学习 + 执行工作流")
    print("="*60)

    # 创建工作流
    workflow = create_sequential_workflow(
        name="Learning and Execution Workflow",
        description="演示学习后执行命令的工作流"
    )

    # 创建集成
    learning_integration = LearningIntegration(use_mock=True)  # 使用模拟结果
    executor_integration = ExecutorIntegration(use_mock=True)  # 使用模拟执行

    # 添加学习步骤
    workflow.add_step(
        learning_integration.create_learning_step(
            topic="如何高效使用Python开发工具",
            timeout=120
        )
    )

    # 添加执行步骤
    workflow.add_step(
        executor_integration.create_execution_step(
            command="echo 'Hello from Fusion Workflow!'",
            timeout=10
        ),
        after="learning_如何高效使用Python开发工具"
    )

    # 创建工作流引擎
    engine = WorkflowEngine(fallback_to_mock=True)

    # 执行工作流
    results = await engine.execute(workflow)

    # 输出结果
    print("\n" + "-"*60)
    print("工作流执行结果：")
    print("-"*60)

    for step_name, result in results.items():
        print(f"\n步骤: {step_name}")
        print(f"  状态: {result.status.value}")
        print(f"  耗时: {result.duration:.2f}s")
        if result.output:
            if isinstance(result.output, dict) and 'output' in result.output:
                print(f"  输出: {result.output['output'][:100]}...")
            else:
                print(f"  输出: {result.output}")


async def example_3_real_workflow():
    """示例3：真正的学习 + 执行工作流（使用真实V2系统）"""
    print("\n" + "="*60)
    print("示例3：真正的学习 + 执行工作流")
    print("="*60)

    # 创建工作流
    workflow = create_sequential_workflow(
        name="Real Learning and Execution Workflow",
        description="使用真实的V2学习系统和执行系统"
    )

    # 创建集成（不使用模拟）
    learning_integration = LearningIntegration(use_mock=False)
    executor_integration = ExecutorIntegration(use_mock=False)

    # 添加学习步骤
    workflow.add_step(
        learning_integration.create_learning_step(
            topic="Python异步编程最佳实践",
            timeout=300
        )
    )

    # 添加执行步骤
    workflow.add_step(
        executor_integration.create_execution_step(
            command="python --version",
            timeout=5
        ),
        after="learning_Python异步编程最佳实践"
    )

    # 创建工作流引擎
    engine = WorkflowEngine(fallback_to_mock=True)

    # 执行工作流
    results = await engine.execute(workflow)

    # 输出结果
    print("\n" + "-"*60)
    print("工作流执行结果：")
    print("-"*60)

    for step_name, result in results.items():
        print(f"\n步骤: {step_name}")
        print(f"  状态: {result.status.value}")
        print(f"  耗时: {result.duration:.2f}s")
        if result.output:
            if isinstance(result.output, dict) and 'output' in result.output:
                print(f"  输出: {result.output['output'][:200]}...")
            else:
                print(f"  输出: {result.output}")


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("Fusion Workflow 示例演示")
    print("="*60)

    try:
        # 示例1：简单的学习工作流
        await example_1_simple_learning()

        # 示例2：学习 + 执行工作流（模拟）
        await example_2_learning_and_execution()

        # 示例3：真正的学习 + 执行工作流
        # await example_3_real_workflow()  # 取消注释以运行真实工作流

        print("\n" + "="*60)
        print("所有示例执行完成！")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
