# -*- coding: utf-8 -*-
"""
工具安全框架

提供统一的工具安全保障：
- 参数验证
- 路径白名单
- 命令白名单
- 审计日志
- 超时限制
"""

import os
import time
import asyncio
import logging
from typing import Dict, Any, List, Set, Optional, Callable
from functools import wraps
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)


# ============================================================================
# 1. 路径白名单
# ============================================================================

ALLOWED_PATHS = [
    os.path.abspath(r"C:\Users\10952\.openclaw\workspace"),
]

def validate_path(path: str) -> str:
    """
    验证路径是否在白名单中

    安全检查：
    - 规范化路径（处理 . 和 ..）
    - 检查是否包含 ..
    - 检查是否在白名单目录内
    - 解析符号链接

    Args:
        path: 待验证的路径（绝对或相对）

    Returns:
        str: 规范化的绝对路径

    Raises:
        PermissionError: 路径不在白名单中
        ValueError: 路径包含非法字符
    """
    # 转为绝对路径
    abspath = os.path.abspath(path)

    # 规范化路径
    normalized = os.path.normpath(abspath)

    # 检查路径遍历攻击
    if ".." in normalized:
        raise ValueError(f"Path traversal not allowed: {path}")

    # 解析符号链接
    real_path = os.path.realpath(normalized)

    # 检查白名单
    for allowed in ALLOWED_PATHS:
        if real_path.startswith(allowed):
            return real_path

    raise PermissionError(f"Path not in allowed directories: {path}")


# ============================================================================
# 2. 命令白名单
# ============================================================================

ALLOWED_COMMANDS: Dict[str, List[str]] = {
    "ls": ["-la", "-l", "-a", "-h", "--color"],
    "dir": ["/W", "/B", "/S"],
    "cat": [],
    "type": [],
    "echo": [],
    "pwd": [],
    "cd": [],
    "grep": ["-i", "-r", "-v", "-n", "-C"],
    "findstr": ["/I", "/N", "/C", "/S"],
    "head": ["-n"],
    "tail": ["-n"],
    "wc": ["-l", "-w", "-c"],
    "date": [],
    "time": [],
}

BLOCKED_PATTERNS: List[str] = [
    "rm -rf",
    "rmdir /s /q",
    "del /f /q",
    "chmod +x",
    "chown",
    "shutdown",
    "reboot",
    "format",
    "fdisk",
]

def validate_command(cmd: str) -> bool:
    """
    验证命令是否在白名单中

    安全检查：
    - 检查命令是否在白列表中
    - 检查参数是否允许
    - 检查是否包含危险模式

    Args:
        cmd: 待验证的命令字符串

    Returns:
        bool: 是否验证通过

    Raises:
        PermissionError: 命令不在白名单中
        ValueError: 包含危险模式
    """
    # 转小写（Windows命令不区分大小写）
    cmd_lower = cmd.lower()

    # 检查危险模式
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in cmd_lower:
            raise ValueError(f"Blocked command pattern: {pattern}")

    # 解析命令
    parts = cmd.split()
    if not parts:
        raise ValueError("Empty command")

    base_cmd = parts[0]

    # 检查白名单
    if base_cmd not in ALLOWED_COMMANDS:
        raise PermissionError(f"Command not allowed: {base_cmd}")

    # 检查参数
    allowed_args = ALLOWED_COMMANDS[base_cmd]
    if allowed_args:
        for arg in parts[1:]:
            # 如果参数以-或/开头，检查是否允许
            if (arg.startswith("-") or arg.startswith("/")) and arg not in allowed_args:
                raise ValueError(f"Invalid argument for {base_cmd}: {arg}")

    return True


# ============================================================================
# 3. Python代码限制
# ============================================================================

BLOCKED_PYTHON_FUNCTIONS: Set[str] = {
    "open",
    "exec",
    "eval",
    "compile",
    "__import__",
    "globals",
    "locals",
    "vars",
    "dir",
    "getattr",
    "setattr",
}

def validate_python_code(code: str) -> bool:
    """
    验证Python代码是否包含危险函数

    Args:
        code: 待验证的Python代码

    Returns:
        bool: 是否验证通过

    Raises:
        ValueError: 代码包含危险函数
    """
    code_lower = code.lower()

    for func in BLOCKED_PYTHON_FUNCTIONS:
        if f"{func}(" in code_lower:
            raise ValueError(f"Python function not allowed: {func}")

    # 检查其他危险模式
    if "__" in code and "import" in code_lower:
        raise ValueError("Dangerous import pattern detected")

    return True


# ============================================================================
# 4. 审计日志
# ============================================================================

