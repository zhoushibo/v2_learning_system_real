"""
Configuration Loader
====================

Load configuration from YAML/JSON files with validation.
"""
from typing import Optional, Dict, Any
from pathlib import Path
import json
import yaml

from .app_config import AppConfig, DEFAULT_CONFIG


class ConfigLoader:
    """Load and validate configuration from files"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize config loader.

        Args:
            config_dir: Directory containing config files (default: ./config)
        """
        self.config_dir = Path(config_dir) if config_dir else Path("./config")
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._current_config: Optional[AppConfig] = None
        self._config_file: Optional[Path] = None

    def load(
        self,
        config_path: Optional[Path] = None,
        config_dict: Optional[Dict[str, Any]] = None
    ) -> AppConfig:
        """
        Load configuration from file or dict.

        Args:
            config_path: Path to config file (YAML/JSON)
            config_dict: Configuration dict (takes precedence over file)

        Returns:
            AppConfig instance

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config is invalid
        """
        if config_dict is not None:
            # Load from dict
            try:
                config = AppConfig.from_dict(config_dict)
                self._current_config = config
                self._config_file = None
                return config
            except Exception as e:
                raise ValueError(f"Invalid config dict: {e}")

        if config_path is None:
            # Try to find default config files
            config_path = self._find_default_config()

        if config_path is None or not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path or 'no default config found'}")

        # Load from file
        return self._load_from_file(config_path)

    def _find_default_config(self) -> Optional[Path]:
        """Find default config file"""
        # Try common config file names
        config_names = [
            "config.yaml",
            "config.yml",
            "config.json",
            "app_config.yaml",
            "app_config.yml",
            "app_config.json",
        ]

        for name in config_names:
            config_path = self.config_dir / name
            if config_path.exists():
                return config_path

        return None

    def _load_from_file(self, config_path: Path) -> AppConfig:
        """
        Load configuration from file.

        Args:
            config_path: Path to config file

        Returns:
            AppConfig instance

        Raises:
            ValueError: If config is invalid
        """
        suffix = config_path.suffix.lower()

        with open(config_path, 'r', encoding='utf-8') as f:
            if suffix in ['.json']:
                config_dict = json.load(f)
            elif suffix in ['.yaml', '.yml']:
                config_dict = yaml.safe_load(f) or {}
            else:
                raise ValueError(f"Unsupported config file format: {suffix}")

        # Merge with defaults
        merged_dict = self._merge_with_defaults(config_dict)

        # Validate and create AppConfig
        try:
            config = AppConfig.from_dict(merged_dict)
            self._current_config = config
            self._config_file = config_path
            return config
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")

    def _merge_with_defaults(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge config with defaults.

        Args:
            config_dict: User config dict

        Returns:
            Merged config dict
        """
        def deep_merge(base: dict, update: dict) -> dict:
            """Deep merge two dicts"""
            result = base.copy()
            for key, value in update.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        return deep_merge(DEFAULT_CONFIG.copy(), config_dict)

    def save(
        self,
        config: AppConfig,
        config_path: Optional[Path] = None
    ) -> bool:
        """
        Save configuration to file.

        Args:
            config: AppConfig instance
            config_path: Path to save config (default: config/config.yaml)

        Returns:
            True if saved successfully

        Raises:
            ValueError: If save fails
        """
        if config_path is None:
            config_path = self.config_dir / "config.yaml"

        config_dict = config.to_dict()

        suffix = config_path.suffix.lower()

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if suffix in ['.json']:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                elif suffix in ['.yaml', '.yml']:
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
                else:
                    # Default to YAML
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)

            return True

        except Exception as e:
            raise ValueError(f"Failed to save config: {e}")

    def get_current_config(self) -> Optional[AppConfig]:
        """Get current loaded config"""
        return self._current_config

    def get_config_file(self) -> Optional[Path]:
        """Get current config file path"""
        return self._config_file

    def create_default_config(self, config_path: Optional[Path] = None) -> Path:
        """
        Create a default config file.

        Args:
            config_path: Path to save config (default: config/config.yaml)

        Returns:
            Path to created config file
        """
        if config_path is None:
            config_path = self.config_dir / "config.yaml"

        default_config = AppConfig.from_dict(DEFAULT_CONFIG)
        self.save(default_config, config_path)

        return config_path
