"""
Configuration System
====================

Configuration management with hot-reload support.

Components:
- app_config: Pydantic configuration models
- config_loader: Load/save configuration from YAML/JSON
- hot_reload: Hot reload service using watchdog

Usage:
    from src.config import ConfigLoader, HotReloadService

    # Load configuration
    loader = ConfigLoader()
    config = loader.load(config_path="config/config.yaml")

    # Start hot reload
    hot_reload = HotReloadService(loader, debounce_seconds=5.0)
    hot_reload.start()

    # Get current config
    print(config.server.host, config.server.port)
"""

from .app_config import (
    AppConfig,
    ServerConfig,
    PluginsConfig,
    MiddlewareConfig,
    RedisConfig,
    DEFAULT_CONFIG,
)
from .config_loader import ConfigLoader
from .hot_reload import HotReloadService

__all__ = [
    # Config models
    "AppConfig",
    "ServerConfig",
    "PluginsConfig",
    "MiddlewareConfig",
    "RedisConfig",
    "DEFAULT_CONFIG",
    # Components
    "ConfigLoader",
    "HotReloadService",
]

__version__ = "1.0.0"
