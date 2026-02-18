"""
Middleware Config Loader
========================

Load middleware configuration from YAML/JSON files.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import yaml

from .middleware_chain import MiddlewareChain
from .builtin_middlewares import LoggingMiddleware, MonitoringMiddleware, RateLimitMiddleware
from .cache_middleware import CacheMiddleware


class MiddlewareConfigLoader:
    """Load and apply middleware configuration"""

    # Middleware class registry
    MIDDLEWARE_CLASSES = {
        "logging": LoggingMiddleware,
        "monitoring": MonitoringMiddleware,
        "rate_limit": RateLimitMiddleware,
        "cache": CacheMiddleware,
    }

    @classmethod
    def register_middleware_class(cls, name: str, middleware_class: type):
        """Register a custom middleware class"""
        cls.MIDDLEWARE_CLASSES[name] = middleware_class

    @classmethod
    def load_from_dict(cls, config: Dict[str, Any]) -> MiddlewareChain:
        """
        Load middleware chain from dict config.

        Args:
            config: Configuration dict

        Returns:
            MiddlewareChain instance
        """
        chain = MiddlewareChain()

        middlewares = config.get("middlewares", [])
        for mw_config in middlewares:
            middleware = cls._create_middleware(mw_config)
            if middleware:
                chain.add_middleware(middleware)

        return chain

    @classmethod
    def load_from_file(cls, config_path: Path) -> MiddlewareChain:
        """
        Load middleware chain from config file.

        Args:
            config_path: Path to config file (JSON or YAML)

        Returns:
            MiddlewareChain instance
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        suffix = config_path.suffix.lower()

        with open(config_path, 'r', encoding='utf-8') as f:
            if suffix in ['.json']:
                config = json.load(f)
            elif suffix in ['.yaml', '.yml']:
                config = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config file format: {suffix}")

        return cls.load_from_dict(config)

    @classmethod
    def _create_middleware(cls, config: Dict[str, Any]) -> Optional['BaseMiddleware']:
        """
        Create middleware instance from config.

        Args:
            config: Middleware config dict

        Returns:
            Middleware instance or None
        """
        # Get middleware type
        middleware_type = config.get("type")
        if not middleware_type:
            print(f"[ConfigLoader] Missing 'type' in middleware config: {config}")
            return None

        # Get middleware class
        middleware_class = cls.MIDDLEWARE_CLASSES.get(middleware_type)
        if not middleware_class:
            print(f"[ConfigLoader] Unknown middleware type: {middleware_type}")
            return None

        # Extract parameters
        params = {
            "name": config.get("name", middleware_type),
            "enabled": config.get("enabled", True),
        }

        # Add type-specific parameters
        if middleware_type == "rate_limit":
            params["max_requests"] = config.get("max_requests", 100)
            params["window_seconds"] = config.get("window_seconds", 60)
        elif middleware_type == "cache":
            params["ttl"] = config.get("ttl", 3600)
            params["cache_key_prefix"] = config.get("cache_key_prefix", "tool_cache")
        elif middleware_type == "logging":
            params["log_level"] = config.get("log_level", "INFO")
            params["include_params"] = config.get("include_params", True)

        # Create instance
        try:
            middleware = middleware_class(**params)

            # Set priority if specified
            priority = config.get("priority")
            if priority is not None:
                middleware.priority = priority

            return middleware

        except Exception as e:
            print(f"[ConfigLoader] Failed to create middleware {middleware_type}: {e}")
            return None

    @classmethod
    def save_example_config(cls, config_path: Path):
        """
        Save an example config file.

        Args:
            config_path: Path to save config file
        """
        example_config = {
            "middlewares": [
                {
                    "type": "logging",
                    "name": "logging",
                    "enabled": True,
                    "priority": 10,
                    "log_level": "INFO",
                    "include_params": True
                },
                {
                    "type": "monitoring",
                    "name": "monitoring",
                    "enabled": True,
                    "priority": 20
                },
                {
                    "type": "cache",
                    "name": "cache",
                    "enabled": True,
                    "priority": 5,
                    "ttl": 3600,
                    "cache_key_prefix": "tool_cache"
                },
                {
                    "type": "rate_limit",
                    "name": "rate_limit",
                    "enabled": True,
                    "priority": 30,
                    "max_requests": 100,
                    "window_seconds": 60
                }
            ]
        }

        suffix = config_path.suffix.lower()

        with open(config_path, 'w', encoding='utf-8') as f:
            if suffix in ['.json']:
                json.dump(example_config, f, indent=2, ensure_ascii=False)
            elif suffix in ['.yaml', '.yml']:
                yaml.dump(example_config, f, default_flow_style=False, allow_unicode=True)

        print(f"[ConfigLoader] Example config saved to {config_path}")
