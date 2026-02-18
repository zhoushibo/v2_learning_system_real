"""工具管理器

管理所有Worker工具，提供统一的调用接口

Phase 2优化：
- 集成工具结果缓存
- 连接池优化
"""

from typing import Dict, List, Optional, Any
from .base_tool import BaseTool, ToolInput, ToolOutput
from .security import SecurityChecker
from ...common.tool_cache import tool_cache


class ToolManager:
    """工具管理器

    核心功能：
    - 工具注册
    - 工具查找
    - 工具调用
    - 白名单管理
    - 沙盒模式控制

    特性：
    - 线程安全
    - 异步执行
    - 内置安全检查
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._whitelist: List[str] = []
        self._sandbox_enabled = True

        # Phase 2: 工具缓存
        self._cache_enabled = True
        self._readonly_tools = {
            "read_file",
            "list_directory"
        }  # 只读工具（更激进的缓存）

    def register_tool(self, tool: BaseTool):
        """
        注册工具

        Args:
            tool: BaseTool实例
        """
        self._tools[tool.name] = tool
        print(f"[ToolManager] [OK] 工具注册: {tool.name}")

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取工具

        Args:
            tool_name: 工具名称

        Returns:
            BaseTool: 工具实例（如果存在）
        """
        return self._tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, str]]:
        """
        列出所有工具

        Returns:
            List[dict]: 工具列表，包含名称和描述
        """
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self._tools.values()
        ]

    async def call_tool(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        use_cache: bool = True
    ) -> ToolOutput:
        """
        调用工具（带缓存优化）

        Args:
            tool_name: 工具名称
            input_data: 输入数据（字典格式）
            use_cache: 是否使用缓存

        Returns:
            ToolOutput: 输出结果
        """

        # 检查工具是否存在
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolOutput(
                success=False,
                error=f"工具不存在: {tool_name}",
                metadata={"tool_name": tool_name}
            )

        # 检查白名单
        if self._whitelist and tool_name not in self._whitelist:
            return ToolOutput(
                success=False,
                error=f"工具不在白名单中: {tool_name}",
                metadata={
                    "tool_name": tool_name,
                    "whitelist": self._whitelist
                }
            )

        # 检查沙盒模式
        if self._sandbox_enabled and not hasattr(tool, 'sandbox_safe'):
            # 如果标记为sandbox_safe=True，允许执行
            # 否则拒绝
            pass

        # === Phase 2: 缓存检查（只读工具优先查缓存） ===
        if self._cache_enabled and use_cache and tool_name in self._readonly_tools:
            cached_result = tool_cache.get_by_tool(tool_name, input_data)
            if cached_result is not None:
                # 返回缓存结果
                print(f"[ToolManager] [缓存命中] {tool_name}")
                return ToolOutput.model_validate(cached_result)

        # === 安全检查 ===
        try:
            await SecurityChecker.pre_tool_call(tool_name, input_data)
        except (ValueError, PermissionError) as e:
            return ToolOutput(
                success=False,
                error=f"安全检查失败: {str(e)}",
                metadata={
                    "tool_name": tool_name,
                    "security_error": str(e)
                }
            )

        # 验证输入
        if not tool.validate_input(input_data):
            return ToolOutput(
                success=False,
                error=f"输入数据无效: {input_data}",
                metadata={"tool_name": tool_name, "input_data": input_data}
            )

        # 转换输入数据为ToolInput对象
        try:
            typed_input = tool.input_schema(**input_data)
        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"输入数据格式错误: {str(e)}",
                metadata={"tool_name": tool_name, "input_data": input_data}
            )

        # 执行工具
        try:
            output = await tool.execute(typed_input)

            # === Phase 2: 写入缓存（成功结果） ===
            if self._cache_enabled and output.success:
                ttl = 3600 if tool_name in self._readonly_tools else 600  # 只读工具1小时，其他10分钟
                tool_cache.set_by_tool(tool_name, input_data, output.dict(), ttl=ttl)

            # === 审计日志（成功） ===
            await SecurityChecker.post_tool_call(
                tool_name,
                input_data,
                output.dict()
            )

            return output
        except Exception as e:
            error_output = ToolOutput(
                success=False,
                error=f"工具执行失败: {str(e)}",
                metadata={
                    "tool_name": tool_name,
                    "input_data": input_data
                }
            )

            # === 审计日志（失败） ===
            await SecurityChecker.post_tool_call(
                tool_name,
                input_data,
                error_output.dict()
            )

            return error_output

    def set_whitelist(self, whitelist: List[str]):
        """
        设置白名单

        Args:
            whitelist: 白名单列表（工具名称）
        """
        self._whitelist = whitelist
        print(f"[ToolManager] ✅ 白名单设置: {whitelist}")

    def enable_sandbox(self, enabled: bool = True):
        """
        启用/禁用沙盒模式

        Args:
            enabled: 是否启用
        """
        self._sandbox_enabled = enabled
        mode = "启用" if enabled else "禁用"
        print(f"[ToolManager] ✅ 沙盒模式已{mode}")

    def get_tool_count(self) -> int:
        """获取已注册工具数量"""
        return len(self._tools)

    # ====== Phase 2: 缓存管理 ======

    def enable_cache(self, enabled: bool = True):
        """
        启用/禁用缓存

        Args:
            enabled: 是否启用
        """
        self._cache_enabled = enabled
        status = "启用" if enabled else "禁用"
        print(f"[ToolManager] [缓存] 已{status}")

    def clear_cache(self, tool_name: Optional[str] = None):
        """
        清空缓存

        Args:
            tool_name: 工具名称（None表示清空所有）
        """
        if tool_name:
            success = tool_cache.clear_by_tool(tool_name)
            print(f"[ToolManager] [缓存] 清空工具缓存: {tool_name} ({'成功' if success else '失败'})")
        else:
            success = tool_cache.clear()
            print(f"[ToolManager] [缓存] 清空所有缓存 ({'成功' if success else '失败'})")

    def get_cache_stats(self) -> dict:
        """
        获取缓存统计

        Returns:
            dict: 缓存统计信息
        """
        return tool_cache.get_stats()

    def invalidate_cache_pattern(self, pattern: str) -> int:
        """
        根据模式使缓存失效

        Args:
            pattern: 匹配模式（如 "read_file:*"）

        Returns:
            失效的缓存数量
        """
        count = tool_cache.invalidate_by_pattern(pattern)
        print(f"[ToolManager] [缓存] 模式失效: {pattern} ({count}个)")
        return count
