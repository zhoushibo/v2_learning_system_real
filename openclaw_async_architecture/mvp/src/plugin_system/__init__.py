"""
Plugin System
=============

Dynamic plugin loading system for tool extensibility.

Components:
- plugin_metadata: Metadata schemas (Pydantic models)
- plugin_registry: Metadata registration and tool discovery
- plugin_loader: Dynamic loading/unloading of Python plugins
- plugin_runtime: Sandboxed execution with permission checks

Usage:
    from src.plugin_system import PluginLoader, SandboxedRuntime, get_registry

    # Load plugins
    loader = PluginLoader(plugin_dir=Path("./plugins"))
    loader.discover_and_load_all()

    # Execute tool
    runtime = SandboxedRuntime()
    tool_class = loader.get_tool_class("hello_world")
    tool = tool_class()
    ctx = runtime.execute_tool(tool, "hello_world", {"name": "World"})

    print(ctx.result)
"""

from .plugin_metadata import (
    Permission,
    ParameterSchema,
    ToolMetadata,
    PluginMetadata,
    EXAMPLE_PLUGIN_METADATA,
)
from .plugin_registry import PluginRegistry, get_registry
from .plugin_loader import PluginLoader
from .plugin_runtime import (
    PermissionDeniedError,
    ToolExecutionContext,
    SandboxedRuntime,
    BaseTool,
)

__all__ = [
    # Metadata
    "Permission",
    "ParameterSchema",
    "ToolMetadata",
    "PluginMetadata",
    "EXAMPLE_PLUGIN_METADATA",
    # Registry
    "PluginRegistry",
    "get_registry",
    # Loader
    "PluginLoader",
    # Runtime
    "PermissionDeniedError",
    "ToolExecutionContext",
    "SandboxedRuntime",
    "BaseTool",
]

__version__ = "1.0.0"
