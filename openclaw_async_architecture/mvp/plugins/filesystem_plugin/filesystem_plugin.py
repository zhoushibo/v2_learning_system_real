"""
File System Plugin
===================

文件系统工具插件（集成现有 FileSystemTools）
"""
import asyncio
import sys
from pathlib import Path
from typing import List

# 添加 src 到路径以导入 Worker 工具
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from plugin_system import BaseTool, ParameterSchema
from worker.tools.tool_plugin_wrapper import ToolPluginWrapper
from worker.tools.filesystem_tools import FileSystemTools


class FileSystemPlugin:
    """文件系统插件"""

    def __init__(self):
        self.name = "filesystem_plugin"
        self.version = "1.0.0"
        self.description = "文件系统工具（异步I/O优化）"

        # 获取所有 Worker 工具
        worker_tools = FileSystemTools.get_tools()

        # 包装为插件工具
        self.plugin_tools = [
            ToolPluginWrapper(worker_tool) for worker_tool in worker_tools
        ]

    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        """根据名称获取工具"""
        for tool in self.plugin_tools:
            if tool.name == name:
                return tool
        return None

    def get_all_tools(self) -> List[BaseTool]:
        """获取所有工具"""
        return self.plugin_tools


# 创建插件实例（插件加载器使用）
_plugin_instance = None


def get_plugin():
    """获取插件实例（单例）"""
    global _plugin_instance
    if _plugin_instance is None:
        _plugin_instance = FileSystemPlugin()
    return _plugin_instance


# 导出工具类（插件加载器使用）
class ReadFileTool(BaseTool):
    """读取文件工具"""

    def __init__(self):
        super().__init__(
            name="read_file",
            description="读取文件内容（异步I/O）"
        )

    async def execute(self, path: str) -> str:
        """执行读取文件"""
        plugin = get_plugin()
        tool = plugin.get_tool_by_name("read_file")
        if tool:
            return await tool.execute(path=path)
        raise Exception("Tool not found")

    def get_schema(self):
        return [
            ParameterSchema(
                name="path",
                type="string",
                required=True,
                description="文件路径"
            )
        ]


class WriteFileTool(BaseTool):
    """写入文件工具"""

    def __init__(self):
        super().__init__(
            name="write_file",
            description="写入文件内容（异步I/O）"
        )

    async def execute(self, path: str, content: str) -> dict:
        """执行写入文件"""
        plugin = get_plugin()
        tool = plugin.get_tool_by_name("write_file")
        if tool:
            return await tool.execute(path=path, content=content)
        raise Exception("Tool not found")

    def get_schema(self):
        return [
            ParameterSchema(
                name="path",
                type="string",
                required=True,
                description="文件路径"
            ),
            ParameterSchema(
                name="content",
                type="string",
                required=True,
                description="文件内容"
            )
        ]


class ListDirectoryTool(BaseTool):
    """列出目录工具"""

    def __init__(self):
        super().__init__(
            name="list_directory",
            description="列出目录内容（异步I/O）"
        )

    async def execute(self, path: str) -> list:
        """执行列出目录"""
        plugin = get_plugin()
        tool = plugin.get_tool_by_name("list_directory")
        if tool:
            return await tool.execute(path=path)
        raise Exception("Tool not found")

    def get_schema(self):
        return [
            ParameterSchema(
                name="path",
                type="string",
                required=True,
                description="目录路径"
            )
        ]


class CreateDirectoryTool(BaseTool):
    """创建目录工具"""

    def __init__(self):
        super().__init__(
            name="create_directory",
            description="创建目录（递归）"
        )

    async def execute(self, path: str) -> dict:
        """执行创建目录"""
        plugin = get_plugin()
        tool = plugin.get_tool_by_name("create_directory")
        if tool:
            return await tool.execute(path=path)
        raise Exception("Tool not found")

    def get_schema(self):
        return [
            ParameterSchema(
                name="path",
                type="string",
                required=True,
                description="目录路径"
            )
        ]
