"""
Tool Plugin Wrapper
====================

将现有 BaseTool 包装为插件系统兼容的工具。
"""
from typing import Dict, Any, Optional
from pathlib import Path

from plugin_system import BaseTool as PluginBaseTool, ParameterSchema
from ..base_tool import BaseTool as WorkerBaseTool, ToolInput, ToolOutput


class ToolPluginWrapper(PluginBaseTool):
    """
    将 Worker 工具包装为插件工具。

    适配器模式：适配 WorkerBaseTool 接口到 PluginBaseTool 接口
    """

    def __init__(self, worker_tool: WorkerBaseTool):
        """
        初始化包装器。

        Args:
            worker_tool: Worker 工具实例
        """
        super().__init__(
            name=worker_tool.name,
            description=worker_tool.description
        )

        self._worker_tool = worker_tool

    async def execute(self, **kwargs) -> Any:
        """
        执行工具（适配插件接口）

        Args:
            **kwargs: 工具参数

        Returns:
            工具执行结果
        """
        # 将 kwargs 转换为 ToolInput
        input_data = self._worker_tool.input_schema(**kwargs)

        # 调用 Worker 工具
        output: ToolOutput = await self._worker_tool.execute(input_data)

        # 返回结果
        if output.success:
            return output.data
        else:
            raise Exception(output.error or "Unknown error")

    def get_schema(self) -> list:
        """
        获取参数 schema（适配插件接口）

        Returns:
            参数 schema 列表
        """
        schema = self._worker_tool.input_schema.schema()
        parameters = []

        if "properties" in schema:
            for param_name, param_info in schema["properties"].items():
                param_schema = ParameterSchema(
                    name=param_name,
                    type=self._map_param_type(param_info),
                    required=param_name in schema.get("required", []),
                    default=param_info.get("default"),
                    description=param_info.get("description", "")
                )
                parameters.append(param_schema)

        return parameters

    def _map_param_type(self, param_info: Dict[str, Any]) -> str:
        """
        映射参数类型到插件类型。

        Args:
            param_info: 参数信息

        Returns:
            插件类型字符串
        """
        param_type = param_info.get("type", "string")

        type_map = {
            "string": "string",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": "list",
            "object": "dict",
        }

        return type_map.get(param_type, "string")
