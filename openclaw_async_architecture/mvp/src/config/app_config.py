"""
Configuration System
====================

Configuration management with hot-reload support.
"""
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import json
import yaml
from pydantic import BaseModel, Field, validator

# Default configuration
DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 3000
    },
    "plugins": {
        "directory": "./plugins",
        "enabled": ["*"]
    },
    "middleware": {
        "config_file": "./middleware_config.yaml",
        "hot_reload": True
    },
    "redis": {
        "host": "localhost",
        "port": 6379,
        "db": 0
    }
}


class ServerConfig(BaseModel):
    """Server configuration"""
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=3000, ge=1, le=65535, description="Server port")

    @validator('port')
    def validate_port(cls, v):
        if v < 1 or v > 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v


class PluginsConfig(BaseModel):
    """Plugin configuration"""
    directory: str = Field(default="./plugins", description="Plugin directory")
    enabled: list = Field(default_factory=lambda: ["*"], description="Enabled plugins")


class MiddlewareConfig(BaseModel):
    """Middleware configuration"""
    config_file: str = Field(default="./middleware_config.yaml", description="Middleware config file")
    hot_reload: bool = Field(default=True, description="Enable hot reload")


class RedisConfig(BaseModel):
    """Redis configuration"""
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    db: int = Field(default=0, ge=0, le=15, description="Redis database")


class AppConfig(BaseModel):
    """Application configuration"""
    server: ServerConfig = Field(default_factory=ServerConfig)
    plugins: PluginsConfig = Field(default_factory=PluginsConfig)
    middleware: MiddlewareConfig = Field(default_factory=MiddlewareConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)

    class Config:
        # Allow extra fields for extensibility
        extra = "allow"

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'AppConfig':
        """
        Create AppConfig from dict.

        Args:
            config: Configuration dict

        Returns:
            AppConfig instance
        """
        # Flatten nested config (e.g., server.host -> server.host)
        # Pydantic will handle nested structure
        return cls(**config)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert AppConfig to dict.

        Returns:
            Configuration dict
        """
        return self.dict()

    def merge(self, other: Dict[str, Any]) -> 'AppConfig':
        """
        Merge another config into this one.

        Args:
            other: Other config dict

        Returns:
            Merged AppConfig
        """
        current_dict = self.to_dict()

        def deep_merge(base: dict, update: dict) -> dict:
            """Deep merge two dicts"""
            result = base.copy()
            for key, value in update.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        merged_dict = deep_merge(current_dict, other)
        return self.from_dict(merged_dict)
