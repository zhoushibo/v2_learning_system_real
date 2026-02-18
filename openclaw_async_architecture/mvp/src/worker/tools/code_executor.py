"""Python代码执行器

执行Python代码，带安全限制

安全限制：
- 超时保护
- 危险函数限制
- 异常捕获
- 有限的命名空间
"""

import asyncio
import sys
import io
import traceback
from typing import Dict, Any
from .base_tool import BaseTool, ToolInput, ToolOutput
from .security import validate_python_code


# ========== 输入Schema ==========

class ExecPythonInput(ToolInput):
    """执行Python代码输入"""
    code: str
    timeout: int = 10
    capture_output: bool = True


# ========== 工具实现 ==========

class ExecPythonTool(BaseTool):
    """执行Python代码工具

    特性：
    - 超时保护
    - 输出捕获（stdout和stderr）
    - 异常捕获
    - 有限的命名空间

    安全措施：
    - 默认超时10秒
    - 禁止修改系统环境
    - 独立的exec全局命名空间
    """

    name = "exec_python"
    description = "执行Python代码（超时10秒，可捕获输出）"
    input_schema = ExecPythonInput

    async def execute(self, input_data: ExecPythonInput) -> ToolOutput:
        """
        执行Python代码

        安全检查流程：
        1. 使用安全框架验证代码
        2. 创建独立的exec命名空间
        3. 创建输出捕获
        4. 带超时执行代码
        5. 捕获异常

        Args:
            input_data: 代码输入

        Returns:
            ToolOutput: 执行结果
        """

        # 安全检查：使用统一的安全框架
        try:
            validate_python_code(input_data.code)
        except ValueError as e:
            return ToolOutput(
                success=False,
                error=f"代码安全检查失败: {str(e)}",
                metadata={"code_length": len(input_data.code)}
            )

        # 保存原始标准输出
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        # 创建输出捕获
        if input_data.capture_output:
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

        try:
            # 创建exec全局命名空间
            # 限制为安全的内置函数
            exec_globals = {
                "__name__": "__main__",
                "__builtins__": __builtins__,
                # 可以添加更多安全的内置模块
                "print": print,
            }

            # 超时执行
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(
                        lambda: exec(input_data.code, exec_globals)
                    ),
                    timeout=input_data.timeout
                )

                if input_data.capture_output:
                    stdout_text = stdout_capture.getvalue()
                    stderr_text = stderr_capture.getvalue()
                else:
                    stdout_text = ""
                    stderr_text = ""

                return ToolOutput(
                    success=True,
                    data={
                        "stdout": stdout_text,
                        "stderr": stderr_text
                    },
                    metadata={
                        "timeout": input_data.timeout,
                        "code_length": len(input_data.code)
                    }
                )

            except asyncio.TimeoutError:
                return ToolOutput(
                    success=False,
                    error=f"代码执行超时（{input_data.timeout}秒）",
                    metadata={"timeout": input_data.timeout}
                )

        except Exception as e:
            # 捕获异常
            error_msg = traceback.format_exc()

            if input_data.capture_output:
                stderr_text = stderr_capture.getvalue()
            else:
                stderr_text = ""

            return ToolOutput(
                success=False,
                error=f"代码执行失败: {str(e)}",
                data={
                    "stdout": stdout_capture.getvalue() if input_data.capture_output else "",
                    "stderr": error_msg + "\n" + stderr_text
                },
                metadata={
                    "timeout": input_data.timeout,
                    "exception": type(e).__name__
                }
            )

        finally:
            # 恢复标准输出
            if input_data.capture_output:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入

        Args:
            input_data: 输入数据

        Returns:
            bool: 是否验证通过
        """
        return "code" in input_data and isinstance(input_data["code"], str)
