"""
Hot Reload Service
==================

Configuration hot reload using file system monitoring.

Note: Requires watchdog library. Falls back gracefully if not available.
"""
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import asyncio
from datetime import datetime
import traceback

# Try to import watchdog
WATCHDOG_AVAILABLE = False
ObserverClass = None
EventHandlerClass = None
FileModifiedEventClass = None

try:
    from watchdog.observers import Observer as ObserverClass
    from watchdog.events import (
        FileSystemEventHandler as EventHandlerClass,
        FileModifiedEvent as FileModifiedEventClass
    )
    WATCHDOG_AVAILABLE = True
except Exception as e:
    print(f"[HotReloadService] watchdog not available: {e}")
    print("[HotReloadService] Hot reload feature disabled")

from .config_loader import ConfigLoader
from .app_config import AppConfig


class ConfigChangeHandler:
    """Handler for config file changes"""

    def __init__(self, hot_reload_service: 'HotReloadService'):
        """
        Initialize handler.

        Args:
            hot_reload_service: Parent hot reload service
        """
        self.hot_reload_service = hot_reload_service

        # Inherit from EventHandlerClass if available
        if EventHandlerClass:
            self._handler = EventHandlerClass()
        else:
            self._handler = None

    def on_modified(self, event):
        """Called when file is modified"""
        # Skip directories
        if hasattr(event, 'is_directory') and event.is_directory:
            return

        # Get file path
        path = None
        if hasattr(event, 'src_path'):
            path = Path(event.src_path)
        elif isinstance(event, Path):
            path = event

        # Check if it's a config file
        if path and path.suffix in ['.json', '.yaml', '.yml', '.toml']:
            print(f"[ConfigChangeHandler] Config file modified: {path}")
            self.hot_reload_service._on_config_changed(path)


