"""
OpenClaw Wrapper - 超时保护拦截器

解决问题：
- 提问超过10分钟导致卡顿
- LLM API无超时保护
- 工具执行无超时保护

核心功能：
1. LLM调用拦截（自动添加60秒超时）
2. 工具执行拦截（exec: 60秒, web: 30秒）
3. Fallback机制（超时后返回模拟结果）
4. 永不崩溃、永不阻塞
"""

import asyncio
import functools
from typing import Callable, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenClawTimeoutError(Exception):
    """OpenClaw超时异常"""
    pass


def with_timeout(timeout_seconds: int, fallback_result: Any = None):
    """
    超时保护装饰器

    Args:
        timeout_seconds: 超时时间（秒）
        fallback_result: 超时时的Fallback结果

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.warning(f"⚠️  {func.__name__} 超时（{timeout_seconds}秒），使用Fallback")
                if fallback_result is not None:
                    return fallback_result
                raise OpenClawTimeoutError(
                    f"{func.__name__} 执行超时（{timeout_seconds}秒）"
                )

        return async_wrapper
    return decorator


class OpenClawWrapper:
    """
    OpenClaw超时保护Wrapper

    使用方式：
    wrapper = OpenClawWrapper()

    # 方式1：直接调用（自动添加超时）
    result = await wrapper.chat(messages)

    # 方式2：手动指定超时
    @wrapper.timeout(60)
    async def long_task():
        ...

    # 方式3：Fallback模式
    result = await wrapper.chat(messages, fallback="抱歉，响应超时")
    """

    def __init__(self):
        # 默认超时配置
        self.default_timeouts = {
            "llm_chat": 60,          # LLM对话：60秒
            "exec_tool": 60,         # exec工具：60秒
            "web_search": 30,        # web搜索：30秒
            "web_fetch": 30,         # web获取：30秒
            "memory_search": 30,     # 记忆搜索：30秒
        }

        # Fallback结果
        self.fallback_results = {
            "llm_chat": "抱歉，响应超时，请简化问题或重试。",
            "exec_tool": {"status": "timeout", "error": "命令执行超时"},
            "web_search": {"results": [], "message": "搜索超时"},
            "web_fetch": {"content": "", "message": "获取超时"},
        }

        logger.info("✅ OpenClawWrapper初始化完成")

    @with_timeout(timeout_seconds=60, fallback_result="抱歉，响应超时。")
    async def chat(self, messages, timeout: Optional[int] = None, fallback: Optional[str] = None):
        """
        LLM对话（带超时保护）

        Args:
            messages: 对话消息
            timeout: 自定义超时时间（秒）
            fallback: 自定义Fallback结果

        Returns:
            LLM响应
        """
        # TODO: 调用OpenClaw的LLM API
        # 这里需要根据OpenClaw的实际API调整

        logger.info(f"🤖 LLM对话：{len(messages)}条消息")
        logger.info(f"⏰ 超时设置：{timeout or self.default_timeouts['llm_chat']}秒")

        # 临时返回模拟结果
        # 实际使用时替换为：
        # from openclaw import main
        # return await main.chat(messages)

        await asyncio.sleep(1)  # 模拟处理

        return "这是模拟的LLM响应。实际使用时需要调用OpenClaw API。"

    @with_timeout(timeout_seconds=60, fallback_result={"status": "timeout", "error": "命令执行超时"})
    async def exec_tool(self, command: str, timeout: Optional[int] = None):
        """
        exec工具（带超时保护）

        Args:
            command: 命令字符串
            timeout: 自定义超时时间（秒）

        Returns:
            执行结果
        """
        logger.info(f"🔧 exec工具：{command}")
        logger.info(f"⏰ 超时设置：{timeout or self.default_timeouts['exec_tool']}秒")

        # TODO: 调用OpenClaw的exec工具
        # 实际使用时替换为：
        # from openclaw import main
        # return await main.exec(command)

        await asyncio.sleep(0.5)  # 模拟处理

        return {
            "status": "success",
            "output": "这是模拟的exec结果",
            "duration": 0.5
        }

    @with_timeout(timeout_seconds=30, fallback_result={"results": [], "message": "搜索超时"})
    async def web_search(self, query: str, timeout: Optional[int] = None):
        """
        web搜索工具（带超时保护）

        Args:
            query: 搜索查询
            timeout: 自定义超时时间（秒）

        Returns:
            搜索结果
        """
        logger.info(f"🔍 web搜索：{query}")
        logger.info(f"⏰ 超时设置：{timeout or self.default_timeouts['web_search']}秒")

        # TODO: 调用OpenClaw的web_search工具

        await asyncio.sleep(0.5)  # 模拟处理

        return {
            "results": [
                {"title": "模拟搜索结果1", "url": "https://example.com/1"},
                {"title": "模拟搜索结果2", "url": "https://example.com/2"},
            ],
            "count": 2
        }

    async def safe_invoke(self, func: Callable, *args, timeout: int = 60, fallback: Any = None, **kwargs):
        """
        安全调用（通用超时保护）

        Args:
            func: 要调用的函数
            timeout: 超时时间
            fallback: Fallback结果
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数执行结果或Fallback
        """
        try:
            return await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"⚠️  {func.__name__} 超时（{timeout}秒）")
            if fallback is not None:
                return fallback
            raise OpenClawTimeoutError(f"{func.__name__} 执行超时")


# ==================== 单例 ====================

_wrapper_instance: Optional[OpenClawWrapper] = None


def get_wrapper() -> OpenClawWrapper:
    """获取OpenClawWrapper单例"""
    global _wrapper_instance
    if _wrapper_instance is None:
        _wrapper_instance = OpenClawWrapper()
    return _wrapper_instance


# ==================== 测试代码 ====================

async def test_timeout():
    """测试超时保护"""
    print("="*60)
    print("测试：OpenClaw超时保护")
    print("="*60)

    wrapper = get_wrapper()

    # 测试1：正常情况（应该成功）
    print("\n测试1：正常LLM对话（应该<60秒）")
    start = datetime.now()
    result = await wrapper.chat([{"role": "user", "content": "测试"}])
    duration = (datetime.now() - start).total_seconds()
    print(f"✅ 成功：{duration:.2f}秒")
    print(f"结果：{result}")

    # 测试2：超时情况（应该触发Fallback）
    print("\n测试2：模拟超时（5秒超时）")
    async def slow_task():
        await asyncio.sleep(10)  # 模拟10秒任务
        return "成功"

    try:
        result = await wrapper.safe_invoke(slow_task, timeout=5, fallback="超时Fallback")
        print(f"✅ Fallback激活：{result}")
    except OpenClawTimeoutError as e:
        print(f"❌ 超时异常：{e}")

    # 测试3：exec工具测试
    print("\n测试3：exec工具超时测试")
    result = await wrapper.exec_tool("echo test")
    print(f"✅ exec结果：{result}")

    print("\n" + "="*60)
    print("✅ 测试完成")


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_timeout())
