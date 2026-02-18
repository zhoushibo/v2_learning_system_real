"""
Plugin Registry
===============

Manages plugin metadata registration and tool discovery.
"""
from typing import Dict, List, Optional
from pathlib import Path
import json

from .plugin_metadata import PluginMetadata, ToolMetadata, Permission


class PluginRegistry:
    """Registry for plugin metadata and tools"""

    def __init__(self):
        self._plugins: Dict[str, PluginMetadata] = {}
        self._tools: Dict[str, ToolMetadata] = {}
        self._tool_to_plugin: Dict[str, str] = {}  # tool name -> plugin name

    def register_plugin(self, metadata: PluginMetadata) -> bool:
        """
        Register a plugin with its metadata.

        Args:
            metadata: Plugin metadata

        Returns:
            True if registered successfully, False if plugin already exists
        """
        plugin_name = metadata.name

        if plugin_name in self._plugins:
            return False

        # Register plugin
        self._plugins[plugin_name] = metadata

        # Register tools
        for tool in metadata.tools:
            if tool.name in self._tools:
                # Tool already exists, skip
                continue
            self._tools[tool.name] = tool
            self._tool_to_plugin[tool.name] = plugin_name

        return True

    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin and its tools.

        Args:
            plugin_name: Plugin name

        Returns:
            True if unregistered successfully, False if plugin not found
        """
        if plugin_name not in self._plugins:
            return False

        plugin = self._plugins[plugin_name]

        # Unregister tools
        for tool in plugin.tools:
            if tool.name in self._tools:
                del self._tools[tool.name]
            if tool.name in self._tool_to_plugin:
                del self._tool_to_plugin[tool.name]

        # Unregister plugin
        del self._plugins[plugin_name]

        return True

    def get_plugin(self, plugin_name: str) -> Optional[PluginMetadata]:
        """Get plugin metadata by name"""
        return self._plugins.get(plugin_name)

    def get_tool(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get tool metadata by name"""
        return self._tools.get(tool_name)

    def get_plugin_for_tool(self, tool_name: str) -> Optional[str]:
        """Get plugin name that provides a tool"""
        return self._tool_to_plugin.get(tool_name)

    def list_plugins(self) -> List[str]:
        """List all registered plugin names"""
        return list(self._plugins.keys())

    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())

    def list_tools_by_category(self, category: str) -> List[str]:
        """List tools by category"""
        return [
            tool_name for tool_name, tool in self._tools.items()
            if tool.category == category
        ]

    def check_tool_permission(self, tool_name: str, required_permission: Permission) -> bool:
        """
        Check if a tool has a specific permission.

        Args:
            tool_name: Tool name
            required_permission: Required permission

        Returns:
            True if tool has permission, False otherwise
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return False

        # Check tool-level permissions
        if required_permission in tool.permissions:
            return True

        # Check plugin-level permissions
        plugin_name = self.get_plugin_for_tool(tool_name)
        if plugin_name:
            plugin = self.get_plugin(plugin_name)
            if plugin and required_permission in plugin.permissions:
                return True

        return False

    def load_from_file(self, metadata_path: Path) -> bool:
        """
        Load plugin metadata from JSON file.

        Args:
            metadata_path: Path to metadata JSON file

        Returns:
            True if loaded successfully, False otherwise
        """
        if not metadata_path.exists():
            return False

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metadata = PluginMetadata(**data)
            return self.register_plugin(metadata)

        except Exception as e:
            print(f"Failed to load metadata from {metadata_path}: {e}")
            return False

    def save_to_file(self, plugin_name: str, metadata_path: Path) -> bool:
        """
        Save plugin metadata to JSON file.

        Args:
            plugin_name: Plugin name
            metadata_path: Path to save metadata

        Returns:
            True if saved successfully, False otherwise
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return False

        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(plugin.dict(), f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Failed to save metadata to {metadata_path}: {e}")
            return False

    def clear(self):
        """Clear all registrations"""
        self._plugins.clear()
        self._tools.clear()
        self._tool_to_plugin.clear()

    @property
    def plugin_count(self) -> int:
        """Get number of registered plugins"""
        return len(self._plugins)

    @property
    def tool_count(self) -> int:
        """Get number of registered tools"""
        return len(self._tools)


# Global registry instance
_registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    """Get global plugin registry"""
    return _registry
