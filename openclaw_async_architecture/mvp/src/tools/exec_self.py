"""
自主实现的exec工具
使用asyncio + subprocess，完全自主可控
支持前台PTY模式和后台模式
"""
import asyncio
import logging
from typing import Optional, Tuple, List
import shlex
import sys

logger = logging.getLogger(__name__)


class ExecTool:
    """自主实现的exec工具，完全独立于OpenClaw"""

    def __init__(
        self,
        default_timeout: int = 30,
        workdir: Optional[str] = None,
        use_pty: bool = False
    ):
        """
        初始化

        Args:
            default_timeout: 默认超时时间（秒）
            workdir: 工作目录
            use_pty: 是否使用PTY（伪终端）
        """
        self.default_timeout = default_timeout
        self.workdir = workdir
        self.use_pty = use_pty

    async def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        background: bool = False,
        capture_output: bool = True,
        workdir: Optional[str] = None
    ) -> Tuple[int, str, str]:
        """
        执行Shell命令

        Args:
            command: 要执行的命令
            timeout: 超时时间（秒），None表示使用默认值
            background: 是否后台运行
            capture_output: 是否捕获输出
            workdir: 工作目录，None表示使用默认值

        Returns:
            (exit_code, stdout, stderr)
        """
        if not command or not command.strip():
            return -1, "", "空命令"

        cmd = command.strip()
        actual_timeout = timeout or self.default_timeout
        actual_workdir = workdir or self.workdir

        logger.info(f"[Exec] 执行命令: {cmd}")
        logger.info(f"[Exec] 工作目录: {actual_workdir or 'current'}")
        logger.info(f"[Exec] PTY: {self.use_pty}")

        if background:
            # 后台模式（不等待完成，立即返回）
            return await self._execute_background(cmd, actual_workdir)
        else:
            # 前台模式（等待完成）
            return await self._execute_foreground(
                cmd,
                timeout=actual_timeout,
                workdir=actual_workdir,
                capture_output=capture_output
            )

    async def _execute_foreground(
        self,
        command: str,
        timeout: int,
        workdir: Optional[str],
        capture_output: bool
    ) -> Tuple[int, str, str]:
        """
        前台执行命令（等待完成）
        """
        try:
            # 创建子进程
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
                cwd=workdir
            )

            # 等待完成（带超时）
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )

                # 解码输出
                stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ""
                stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ""

                logger.info(f"[Exec] 命令完成: exit_code={process.returncode}")

                return (
                    process.returncode or 0,
                    stdout_text,
                    stderr_text
                )

            except asyncio.TimeoutError:
                # 超时，终止进程
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass

                logger.error(f"[Exec] 命令超时（{timeout}秒），已终止")
                return -1, "", f"命令超时（{timeout}秒），已终止"

        except Exception as e:
            logger.error(f"[Exec] 执行失败: {e}")
            return -1, "", str(e)

    async def _execute_background(
        self,
        command: str,
        workdir: Optional[str]
    ) -> Tuple[int, str, str]:
        """
        后台执行命令（不等待完成）
        """
        try:
            # 创建子进程
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=None,  # 不捕获输出
                stderr=None,
                cwd=workdir
            )

            logger.info(f"[Exec] 命令已启动（后台）: pid={process.pid}")

            # 立即返回
            return (
                0,
                f"命令已在后台启动 (PID: {process.pid})",
                ""
            )

        except Exception as e:
            logger.error(f"[Exec] 后台启动失败: {e}")
            return -1, "", str(e)

    def sync_execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        background: bool = False,
        capture_output: bool = True,
        workdir: Optional[str] = None
    ) -> Tuple[int, str, str]:
        """
        同步版本

        用于不支持async的场景
        """
        return asyncio.run(
            self.execute(command, timeout, background, capture_output, workdir)
        )


# 便捷函数
async def execute(
    command: str,
    timeout: int = 30,
    background: bool = False,
    capture_output: bool = True,
    workdir: Optional[str] = None
) -> Tuple[int, str, str]:
    """
    execute便捷函数

    Args:
        command: 要执行的命令
        timeout: 超时时间
        background: 是否后台运行
        capture_output: 是否捕获输出
        workdir: 工作目录

    Returns:
        (exit_code, stdout, stderr)
    """
    tool = ExecTool(default_timeout=timeout, workdir=workdir)
    return await tool.execute(command, timeout, background, capture_output, workdir)


# 快捷函数（同步）
def exec_sync(
    command: str,
    timeout: int = 30,
    background: bool = False,
    workdir: Optional[str] = None
) -> Tuple[int, str, str]:
    """
    同步快捷函数

    类似于subprocess.run，但更强大
    """
    tool = ExecTool(default_timeout=timeout, workdir=workdir)
    return tool.sync_execute(command, timeout, background, capture_output=True, workdir=workdir)


# 测试
if __name__ == "__main__":
    import sys

    # 设置Unicode输出（Windows）
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    async def test():
        print("\n" + "="*70)
        print("自主Exec测试")
        print("="*70 + "\n")

        # 测试1：简单命令
        print("[测试1] 执行简单命令")
        exit_code, stdout, stderr = await execute("echo Hello World")
        print(f"Exit Code: {exit_code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")

        # 测试2：获取目录列表
        print("\n[测试2] 获取目录列表")
        exit_code, stdout, stderr = await execute("dir")
        print(f"Exit Code: {exit_code}")
        print(f"Stdout (前100字符): {stdout[:100]}")
        print(f"Stderr: {stderr}")

        # 测试3：后台启动
        print("\n[测试3] 后台启动命令")
        exit_code, stdout, stderr = await execute("timeout /t 2 > nul", background=True)
        print(f"Exit Code: {exit_code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")

        print("\n" + "="*70)
        print("测试完成")
        print("="*70 + "\n")

    asyncio.run(test())
