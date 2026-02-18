"""
ToolEngine - 工具引擎

职责：
1. 统一管理所有工具（web_search、web_fetch、exec）
2. 提供统一的异步 API
3. 集成超时保护（使用 OpenClaw Wrapper）
4. 工具结果格式化和缓存

可用工具：
- web_search: 网络搜索（Brave API）
- web_fetch: 网页内容获取
- exec: Shell 命令执行
- memory_search: 记忆搜索
- tts: 文本转语音
"""

import asyncio
import json
import logging
import sys
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from openclaw_timeout_wrapper import get_wrapper

logger = logging.getLogger(__name__)


class ToolType(Enum):
    """工具类型枚举"""
    WEB_SEARCH = "web_search"
    WEB_FETCH = "web_fetch"
    EXEC = "exec"
    MEMORY_SEARCH = "memory_search"
    TTS = "tts"


class ToolEngine:
    """
    工具引擎

    核心能力：
    1. 统一工具调用接口
    2. 自动超时保护
    3. 结果缓存
    4. 错误处理和重试
    """

    def __init__(self, memory_manager=None):
        """
        初始化工具引擎

        Args:
            memory_manager: 记忆管理器实例（用于 memory_search）
        """
        self.memory = memory_manager
        self.wrapper = get_wrapper()

        # 工具超时配置
        self.tool_timeouts = {
            ToolType.WEB_SEARCH: 30,      # 网络搜索：30 秒
            ToolType.WEB_FETCH: 30,       # 网页获取：30 秒
            ToolType.EXEC: 60,            # Shell 命令：60 秒
            ToolType.MEMORY_SEARCH: 10,   # 记忆搜索：10 秒
            ToolType.TTS: 15,             # TTS: 15 秒
        }

        # 结果缓存（LRU，最多 100 条）
        self.cache: Dict[str, Any] = {}
        self.cache_max_size = 100

        # 工具统计
        self.stats = {
            "calls": 0,
            "cache_hits": 0,
            "errors": 0,
        }

        logger.info("✅ ToolEngine 初始化完成")

    async def call(self, tool_type: ToolType, **kwargs) -> Dict:
        """
        统一工具调用接口

        Args:
            tool_type: 工具类型
            **kwargs: 工具参数

        Returns:
            Dict: 工具结果（统一格式）
        """
        self.stats["calls"] += 1

        # 生成缓存键
        cache_key = f"{tool_type.value}:{json.dumps(kwargs, sort_keys=True)}"

        # 检查缓存
        if cache_key in self.cache:
            self.stats["cache_hits"] += 1
            logger.info(f"📦 缓存命中：{tool_type.value}")
            return self.cache[cache_key]

        # 调用工具
        logger.info(f"🔧 调用工具：{tool_type.value}")

        try:
            if tool_type == ToolType.WEB_SEARCH:
                result = await self._web_search(**kwargs)
            elif tool_type == ToolType.WEB_FETCH:
                result = await self._web_fetch(**kwargs)
            elif tool_type == ToolType.EXEC:
                result = await self._exec(**kwargs)
            elif tool_type == ToolType.MEMORY_SEARCH:
                result = await self._memory_search(**kwargs)
            elif tool_type == ToolType.TTS:
                result = await self._tts(**kwargs)
            else:
                raise ValueError(f"未知工具类型：{tool_type.value}")

            # 缓存结果
            self._cache_result(cache_key, result)

            return result

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"❌ 工具调用失败：{tool_type.value} - {e}")

            return {
                "status": "error",
                "error": str(e),
                "tool": tool_type.value,
                "timestamp": datetime.now().isoformat()
            }

    async def _web_search(self, query: str, count: int = 5, **kwargs) -> Dict:
        """
        网络搜索

        Args:
            query: 搜索查询
            count: 结果数量（1-10）
            **kwargs: 其他参数（country、language 等）

        Returns:
            Dict: 搜索结果
        """
        logger.info(f"🔍 搜索：{query}")

        # 使用 Wrapper 调用（30 秒超时）
        timeout = self.tool_timeouts[ToolType.WEB_SEARCH]

        # TODO: 集成真实 OpenClaw web_search 工具
        # 目前使用模拟结果

        await asyncio.sleep(0.5)  # 模拟网络延迟

        result = {
            "status": "success",
            "tool": "web_search",
            "query": query,
            "results": [
                {
                    "title": f"搜索结果{i+1}: {query}",
                    "url": f"https://example.com/result{i+1}",
                    "snippet": f"这是关于「{query}」的搜索结果摘要..."
                }
                for i in range(min(count, 5))
            ],
            "count": min(count, 5),
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"✅ 搜索完成：{result['count']}条结果")
        return result

    async def _web_fetch(self, url: str, extract_mode: str = "markdown", **kwargs) -> Dict:
        """
        网页内容获取

        Args:
            url: 网页 URL
            extract_mode: 提取模式（"markdown" 或 "text"）
            **kwargs: 其他参数

        Returns:
            Dict: 网页内容
        """
        logger.info(f"📄 获取网页：{url}")

        timeout = self.tool_timeouts[ToolType.WEB_FETCH]

        # TODO: 集成真实 OpenClaw web_fetch 工具
        # 目前使用模拟结果

        await asyncio.sleep(0.5)  # 模拟网络延迟

        result = {
            "status": "success",
            "tool": "web_fetch",
            "url": url,
            "content": f"这是从 {url} 获取的网页内容（模拟）...\n\n# {url}\n\n网页内容摘要...",
            "extract_mode": extract_mode,
            "length": 500,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"✅ 获取完成：{result['length']}字符")
        return result

    async def _exec(self, command: str, timeout: Optional[int] = None, **kwargs) -> Dict:
        """
        Shell 命令执行

        Args:
            command: 命令字符串
            timeout: 超时时间（秒）
            **kwargs: 其他参数

        Returns:
            Dict: 执行结果
        """
        logger.info(f"⚙️ 执行命令：{command}")

        exec_timeout = timeout or self.tool_timeouts[ToolType.EXEC]

        # 使用 Wrapper 调用（带超时保护）
        result = await self.wrapper.exec_tool(command, timeout=exec_timeout)

        # 格式化结果
        if isinstance(result, dict):
            return {
                "status": result.get("status", "unknown"),
                "tool": "exec",
                "command": command,
                "output": result.get("output", ""),
                "error": result.get("error"),
                "duration": result.get("duration", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "success",
                "tool": "exec",
                "command": command,
                "output": str(result),
                "timestamp": datetime.now().isoformat()
            }

    async def _memory_search(self, query: str, n_results: int = 5, **kwargs) -> Dict:
        """
        记忆搜索

        Args:
            query: 搜索查询
            n_results: 结果数量
            **kwargs: 其他参数

        Returns:
            Dict: 搜索结果
        """
        logger.info(f"🧠 搜索记忆：{query}")

        if not self.memory:
            return {
                "status": "error",
                "error": "记忆管理器未初始化",
                "tool": "memory_search"
            }

        timeout = self.tool_timeouts[ToolType.MEMORY_SEARCH]

        # 调用记忆管理器
        try:
            results = await asyncio.wait_for(
                self.memory.search(query, n_results=n_results),
                timeout=timeout
            )

            return {
                "status": "success",
                "tool": "memory_search",
                "query": query,
                "results": results,
                "count": len(results),
                "timestamp": datetime.now().isoformat()
            }

        except asyncio.TimeoutError:
            logger.warning(f"⚠️ 记忆搜索超时（{timeout}秒）")
            return {
                "status": "error",
                "error": f"搜索超时（{timeout}秒）",
                "tool": "memory_search"
            }

    async def _tts(self, text: str, channel: Optional[str] = None, **kwargs) -> Dict:
        """
        文本转语音

        Args:
            text: 文本内容
            channel: 频道 ID（用于选择输出格式）
            **kwargs: 其他参数

        Returns:
            Dict: TTS 结果（MEDIA 路径）
        """
        logger.info(f"🔊 TTS: {text[:50]}...")

        timeout = self.tool_timeouts[ToolType.TTS]

        # TODO: 集成真实 OpenClaw tts 工具
        # 目前使用模拟结果

        await asyncio.sleep(0.3)  # 模拟处理

        result = {
            "status": "success",
            "tool": "tts",
            "text": text,
            "media_path": "MEDIA:tts_output_12345.mp3",
            "duration": 5.0,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"✅ TTS 完成：{result['media_path']}")
        return result

    def _cache_result(self, key: str, result: Dict):
        """缓存结果（LRU）"""
        if len(self.cache) >= self.cache_max_size:
            # 移除最旧的缓存
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[key] = result

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "type": "ToolEngine",
            "calls": self.stats["calls"],
            "cache_hits": self.stats["cache_hits"],
            "cache_size": len(self.cache),
            "errors": self.stats["errors"],
            "tools": [t.value for t in ToolType],
            "timeouts": {t.value: v for t, v in self.tool_timeouts.items()},
            "timestamp": datetime.now().isoformat()
        }


