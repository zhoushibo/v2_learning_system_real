"""
Executor Integration - V2 MVP执行系统集成
"""

import sys
import asyncio
import logging
import subprocess
from typing import Dict, Any, Optional

# 添加V2 MVP路径
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'openclaw_async_architecture' / 'mvp'))
    from src.tools.exec_self import ExecSelfTool
    V2_EXECUTOR_AVAILABLE = True
except Exception as e:
    logging.warning(f"V2 Executor not available: {e}")
    V2_EXECUTOR_AVAILABLE = False

# 提前导入Step类（避免相对导入问题）
from workflow.engine import Step

logger = logging.getLogger(__name__)


class ExecutorIntegration:
    """
    V2 MVP执行系统集成
    将V2 MVP的执行工具封装为工作流步骤
    """

    def __init__(self, use_mock: bool = False):
        """
        初始化V2执行系统集成

        Args:
            use_mock: 是否使用模拟结果
        """
        self.use_mock = use_mock
        self.exec_tool = None

        if not use_mock and V2_EXECUTOR_AVAILABLE:
            try:
                self.exec_tool = ExecSelfTool()
                logger.info("V2 Executor initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize V2 Executor: {e}")
                self.use_mock = True
        else:
            logger.info("Using mock executor integration")
            self.use_mock = True

    async def execute_command(
        self,
        command: str,
        timeout: int = 30,
        background: bool = False,
        pty: bool = True
    ) -> Dict[str, Any]:
        """
        执行命令

        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            background: 是否后台运行
            pty: 是否使用PTY模式

        Returns:
            执行结果
        """
        if self.use_mock or self.exec_tool is None:
            return await self._execute_mock(command, timeout, background, pty)

        logger.info(f"Executing command: {command}")

        try:
            # 如果启用了PTY模式，使用前台执行
            if pty and not background:
                result = await self._execute_sync(command, timeout)
                return {
                    'status': 'success',
                    'command': command,
                    'output': result,
                    'timeout': timeout,
                    'mode': 'foreground-pty'
                }
            else:
                # 后台执行
                # TODO: 实现后台执行
                logger.warning("Background mode not fully implemented, using foreground")
                result = await self._execute_sync(command, timeout)
                return {
                    'status': 'success',
                    'command': command,
                    'output': result,
                    'timeout': timeout,
                    'mode': 'foreground'
                }
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return await self._execute_mock(command, timeout, background, pty)

    async def _execute_sync(self, command: str, timeout: int) -> str:
        """
        同步执行命令（使用subprocess）

        Args:
            command: 要执行的命令
            timeout: 超时时间

        Returns:
            输出内容
        """
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            output = stdout.decode('utf-8', errors='replace')
            if stderr:
                output += stderr.decode('utf-8', errors='replace')

            return output
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise TimeoutError(f"Command timed out after {timeout}s")

    async def _execute_mock(
        self,
        command: str,
        timeout: int,
        background: bool,
        pty: bool
    ) -> Dict[str, Any]:
        """
        模拟执行命令

        Args:
            command: 要执行的命令
            timeout: 超时时间
            background: 是否后台运行
            pty: 是否使用PTY

        Returns:
            模拟执行结果
        """
        logger.warning(f"Using mock execution for: {command}")

        # 模拟执行延迟
        await asyncio.sleep(0.5)

        # 返回模拟结果
        return {
            'status': 'success',
            'command': command,
            'mock': True,
            'output': f"Mock output for: {command}\nExecution completed in {timeout}s",
            'timeout': timeout,
            'mode': 'foreground-mock'
        }

    def create_execution_step(
        self,
        command: str,
        timeout: int = 30,
        background: bool = False,
        pty: bool = True
    ):
        """
        创建执行步骤

        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            background: 是否后台运行
            pty: 是否使用PTY模式

        Returns:
            Step: 工作流步骤
        """
        def execution_function(context: Dict[str, Any]):
            return self.execute_command(command, timeout, background, pty)

        return Step(
            name=f"execute_{command.replace(' ', '_').replace('/', '_')[:20]}",
            function=execution_function,
            enabled=True,
            timeout=timeout + 10,  # 步骤超时比命令超时长一点
            metadata={
                'type': 'execution',
                'command': command
            }
        )


# 修复 Path 导入
from pathlib import Path
