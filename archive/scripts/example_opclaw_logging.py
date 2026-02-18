"""
OpenClaw 全链路日志追踪示例

展示如何在真实 OpenClaw 任务中使用 TaskLogger：
1. 记录每个工具调用的耗时
2. 记录 Agent 路由耗时
3. 记录错误详情
4. 生成诊断报告

使用方法：
python example_opclaw_logging.py
"""

import asyncio
import logging
from task_logger import TaskLogger
from openclaw_timeout_wrapper import get_wrapper
from mvp_jarvais.core import MemoryManager, AgentManager, ToolEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)


async def simulate_opclaw_task():
    """
    模拟真实 OpenClaw 任务
    
    场景：用户问"我们的项目进展如何？"
    流程：
    1. 接收用户输入
    2. Agent 路由
    3. 记忆搜索
    4. 工具调用（可选）
    5. 生成回答
    """
    
    # 创建全链路日志器
    task_logger = TaskLogger("OpenClaw 任务：用户查询项目进展")
    
    async with task_logger.step("1. 接收用户输入", metadata={"input": "我们的项目进展如何？"}):
        user_input = "我们的项目进展如何？"
        await asyncio.sleep(0.1)  # 模拟接收延迟
    
    # 初始化组件
    async with task_logger.step("2. 初始化组件"):
        memory = MemoryManager(enable_v1=False)
        agent_manager = AgentManager(memory)
        tool_engine = ToolEngine(memory)
        await asyncio.sleep(0.3)
    
    # Agent 路由
    async with task_logger.step("3. Agent 路由"):
        try:
            result = await agent_manager.route(user_input)
            logger.info(f"路由结果：{result['type']} → {result['agent']}")
        except Exception as e:
            logger.error(f"路由失败：{e}")
            raise
    
    # 根据路由结果执行
    async with task_logger.step("4. 执行任务", metadata={"agent": result.get('agent', 'unknown')}):
        try:
            if result['type'] == 'knowledge_query':
                # 知识查询：搜索记忆
                async with task_logger.step("4.1 记忆搜索"):
                    search_results = await memory.search("项目进展", n_results=3)
                    logger.info(f"搜索到 {len(search_results)} 条记忆")
                
                async with task_logger.step("4.2 生成回答"):
                    if search_results:
                        answer = f"根据记忆，{search_results[0].get('content', '无内容')}"
                    else:
                        answer = "没有找到相关记忆"
                    await asyncio.sleep(0.2)
            
            elif result['type'] == 'task_execution':
                # 任务执行：调用工具
                async with task_logger.step("4.1 工具调用"):
                    tool_result = await tool_engine.call(
                        'exec',
                        command="echo '执行任务'"
                    )
                    logger.info(f"工具结果：{tool_result['status']}")
                
                answer = "任务执行完成"
            
            else:
                # 普通对话
                answer = result.get('response', '')
        
        except Exception as e:
            logger.error(f"执行失败：{e}")
            raise
    
    # 返回结果
    async with task_logger.step("5. 返回结果"):
        logger.info(f"回答：{answer[:100]}...")
        await asyncio.sleep(0.1)
    
    # 生成完整报告
    print("\n" + "="*70)
    print("📋 全链路诊断报告")
    print("="*70)
    
    report = task_logger.generate_report(format="text")
    print(report)
    
    # 也可以生成 JSON 报告用于分析
    json_report = task_logger.generate_report(format="json")
    print("\nJSON 报告已生成（可用于进一步分析）")
    
    return answer


async def simulate_slow_task():
    """
    模拟慢任务（用于诊断卡顿问题）
    
    场景：执行一个可能很慢的命令
    """
    
    task_logger = TaskLogger("OpenClaw 任务：执行慢命令")
    
    async with task_logger.step("1. 准备命令"):
        command = "python -c 'import time; time.sleep(5); print(\"完成\")'"
        logger.info(f"命令：{command}")
    
    async with task_logger.step("2. 执行命令"):
        wrapper = get_wrapper()
        
        try:
            # 使用 Wrapper（60 秒超时）
            result = await wrapper.exec_tool(command, timeout=60)
            logger.info(f"执行结果：{result}")
        except Exception as e:
            logger.error(f"执行失败：{e}")
            raise
    
    async with task_logger.step("3. 处理结果"):
        output = result.get('output', '') if isinstance(result, dict) else str(result)
        logger.info(f"输出：{output[:100]}...")
    
    # 生成报告
    print("\n" + "="*70)
    print("📋 慢任务诊断报告")
    print("="*70)
    
    report = task_logger.generate_report(format="markdown")
    print(report)


async def simulate_error_task():
    """
    模拟错误任务（用于诊断错误）
    
    场景：执行一个会失败的命令
    """
    
    task_logger = TaskLogger("OpenClaw 任务：执行错误命令")
    
    async with task_logger.step("1. 准备命令"):
        command = "non_existent_command"
        logger.info(f"命令：{command}")
    
    async with task_logger.step("2. 执行命令"):
        wrapper = get_wrapper()
        
        try:
            result = await wrapper.exec_tool(command, timeout=10)
            logger.info(f"执行结果：{result}")
        except Exception as e:
            logger.error(f"执行失败：{e}")
            # 错误会被自动记录
    
    async with task_logger.step("3. 错误处理"):
        logger.warning("命令执行失败，进行错误处理")
        error_message = "命令不存在或执行失败"
    
    # 生成报告
    print("\n" + "="*70)
    print("📋 错误诊断报告")
    print("="*70)
    
    report = task_logger.generate_report(format="text")
    print(report)


async def main():
    """主函数"""
    print("="*70)
    print("🔍 OpenClaw 全链路日志追踪示例")
    print("="*70)
    print("\n将演示 3 个场景：")
    print("1. 正常任务：用户查询项目进展")
    print("2. 慢任务：执行耗时命令")
    print("3. 错误任务：执行失败命令")
    print("\n" + "="*70)
    
    try:
        # 场景 1：正常任务
        print("\n【场景 1】正常任务")
        print("="*70)
        answer = await simulate_opclaw_task()
        print(f"\n✅ 回答：{answer}")
        
        await asyncio.sleep(1)
        
        # 场景 2：慢任务
        print("\n\n【场景 2】慢任务")
        print("="*70)
        await simulate_slow_task()
        
        await asyncio.sleep(1)
        
        # 场景 3：错误任务
        print("\n\n【场景 3】错误任务")
        print("="*70)
        await simulate_error_task()
        
        print("\n" + "="*70)
        print("🎉 所有示例完成！")
        print("="*70)
        print("\n💡 使用说明：")
        print("1. 在真实 OpenClaw 任务中导入 TaskLogger")
        print("2. 用 async with task_logger.step() 包裹每个步骤")
        print("3. 任务完成后调用 generate_report() 生成诊断报告")
        print("4. 根据报告定位慢/卡/错误问题")
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
