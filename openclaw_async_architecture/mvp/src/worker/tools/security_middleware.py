"""
Security Middleware
===================

将安全框架改造为中间件（整合 Phase 1 安全框架）
"""
import asyncio
from typing import Dict, Any, Optional

from middleware import BaseMiddleware, ExecutionContext, MiddlewareResult
from .security import (
    validate_path,
    validate_command,
    validate_python_code,
    mask_sensitive_data,
)


class SecurityMiddleware(BaseMiddleware):
    """
    安全中间件（整合 Phase 1 安全框架）

    功能：
    - 路径白名单验证
    - 命令白名单验证
    - Python 代码验证
    - 敏感数据掩码（审计日志）
    """

    def __init__(
        self,
        name: str = "security",
        enabled: bool = True,
        mask_sensitive: bool = True
    ):
        """
        初始化安全中间件。

        Args:
            name: 中间件名称
            enabled: 是否启用
            mask_sensitive: 是否掩码敏感数据
        """
        super().__init__(name, enabled, priority=1)  # 最高优先级（最先执行）
        self.mask_sensitive = mask_sensitive

    async def pre_process(self, ctx: ExecutionContext) -> MiddlewareResult:
        """
        执行安全检查（预处理）

        Args:
            ctx: 执行上下文

        Returns:
            MiddlewareResult
        """
        tool_name = ctx.tool_name
        params = ctx.parameters

        # 根据工具类型执行不同的安全检查
        try:
            # 文件系统工具 - 路径验证
            if tool_name in ["read_file", "write_file", "list_directory", "create_directory"]:
                if "path" in params:
                    validate_path(params["path"])

            # 命令执行工具 - 命令验证
            elif tool_name in ["exec_command", "exec_python"]:
                if tool_name == "exec_command" and "command" in params:
                    validate_command(params["command"])
                elif tool_name == "exec_python" and "code" in params:
                    validate_python_code(params["code"])

            # 如果所有检查通过
            return MiddlewareResult()

        except (PermissionError, ValueError) as e:
            # 安全检查失败
            return MiddlewareResult(
                success=False,
                skip_remaining=True,
                error=f"Security check failed: {e}"
            )

        except Exception as e:
            # 意外错误
            return MiddlewareResult(
                success=False,
                skip_remaining=True,
                error=f"Security middleware error: {e}"
            )

    async def post_process(
        self,
        ctx: ExecutionContext,
        tool_result: Any
    ) -> MiddlewareResult:
        """
        后处理：掩码敏感数据

        Args:
            ctx: 执行上下文
            tool_result: 工具执行结果

        Returns:
            MiddlewareResult（可能修改结果）
        """
        # 如果需要掩码且结果包含敏感数据
        if self.mask_sensitive:
            # 对结果进行敏感数据掩码
            # 注意：这里假设 tool_result 是 dict 类型
            if isinstance(tool_result, dict):
                masked_result = mask_sensitive_data(tool_result)
                return MiddlewareResult(modified_result=masked_result)

        return MiddlewareResult()

    async def on_error(
        self,
        ctx: ExecutionContext,
        error: Exception
    ) -> MiddlewareResult:
        """
        错误处理

        Args:
            ctx: 执行上下文
            error: 异常对象

        Returns:
            MiddlewareResult
        """
        # 记录安全相关的错误
        print(f"[SecurityMiddleware] Error in tool {ctx.tool_name}: {error}")

        # 返回错误信息（不重新抛出）
        return MiddlewareResult(success=False, error=str(error))
