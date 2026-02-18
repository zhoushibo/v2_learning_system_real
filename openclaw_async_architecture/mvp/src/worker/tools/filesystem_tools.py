# -*- coding: utf-8 -*-
"""文件系统工具 - Phase 2异步优化版"""

import os
import asyncio
import aiofiles
from typing import Optional
from .base_tool import BaseTool, ToolInput, ToolOutput


class ReadFileInput(ToolInput):
    """读取文件输入"""
    path: str


class WriteFileInput(ToolInput):
    """写入文件输入"""
    path: str
    content: str


class ListDirectoryInput(ToolInput):
    """列出目录输入"""
    path: str


class CreateDirectoryInput(ToolInput):
    """创建目录输入"""
    path: str


class FileSystemTools:
    """文件系统工具集（异步I/O优化版）"""

    @staticmethod
    def get_tools():
        """获取所有文件系统工具"""
        return [
            ReadFileTool(),
            WriteFileTool(),
            ListDirectoryTool(),
            CreateDirectoryTool()
        ]


class ReadFileTool(BaseTool):
    """读取文件工具（异步I/O）"""

    name = "read_file"
    description = "读取文件内容（异步）"
    input_schema = ReadFileInput

    async def execute(self, input_data: ReadFileInput) -> ToolOutput:
        """
        读取文件内容（使用aiofiles异步I/O）

        Args:
            input_data: 文件路径

        Returns:
            ToolOutput: 文件内容
        """
        try:
            # 使用aiofiles异步读取
            async with aiofiles.open(input_data.path, mode='r', encoding='utf-8') as f:
                content = await f.read()

            return ToolOutput(
                success=True,
                result=content,
                metadata={
                    "path": input_data.path,
                    "size": len(content),
                    "encoding": "utf-8"
                }
            )
        except FileNotFoundError:
            return ToolOutput(
                success=False,
                error=f"文件不存在: {input_data.path}",
                metadata={"path": input_data.path}
            )
        except PermissionError:
            return ToolOutput(
                success=False,
                error=f"无读取权限: {input_data.path}",
                metadata={"path": input_data.path}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"读取文件失败: {str(e)}",
                metadata={"path": input_data.path}
            )


class WriteFileTool(BaseTool):
    """写入文件工具（异步I/O）"""

    name = "write_file"
    description = "写入文件内容（异步）"
    input_schema = WriteFileInput

    async def execute(self, input_data: WriteFileInput) -> ToolOutput:
        """
        写入文件内容（使用aiofiles异步I/O）

        Args:
            input_data: 文件路径和内容

        Returns:
            ToolOutput: 写入结果
        """
        try:
            # 创建父目录（同步操作）
            dir_path = os.path.dirname(input_data.path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            # 使用aiofiles异步写入
            async with aiofiles.open(input_data.path, mode='w', encoding='utf-8') as f:
                await f.write(input_data.content)

            return ToolOutput(
                success=True,
                result=f"文件已写入: {input_data.path}",
                metadata={
                    "path": input_data.path,
                    "size": len(input_data.content)
                }
            )
        except PermissionError:
            return ToolOutput(
                success=False,
                error=f"无写入权限: {input_data.path}",
                metadata={"path": input_data.path}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"写入文件失败: {str(e)}",
                metadata={"path": input_data.path}
            )


class ListDirectoryTool(BaseTool):
    """列出目录工具（异步I/O）"""

    name = "list_directory"
    description = "列出目录内容（异步）"
    input_schema = ListDirectoryInput

    async def execute(self, input_data: ListDirectoryInput) -> ToolOutput:
        """
        列出目录内容（使用asyncio异步遍历）

        Args:
            input_data: 目录路径

        Returns:
            ToolOutput: 目录列表
        """
        try:
            # 使用asyncio.to_thread包装同步操作
            loop = asyncio.get_event_loop()

            def list_dir():
                if not os.path.exists(input_data.path):
                    raise FileNotFoundError(f"目录不存在: {input_data.path}")
                if not os.path.isdir(input_data.path):
                    raise NotADirectoryError(f"不是目录: {input_data.path}")

                entries = []
                for entry in os.listdir(input_data.path):
                    entry_path = os.path.join(input_data.path, entry)
                    try:
                        stat = os.stat(entry_path)
                        entries.append({
                            "name": entry,
                            "type": "dir" if os.path.isdir(entry_path) else "file",
                            "size": stat.st_size if os.path.isfile(entry_path) else 0,
                            "modified": stat.st_mtime
                        })
                    except OSError:
                        entries.append({
                            "name": entry,
                            "type": "unknown",
                            "size": 0,
                            "modified": 0
                        })
                return sorted(entries, key=lambda x: x["name"])

            entries = await loop.run_in_executor(None, list_dir)

            return ToolOutput(
                success=True,
                result=entries,
                metadata={
                    "path": input_data.path,
                    "count": len(entries)
                }
            )
        except FileNotFoundError as e:
            return ToolOutput(
                success=False,
                error=str(e),
                metadata={"path": input_data.path}
            )
        except NotADirectoryError as e:
            return ToolOutput(
                success=False,
                error=str(e),
                metadata={"path": input_data.path}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"列出目录失败: {str(e)}",
                metadata={"path": input_data.path}
            )


class CreateDirectoryTool(BaseTool):
    """创建目录工具（异步I/O）"""

    name = "create_directory"
    description = "创建目录（异步）"
    input_schema = CreateDirectoryInput

    async def execute(self, input_data: CreateDirectoryInput) -> ToolOutput:
        """
        创建目录（使用asyncio异步执行）

        Args:
            input_data: 目录路径

        Returns:
            ToolOutput: 创建结果
        """
        try:
            # 使用asyncio.to_thread包装同步操作
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, os.makedirs, input_data.path, True)

            return ToolOutput(
                success=True,
                result=f"目录已创建: {input_data.path}",
                metadata={"path": input_data.path}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"创建目录失败: {str(e)}",
                metadata={"path": input_data.path}
            )
