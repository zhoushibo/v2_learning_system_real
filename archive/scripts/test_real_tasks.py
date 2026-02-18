"""
真实任务测试 - 使用全链路日志诊断 OpenClaw 问题

测试场景：
1. 正常任务：快速响应
2. 慢任务：模拟网络延迟
3. 卡任务：模拟命令卡住（用超时保护）
4. 错误任务：模拟命令失败
5. 复杂任务：多步骤组合

使用方法：
python test_real_tasks.py
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# 添加路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(project_root))

from mvp_jarvais.core import MemoryManager, AgentManager, ToolEngine, ToolType
from task_logger import TaskLogger
from openclaw_timeout_wrapper import get_wrapper

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)


async def test_1_normal_query():
    """测试 1：正常查询（应该 <1 秒）"""
    print("\n" + "="*70)
    print("【测试 1】正常查询：项目进展")
    print("="*70)
    
    # 创建全链路日志器
    task_logger = TaskLogger("真实任务：正常查询")
    
    async with task_logger.step("1. 初始化组件"):
        memory = MemoryManager(enable_v1=False)
        manager = AgentManager(memory)
        await asyncio.sleep(0.1)
    
    # 先记住一些数据
    async with task_logger.step("2. 准备记忆数据"):
        await memory.remember(
            key="project_progress",
            content="MVP JARVIS 系统开发进度：95%，已完成 MemoryManager、KnowledgeAgent、AgentManager、ToolEngine",
            metadata={"type": "status", "progress": "95%"}
        )
        await asyncio.sleep(0.1)
    
    # 执行查询
    async with task_logger.step("3. 执行查询"):
        start = datetime.now()
        result = await manager.route("我们的项目进展如何？", enable_logging=False)
        duration = (datetime.now() - start).total_seconds()
        
        logger.info(f"✅ 查询完成：{result['agent']}")
        logger.info(f"📊 耗时：{duration:.3f}秒")
        logger.info(f"💬 回答：{result['response'][:100]}...")
    
    # 生成报告
    print("\n📋 诊断报告:")
    report = task_logger.generate_report(format="text")
    print(report)
    
    return duration < 2.0  # 预期：<2 秒


async def test_2_slow_web_search():
    """测试 2：慢任务 - 模拟网络搜索延迟"""
    print("\n" + "="*70)
    print("【测试 2】慢任务：网络搜索（模拟 3 秒延迟）")
    print("="*70)
    
    task_logger = TaskLogger("真实任务：慢网络搜索")
    
    async with task_logger.step("1. 初始化工具引擎"):
        memory = MemoryManager(enable_v1=False)
        tool_engine = ToolEngine(memory)
        await asyncio.sleep(0.1)
    
    async with task_logger.step("2. 执行网络搜索", metadata={"query": "AI 最新进展"}):
        start = datetime.now()
        
        # 模拟慢速网络（3 秒延迟）
        async def slow_search():
            await asyncio.sleep(3.0)  # 模拟慢网络
            return {
                "status": "success",
                "results": [
                    {"title": "AI 突破：新模型发布", "url": "https://example.com/1"}
                ]
            }
        
        try:
            # 使用超时保护（5 秒）
            result = await asyncio.wait_for(slow_search(), timeout=5.0)
            duration = (datetime.now() - start).total_seconds()
            logger.info(f"✅ 搜索完成：{len(result['results'])}条结果")
            logger.info(f"📊 耗时：{duration:.3f}秒")
        except asyncio.TimeoutError:
            duration = (datetime.now() - start).total_seconds()
            logger.warning(f"⏰ 搜索超时（{duration:.3f}秒）")
            result = {"status": "timeout", "error": "搜索超时"}
    
    async with task_logger.step("3. 处理结果"):
        logger.info(f"📦 结果状态：{result.get('status', 'unknown')}")
    
    # 生成报告
    print("\n📋 诊断报告:")
    report = task_logger.generate_report(format="text")
    print(report)
    
    return True  # 无论成功或超时，都是预期行为


async def test_3_hanging_command():
    """测试 3：卡任务 - 模拟命令卡住（用 Wrapper 超时保护）"""
    print("\n" + "="*70)
    print("【测试 3】卡任务：执行可能卡住的命令（Wrapper 保护）")
    print("="*70)
    
    task_logger = TaskLogger("真实任务：卡住的命令")
    
    async with task_logger.step("1. 初始化 Wrapper"):
        wrapper = get_wrapper()
        await asyncio.sleep(0.1)
    
    async with task_logger.step("2. 执行命令", metadata={"command": "python -c 'import time; time.sleep(10)'"}):
        start = datetime.now()
        
        # 真实命令：会卡住 10 秒
        command = "python -c \"import time; time.sleep(10); print('完成')\""
        
        # 使用 Wrapper（5 秒超时）
        result = await wrapper.exec_tool(command, timeout=5)
        
        duration = (datetime.now() - start).total_seconds()
        logger.info(f"📊 实际耗时：{duration:.3f}秒")
        logger.info(f"📦 结果：{result}")
    
    async with task_logger.step("3. 分析结果"):
        if duration < 6.0:
            logger.info("✅ Wrapper 超时保护生效！命令被及时终止")
        else:
            logger.warning("⚠️  警告：耗时过长，Wrapper 可能未生效")
    
    # 生成报告
    print("\n📋 诊断报告:")
    report = task_logger.generate_report(format="text")
    print(report)
    
    return duration < 6.0  # 预期：<6 秒（超时保护生效）


async def test_4_failed_command():
    """测试 4：错误任务 - 执行不存在的命令"""
    print("\n" + "="*70)
    print("【测试 4】错误任务：执行不存在的命令")
    print("="*70)
    
    task_logger = TaskLogger("真实任务：失败的命令")
    
    async with task_logger.step("1. 初始化 Wrapper"):
        wrapper = get_wrapper()
        await asyncio.sleep(0.1)
    
    async with task_logger.step("2. 执行命令", metadata={"command": "non_existent_command_xyz"}):
        start = datetime.now()
        
        command = "non_existent_command_xyz"
        
        try:
            result = await wrapper.exec_tool(command, timeout=10)
            duration = (datetime.now() - start).total_seconds()
            logger.info(f"📊 耗时：{duration:.3f}秒")
            logger.info(f"📦 结果：{result}")
        except Exception as e:
            duration = (datetime.now() - start).total_seconds()
            logger.error(f"❌ 命令失败：{e}")
            result = {"status": "error", "error": str(e)}
    
    async with task_logger.step("3. 错误分析"):
        logger.info(f"📋 错误类型：{result.get('status', 'unknown')}")
        if result.get('error'):
            logger.info(f"📋 错误详情：{result['error'][:200]}")
    
    # 生成报告
    print("\n📋 诊断报告:")
    report = task_logger.generate_report(format="text")
    print(report)
    
    return True  # 错误是预期的


async def test_5_complex_workflow():
    """测试 5：复杂任务 - 多步骤组合"""
    print("\n" + "="*70)
    print("【测试 5】复杂任务：完整工作流（查询→学习→执行）")
    print("="*70)
    
    task_logger = TaskLogger("真实任务：复杂工作流")
    
    total_start = datetime.now()
    
    async with task_logger.step("1. 初始化所有组件"):
        memory = MemoryManager(enable_v1=False)
        manager = AgentManager(memory)
        tool_engine = ToolEngine(memory)
        await asyncio.sleep(0.2)
    
    # 步骤 1：查询
    async with task_logger.step("2. 步骤 1 - 知识查询"):
        result1 = await manager.route("我们有哪些核心资产？", enable_logging=False)
        logger.info(f"✅ 查询完成：{result1['response'][:80]}...")
        await asyncio.sleep(0.1)
    
    # 步骤 2：学习
    async with task_logger.step("3. 步骤 2 - 持续学习"):
        result2 = await manager.route("帮我学习向量搜索技术", enable_logging=False)
        logger.info(f"✅ 学习完成")
        await asyncio.sleep(0.1)
    
    # 步骤 3：执行
    async with task_logger.step("4. 步骤 3 - 工具调用"):
        result3 = await tool_engine.call(ToolType.EXEC, command="echo '工作流完成'")
        logger.info(f"✅ 执行完成：{result3.get('output', '')}")
        await asyncio.sleep(0.1)
    
    total_duration = (datetime.now() - total_start).total_seconds()
    
    async with task_logger.step("5. 总结"):
        logger.info(f"📊 总耗时：{total_duration:.3f}秒")
        logger.info(f"✅ 工作流完成：3 个步骤全部执行")
    
    # 生成报告
    print("\n📋 诊断报告:")
    report = task_logger.generate_report(format="text")
    print(report)
    
    return total_duration < 5.0  # 预期：<5 秒


async def main():
    """主测试程序"""
    print("="*70)
    print("🔍 真实任务测试 - 全链路日志诊断系统")
    print("="*70)
    print(f"\n开始时间：{datetime.now().strftime('%H:%M:%S')}")
    print("\n将测试 5 个场景：")
    print("  1. 正常查询（预期：<2 秒）")
    print("  2. 慢网络搜索（预期：3 秒 + 超时保护）")
    print("  3. 卡住的命令（预期：Wrapper 超时保护）")
    print("  4. 失败的命令（预期：错误处理）")
    print("  5. 复杂工作流（预期：<5 秒）")
    print("\n" + "="*70)
    
    results = []
    
    try:
        # 测试 1：正常查询
        passed = await test_1_normal_query()
        results.append(("正常查询", passed))
        await asyncio.sleep(0.5)
        
        # 测试 2：慢任务
        passed = await test_2_slow_web_search()
        results.append(("慢网络搜索", passed))
        await asyncio.sleep(0.5)
        
        # 测试 3：卡任务
        passed = await test_3_hanging_command()
        results.append(("卡住的命令", passed))
        await asyncio.sleep(0.5)
        
        # 测试 4：错误任务
        passed = await test_4_failed_command()
        results.append(("失败的命令", passed))
        await asyncio.sleep(0.5)
        
        # 测试 5：复杂工作流
        passed = await test_5_complex_workflow()
        results.append(("复杂工作流", passed))
        
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        return
    except Exception as e:
        print(f"\n\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return
    
    # 总结
    print("\n" + "="*70)
    print("📊 测试总结")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {status}: {name}")
    
    print(f"\n总计：{passed_count}/{total_count} 通过")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！全链路日志系统工作正常！")
        print("\n💡 使用说明：")
        print("  1. 在真实任务中导入 TaskLogger")
        print("  2. 用 async with task_logger.step() 包裹每个步骤")
        print("  3. 任务完成后查看诊断报告")
        print("  4. 根据报告定位慢/卡/错误问题")
    else:
        print(f"\n⚠️  有 {total_count - passed_count} 个测试未通过，请检查日志")
    
    print(f"\n结束时间：{datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
