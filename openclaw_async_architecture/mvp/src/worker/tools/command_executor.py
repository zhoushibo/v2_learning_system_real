"""命令执行器

执行系统命令，带安全限制

安全限制：
- 白名单机制
- 禁止危险命令
- 超时保护
"""

import asyncio
import time
from typing import Dict, Any
from .base_tool import BaseTool, ToolInput, ToolOutput
from .security import validate_command, with_timeout


# ========== 输入Schema ==========

class ExecCommandInput(ToolInput):
    """执行命令输入"""
    command: str
    timeout: int = 30
    cwd: str = None


# ========== 白名单命令 ==========

SAFE_COMMANDS = [
    # 文件操作
    "ls", "dir",
    "cat", "type",
    "grep", "findstr",

    # 开发工具
    "git",
    "python", "python3", "py",
    "pip", "pip3",
    "npm", "node",

    # 安全工具
    "echo", "cd",
    "pwd",
]

# 禁止命令关键词
DANGEROUS_KEYWORDS = [
    "rm -rf",
    "del /f /s /q",
    "format",
    "mkfs",
    "dd",
    "> /dev/",
    ":(){:|:&};:",  # Fork bomb
    "shutdown",
    "reboot",
    "halt",
]


# ========== 工具实现 ==========

class ExecCommandTool(BaseTool):
    """执行命令工具（带安全限制）

    特性：
    - 白名单机制
    - 危险命令检测
    - 超时保护
    - stdout和stderr捕获
    """

    name = "exec_command"
    description = "执行系统命令（白名单限制，超时30秒）"
    input_schema = ExecCommandInput

    async def execute(self, input_data: ExecCommandInput) -> ToolOutput:
        """
        执行命令

        安全检查流程：
        1. 使用安全框架验证命令
        2. 执行命令（超时保护）
        3. 捕获输出

        Args:
            input_data: 命令输入

        Returns:
            ToolOutput: 执行结果
        """

        # 安全检查：使用统一的安全框架
        try:
            validate_command(input_data.command)
        except (ValueError, PermissionError) as e:
            return ToolOutput(
                success=False,
                error=f"命令安全检查失败: {str(e)}",
                metadata={"command": input_data.command}
            )

        # 执行命令
        try:
            process = await asyncio.create_subprocess_shell(
                input_data.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=input_data.cwd
            )

            try:
                # 使用asyncio超时
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=input_data.timeout
                )

                stdout_text = stdout.decode('utf-8', errors='replace')
                stderr_text = stderr.decode('utf-8', errors='replace')

                return ToolOutput(
                    success=process.returncode == 0,
                    data={
                        "stdout": stdout_text,
                        "stderr": stderr_text,
                        "exit_code": process.returncode
                    },
                    metadata={
                        "command": input_data.command,
                        "timeout": input_data.timeout,
                        "cwd": input_data.cwd or "当前目录",
                        "execution_time": None  # TODO: 添加计时
                    }
                )
            except asyncio.TimeoutError:
                # 超时，杀死进程
                process.kill()
                await process.wait()

                return ToolOutput(
                    success=False,
                    error=f"命令执行超时（{input_data.timeout}秒）",
                    metadata={
                        "command": input_data.command,
                        "timeout": input_data.timeout
                    }
                )

        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"命令执行失败: {str(e)}",
                metadata={"command": input_data.command}
            )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入

        Args:
            input_data: 输入数据

        Returns:
            bool: 是否验证通过
        """
        return "command" in input_data and isinstance(input_data["command"], str)

    def _check_command_safety(self, command: str) -> dict:
        """
        检查命令是否安全

        检查项：
        1. 禁止关键词
        2. 白名单验证

        Args:
            command: 命令字符串

        Returns:
            dict: {"safe": bool, "reason": str}
        """
        # 1. 检查禁止关键词
        for keyword in DANGEROUS_KEYWORDS:
            if keyword.lower() in command.lower():
                return {
                    "safe": False,
                    "reason": f"包含禁止关键词: {keyword}"
                }

        # 2. 获取命令名（第一个词）
        command_parts = command.strip().split()
        if not command_parts:
            return {"safe": False, "reason": "命令为空"}

        command_name = command_parts[0]

        # 3. 检查白名单
        if command_name not in SAFE_COMMANDS:
            return {
                "safe": False,
                "reason": f"命令不在白名单中: {command_name}\n可用命令: {', '.join(SAFE_COMMANDS)}"
            }

        return {"safe": True}