AUDIT_MASKED_FIELDS: Set[str] = {
    "password",
    "api_key",
    "token",
    "secret",
    "key",
}

def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    掩码敏感数据

    Args:
        data: 原始数据

    Returns:
        dict: 掩码后的数据
    """
    masked = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(field in key_lower for field in AUDIT_MASKED_FIELDS):
            masked[key] = "***HIDDEN***"
        elif isinstance(value, dict):
            masked[key] = mask_sensitive_data(value)
        else:
            masked[key] = value
    return masked


async def audit_log(
    event_type: str,
    tool_name: str,
    params: Dict[str, Any],
    result: Optional[str] = None,
    error: Optional[str] = None,
    user: str = "unknown",
) -> None:
    """
    记录审计日志

    Args:
        event_type: 事件类型（call, error, etc.）
        tool_name: 工具名称
        params: 工具参数
        result: 执行结果（可选）
        error: 错误信息（可选）
        user: 用户标识
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "tool_name": tool_name,
        "params": mask_sensitive_data(params),
        "result": result[:1000] if result else None,  # 限制长度
        "error": error[:1000] if error else None,
        "user": user,
    }

    # 记录到日志
    logger.info(f"AUDIT: {log_entry}")

    # TODO: 发送到审计日志存储（文件、数据库、ELK等）


# ============================================================================
# 5. 超时限制
# ============================================================================

def with_timeout(timeout_seconds: float = 30.0):
    """
    超时装饰器

    Args:
        timeout_seconds: 超时时间（秒）

    Returns:
        装饰器函数
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
                return result
            except asyncio.TimeoutError:
                raise TimeoutError(f"Execution timeout after {timeout_seconds}s")

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                if elapsed > timeout_seconds:
                    raise TimeoutError(f"Execution timeout after {timeout_seconds}s")
                return result
            except Exception as e:
                raise e

        # 根据函数是否协程返回不同的包装器
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# ============================================================================
# 6. 综合安全检查中间件
# ============================================================================

class SecurityChecker:
    """安全检查中间件"""

    @staticmethod
    def check_path_tool(tool_name: str, params: Dict[str, Any]) -> bool:
        """
        检查路径工具的安全性

        Args:
            tool_name: 工具名称
            params: 工具参数

        Returns:
            bool: 是否通过检查

        Raises:
            ValueError/PermissionError: 安全检查失败
        """
        if tool_name in ["read_file", "write_file", "list_directory", "create_directory"]:
            if "path" in params:
                validate_path(params["path"])
        return True

    @staticmethod
    def check_command_tool(tool_name: str, params: Dict[str, Any]) -> bool:
        """
        检查命令工具的安全性

        Args:
            tool_name: 工具名称
            params: 工具参数

        Returns:
            bool: 是否通过检查

        Raises:
            ValueError/PermissionError: 安全检查失败
        """
        if tool_name == "exec_command":
            if "command" in params:
                validate_command(params["command"])
        return True

    @staticmethod
    def check_python_tool(tool_name: str, params: Dict[str, Any]) -> bool:
        """
        检查Python工具的安全性

        Args:
            tool_name: 工具名称
            params: 工具参数

        Returns:
            bool: 是否通过检查

        Raises:
            ValueError: 安全检查失败
        """
        if tool_name == "exec_python":
            if "code" in params:
                validate_python_code(params["code"])
        return True

    @staticmethod
    async def pre_tool_call(tool_name: str, params: Dict[str, Any]) -> bool:
        """
        工具调用前安全检查

        Args:
            tool_name: 工具名称
            params: 工具参数

        Returns:
            bool: 是否通过检查

        Raises:
            各种安全异常
        """
        SecurityChecker.check_path_tool(tool_name, params)
        SecurityChecker.check_command_tool(tool_name, params)
        SecurityChecker.check_python_tool(tool_name, params)

        # 记录审计日志
        await audit_log(
            event_type="call",
            tool_name=tool_name,
            params=params
        )

        return True

    @staticmethod
    async def post_tool_call(
        tool_name: str,
        params: Dict[str, Any],
        result: Dict[str, Any],
    ) -> bool:
        """
        工具调用后安全处理

        Args:
            tool_name: 工具名称
            params: 工具参数
            result: 执行结果

        Returns:
            bool: 是否处理成功
        """
        success = result.get("success", False)

        if success:
            await audit_log(
                event_type="success",
                tool_name=tool_name,
                params=params,
                result=str(result.get("data", ""))[:1000],
            )
        else:
            await audit_log(
                event_type="error",
                tool_name=tool_name,
                params=params,
                error=result.get("error", "")[:1000],
            )

        return True