# ==================== 便捷函数 ====================

_engine_instance: Optional[ToolEngine] = None


def get_tool_engine(memory_manager=None) -> ToolEngine:
    """获取 ToolEngine 单例"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ToolEngine(memory_manager)
    return _engine_instance


# ==================== 测试代码 ====================

async def test_tool_engine():
    """测试 ToolEngine"""
    print("="*70)
    print("🔧 ToolEngine 测试")
    print("="*70)

    from mvp_jarvais.core.memory_manager import MemoryManager

    # 创建记忆管理器
    memory = MemoryManager(enable_v1=False)

    # 创建工具引擎
    engine = ToolEngine(memory)
    print("\n✅ ToolEngine 初始化完成")

    # 测试 1: web_search
    print("\n🔍 测试 1: web_search")
    result = await engine.call(ToolType.WEB_SEARCH, query="AI 最新进展", count=3)
    print(f"  状态：{result['status']}")
    print(f"  结果数：{result['count']}")
    if result['results']:
        print(f"  第 1 条：{result['results'][0]['title']}")

    # 测试 2: web_fetch
    print("\n📄 测试 2: web_fetch")
    result = await engine.call(ToolType.WEB_FETCH, url="https://example.com")
    print(f"  状态：{result['status']}")
    print(f"  长度：{result['length']}字符")

    # 测试 3: exec
    print("\n⚙️ 测试 3: exec")
    result = await engine.call(ToolType.EXEC, command="echo Hello World")
    print(f"  状态：{result['status']}")
    print(f"  输出：{result['output']}")

    # 测试 4: memory_search
    print("\n🧠 测试 4: memory_search")
    # 先记住一些数据
    await memory.remember(
        key="test_memory",
        content="这是一个测试记忆，用于验证记忆搜索功能",
        metadata={"type": "test"}
    )
    result = await engine.call(ToolType.MEMORY_SEARCH, query="测试记忆", n_results=2)
    print(f"  状态：{result['status']}")
    print(f"  结果数：{result['count']}")

    # 测试 5: 缓存
    print("\n📦 测试 5: 缓存机制")
    print(f"  缓存大小：{len(engine.cache)}")
    print(f"  调用次数：{engine.stats['calls']}")
    print(f"  缓存命中：{engine.stats['cache_hits']}")

    # 再次调用相同查询（应该命中缓存）
    result2 = await engine.call(ToolType.WEB_SEARCH, query="AI 最新进展", count=3)
    print(f"  再次调用后缓存命中：{engine.stats['cache_hits']}")

    # 统计
    print("\n📈 统计信息")
    stats = engine.get_stats()
    print(f"  工具：{stats['tools']}")
    print(f"  总调用：{stats['calls']}")
    print(f"  缓存命中：{stats['cache_hits']}")
    print(f"  错误：{stats['errors']}")

    print("\n✅ ToolEngine 测试完成！")


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_tool_engine())