class HotReloadService:
    """
    Hot reload service for configuration.

    Watches config files and triggers reload on changes.
    """

    def __init__(
        self,
        loader: ConfigLoader,
        debounce_seconds: float = 5.0
    ):
        """
        Initialize hot reload service.

        Args:
            loader: Config loader instance
            debounce_seconds: Debounce time to avoid rapid reloads (default: 5s)
        """
        self.loader = loader
        self.debounce_seconds = debounce_seconds

        self._observer = None
        self._handler = None
        self._reload_task: Optional[asyncio.Task] = None
        self._is_reloading = False
        self._last_reload_time = 0.0

        # Callbacks for config changes
        self._on_reload_callbacks: list = []
        self._on_error_callbacks: list = []

        # Keep track of previous config for rollback
        self._previous_config: Optional[AppConfig] = None

    @property
    def is_available(self) -> bool:
        """Check if watchdog is available"""
        return WATCHDOG_AVAILABLE

    def start(self):
        """Start watching config files"""
        if not self.is_available:
            print("[HotReloadService] watchdog not available, cannot start")
            return False

        if self._observer is not None:
            print("[HotReloadService] Already watching")
            return False

        try:
            config_file = self.loader.get_config_file()
            if not config_file:
                print("[HotReloadService] No config file loaded, cannot watch")
                return False

            # Create observer
            self._observer = ObserverClass()

            # Create handler
            self._handler = ConfigChangeHandler(self)

            # Watch config file directory
            config_dir = str(config_file.parent)

            # Schedule the handler (watchdog API)
            if hasattr(self._observer, 'schedule'):
                self._observer.schedule(self._handler, config_dir, recursive=False)

            # Start observer
            if hasattr(self._observer, 'start'):
                self._observer.start()
                print(f"[HotReloadService] Started watching: {config_dir}")
            else:
                print("[HotReloadService] Observer not startable")
                return False

            return True

        except Exception as e:
            print(f"[HotReloadService] Failed to start: {e}")
            traceback.print_exc()
            return False

    def stop(self):
        """Stop watching config files"""
        if self._observer is None:
            return

        try:
            if hasattr(self._observer, 'stop'):
                self._observer.stop()
            if hasattr(self._observer, 'join'):
                self._observer.join(timeout=1.0)

            self._observer = None
            print("[HotReloadService] Stopped watching")
        except Exception as e:
            print(f"[HotReloadService] Failed to stop: {e}")

    def _on_config_changed(self, config_file: Path):
        """Called when config file is modified"""
        # Debounce to avoid rapid reloads
        from time import time
        now = time()

        if now - self._last_reload_time < self.debounce_seconds:
            print(f"[HotReloadService] Too soon to reload, skipping")
            return

        if self._is_reloading:
            print(f"[HotReloadService] Already reloading, skipping")
            return

        # Trigger reload
        try:
            asyncio.create_task(self._reload_config(config_file))
        except RuntimeError:
            # No event loop, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._reload_config(config_file))

    async def _reload_config(self, config_file: Path):
        """Reload configuration from file"""
        self._is_reloading = True
        from time import time
        self._last_reload_time = time()

        try:
            print(f"[HotReloadService] Reloading config from: {config_file}")

            # Keep previous config for rollback
            self._previous_config = self.loader.get_current_config()

            # Load new config
            new_config = self.loader.load(config_path=config_file)

            # Notify callbacks
            await self._notify_reload(new_config, self._previous_config)

            print(f"[HotReloadService] Config reloaded successfully")

        except Exception as e:
            error_msg = f"Failed to reload config: {e}"
            print(f"[HotReloadService] {error_msg}")
            traceback.print_exc()

            # Rollback to previous config
            if self._previous_config:
                print(f"[HotReloadService] Rolling back to previous config")
                self.loader._current_config = self._previous_config

            # Notify error callbacks
            await self._notify_error(error_msg, e)

        finally:
            self._is_reloading = False
            from time import time
            self._last_reload_time = time()

    async def _notify_reload(
        self,
        new_config: AppConfig,
        old_config: Optional[AppConfig]
    ):
        """Notify reload callbacks"""
        for callback in self._on_reload_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(new_config, old_config)
                else:
                    callback(new_config, old_config)
            except Exception as e:
                print(f"[HotReloadService] Callback error: {e}")

    async def _notify_error(self, error_msg: str, exception: Exception):
        """Notify error callbacks"""
        for callback in self._on_error_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(error_msg, exception)
                else:
                    callback(error_msg, exception)
            except Exception as e:
                print(f"[HotReloadService] Error callback error: {e}")

    def add_reload_callback(self, callback: Callable):
        """Add a callback for successful reloads"""
        self._on_reload_callbacks.append(callback)

    def add_error_callback(self, callback: Callable):
        """Add a callback for reload errors"""
        self._on_error_callbacks.append(callback)

    def remove_reload_callback(self, callback: Callable):
        """Remove a reload callback"""
        if callback in self._on_reload_callbacks:
            self._on_reload_callbacks.remove(callback)

    def remove_error_callback(self, callback: Callable):
        """Remove an error callback"""
        if callback in self._on_error_callbacks:
            self._on_error_callbacks.remove(callback)

    def trigger_manual_reload(self) -> bool:
        """
        Trigger a manual config reload.

        Returns:
            True if reload was triggered
        """
        config_file = self.loader.get_config_file()
        if not config_file:
            print("[HotReloadService] No config file loaded")
            return False

        self._on_config_changed(config_file)
        return True

    def get_previous_config(self) -> Optional[AppConfig]:
        """Get previous config (before last reload)"""
        return self._previous_config

    def rollback(self) -> bool:
        """
        Rollback to previous config.

        Returns:
            True if rollback was successful
        """
        if not self._previous_config:
            print("[HotReloadService] No previous config to rollback to")
            return False

        self.loader._current_config = self._previous_config
        print(f"[HotReloadService] Rolled back to previous config")
        return True
