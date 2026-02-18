"""
Plugin Loader
=============

Dynamically loads and unloads plugins.
"""
from typing import Optional, Dict, Any
from pathlib import Path
import importlib.util
import sys

from .plugin_metadata import PluginMetadata
from .plugin_registry import get_registry


class PluginLoader:
    """Dynamically loads and unloads Python plugins"""

    def __init__(self, plugin_dir: Path):
        """
        Initialize plugin loader.

        Args:
            plugin_dir: Directory containing plugins
        """
        self.plugin_dir = Path(plugin_dir)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        self._loaded_plugins: Dict[str, Any] = {}  # plugin_name -> module
        self._plugin_classes: Dict[str, Any] = {}  # plugin_name -> plugin class
        self._tool_classes: Dict[str, Any] = {}   # tool_name -> tool class

    def load_plugin(self, metadata: PluginMetadata) -> bool:
        """
        Load a plugin by metadata.

        Args:
            metadata: Plugin metadata

        Returns:
            True if loaded successfully, False otherwise
        """
        plugin_name = metadata.name

        # Already loaded?
        if plugin_name in self._loaded_plugins:
            return True

        try:
            # Parse entry point (module:Class)
            module_name, class_name = metadata.entry_point.split(':')

            # Construct module path
            # Support both: plugin_dir/{plugin_name}.py and plugin_dir/{plugin_name}/{module_name}.py
            module_path1 = self.plugin_dir / f"{module_name}.py"
            module_path2 = self.plugin_dir / module_name / f"{module_name}.py"

            if module_path1.exists():
                module_path = module_path1
            elif module_path2.exists():
                module_path = module_path2
            else:
                raise FileNotFoundError(f"Plugin file not found: {module_path1} or {module_path2}")

            # Load module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Failed to load spec for {module_name}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)

            # Get plugin class
            plugin_class = getattr(module, class_name)
            self._plugin_classes[plugin_name] = plugin_class
            self._loaded_plugins[plugin_name] = module

            # Get tool classes
            for tool_meta in metadata.tools:
                _, tool_class_name = tool_meta.entry_point.split(':')
                tool_class = getattr(module, tool_class_name)
                self._tool_classes[tool_meta.name] = tool_class

            # Register metadata
            registry = get_registry()
            registry.register_plugin(metadata)

            print(f"[PluginLoader] Loaded plugin: {plugin_name}")
            return True

        except Exception as e:
            print(f"[PluginLoader] Failed to load plugin {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            True if unloaded successfully, False otherwise
        """
        if plugin_name not in self._loaded_plugins:
            return False

        try:
            # Remove from loaded plugins
            del self._loaded_plugins[plugin_name]
            del self._plugin_classes[plugin_name]

            # Remove tool classes
            registry = get_registry()
            metadata = registry.get_plugin(plugin_name)
            if metadata:
                for tool in metadata.tools:
                    if tool.name in self._tool_classes:
                        del self._tool_classes[tool.name]

            # Unregister metadata
            registry.unregister_plugin(plugin_name)

            # Remove from sys.modules
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]

            print(f"[PluginLoader] Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            print(f"[PluginLoader] Failed to unload plugin {plugin_name}: {e}")
            return False

    def get_plugin_class(self, plugin_name: str) -> Optional[Any]:
        """Get plugin class by name"""
        return self._plugin_classes.get(plugin_name)

    def get_tool_class(self, tool_name: str) -> Optional[Any]:
        """Get tool class by name"""
        return self._tool_classes.get(tool_name)

    def list_loaded_plugins(self) -> list:
        """List loaded plugin names"""
        return list(self._loaded_plugins.keys())

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin (unload and load).

        Args:
            plugin_name: Plugin name

        Returns:
            True if reloaded successfully, False otherwise
        """
        if plugin_name in self._loaded_plugins:
            # Get metadata
            registry = get_registry()
            metadata = registry.get_plugin(plugin_name)
            if not metadata:
                return False

            # Unload
            self.unload_plugin(plugin_name)

            # Load
            return self.load_plugin(metadata)

        return False

    def discover_and_load_all(self) -> int:
        """
        Discover all plugins in plugin directory and load them.

        Returns:
            Number of plugins loaded
        """
        loaded = 0

        # Find all metadata.json files
        for metadata_file in self.plugin_dir.glob("*/metadata.json"):
            try:
                # Load metadata
                registry = get_registry()
                if registry.load_from_file(metadata_file):
                    metadata = registry.get_plugin(metadata_file.parent.name)
                    if metadata and self.load_plugin(metadata):
                        loaded += 1
            except Exception as e:
                print(f"[PluginLoader] Failed to load plugin from {metadata_file}: {e}")

        print(f"[PluginLoader] Discovered and loaded {loaded} plugins")
        return loaded
