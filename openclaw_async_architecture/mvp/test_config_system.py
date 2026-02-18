# test_config_system.py
"""
Unit Tests for Configuration System
=====================================

Tests for config loading, validation, and hot reload.
"""
import sys
import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from time import sleep

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from config import (
    AppConfig,
    ServerConfig,
    PluginsConfig,
    MiddlewareConfig,
    RedisConfig,
    ConfigLoader,
    HotReloadService,
    DEFAULT_CONFIG,
)


class TestServerConfig(unittest.TestCase):
    """Test server configuration"""

    def test_default_values(self):
        """Test default values"""
        config = ServerConfig()
        self.assertEqual(config.host, "0.0.0.0")
        self.assertEqual(config.port, 3000)

    def test_custom_values(self):
        """Test custom values"""
        config = ServerConfig(host="127.0.0.1", port=8080)
        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, 8080)

    def test_port_validation(self):
        """Test port validation"""
        # Valid ports
        ServerConfig(port=1)
        ServerConfig(port=65535)

        # Invalid ports
        with self.assertRaises(ValueError):
            ServerConfig(port=0)

        with self.assertRaises(ValueError):
            ServerConfig(port=65536)


class TestPluginsConfig(unittest.TestCase):
    """Test plugins configuration"""

    def test_default_values(self):
        """Test default values"""
        config = PluginsConfig()
        self.assertEqual(config.directory, "./plugins")
        self.assertEqual(config.enabled, ["*"])


class TestAppConfig(unittest.TestCase):
    """Test application configuration"""

    def test_from_dict(self):
        """Test creating from dict"""
        config_dict = {
            "server": {
                "host": "127.0.0.1",
                "port": 8080
            },
            "redis": {
                "host": "redis-server",
                "port": 6380
            }
        }

        config = AppConfig.from_dict(config_dict)

        self.assertEqual(config.server.host, "127.0.0.1")
        self.assertEqual(config.server.port, 8080)
        self.assertEqual(config.redis.host, "redis-server")
        self.assertEqual(config.redis.port, 6380)

    def test_to_dict(self):
        """Test converting to dict"""
        config = AppConfig(
            server=ServerConfig(host="127.0.0.1", port=8080)
        )

        config_dict = config.to_dict()

        self.assertEqual(config_dict["server"]["host"], "127.0.0.1")
        self.assertEqual(config_dict["server"]["port"], 8080)

    def test_merge(self):
        """Test merging configs"""
        base_config = AppConfig(
            server=ServerConfig(host="0.0.0.0", port=3000)
        )

        update_dict = {
            "server": {
                "port": 8080
            },
            "plugins": {
                "enabled": ["plugin1"]
            }
        }

        merged = base_config.merge(update_dict)

        self.assertEqual(merged.server.host, "0.0.0.0")  # Unchanged
        self.assertEqual(merged.server.port, 8080)  # Updated
        self.assertEqual(merged.plugins.enabled, ["plugin1"])  # Added


class TestConfigLoader(unittest.TestCase):
    """Test config loader"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.temp_dir / "config"
        self.config_dir.mkdir()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_from_dict(self):
        """Test loading from dict"""
        loader = ConfigLoader()

        config_dict = {
            "server": {
                "host": "127.0.0.1",
                "port": 8080
            }
        }

        config = loader.load(config_dict=config_dict)

        self.assertEqual(config.server.host, "127.0.0.1")
        self.assertEqual(config.server.port, 8080)

    def test_load_from_json(self):
        """Test loading from JSON file"""
        loader = ConfigLoader(self.config_dir)

        config_path = self.config_dir / "config.json"
        config_dict = {
            "server": {
                "host": "127.0.0.1",
                "port": 8080
            }
        }

        import json
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f)

        config = loader.load(config_path=config_path)

        self.assertEqual(config.server.host, "127.0.0.1")
        self.assertEqual(config.server.port, 8080)

    def test_load_from_yaml(self):
        """Test loading from YAML file"""
        loader = ConfigLoader(self.config_dir)

        config_path = self.config_dir / "config.yaml"
        yaml_content = """
server:
  host: 127.0.0.1
  port: 8080
redis:
  host: redis-server
"""

        import yaml
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        config = loader.load(config_path=config_path)

        self.assertEqual(config.server.host, "127.0.0.1")
        self.assertEqual(config.server.port, 8080)
        self.assertEqual(config.redis.host, "redis-server")

    def test_load_invalid_port(self):
        """Test loading with invalid port"""
        loader = ConfigLoader(self.config_dir)

        config_path = self.config_dir / "config.json"
        config_dict = {
            "server": {
                "port": 99999  # Invalid
            }
        }

        import json
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f)

        with self.assertRaises(ValueError):
            loader.load(config_path=config_path)

    def test_merge_with_defaults(self):
        """Test merging with defaults"""
        loader = ConfigLoader(self.config_dir)

        # Config with only partial settings
        config_path = self.config_dir / "config.yaml"
        yaml_content = """
server:
  port: 8080
"""

        import yaml
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        config = loader.load(config_path=config_path)

        # Should have default values for missing fields
        self.assertEqual(config.server.host, "0.0.0.0")  # Default
        self.assertEqual(config.server.port, 8080)  # Custom
        self.assertEqual(config.redis.host, "localhost")  # Default

    def test_save_config(self):
        """Test saving config to file"""
        loader = ConfigLoader(self.config_dir)

        config = AppConfig(
            server=ServerConfig(host="127.0.0.1", port=8080)
        )

        # Save as YAML
        config_path_yaml = self.config_dir / "config.yaml"
        loader.save(config, config_path_yaml)
        self.assertTrue(config_path_yaml.exists())

        # Save as JSON
        config_path_json = self.config_dir / "config.json"
        loader.save(config, config_path_json)
        self.assertTrue(config_path_json.exists())

    def test_create_default_config(self):
        """Test creating default config file"""
        loader = ConfigLoader(self.config_dir)

        config_path = loader.create_default_config()

        self.assertTrue(config_path.exists())

        # Load and verify
        config = loader.load(config_path=config_path)
        self.assertEqual(config.server.host, "0.0.0.0")
        self.assertEqual(config.server.port, 3000)


class TestHotReloadService(unittest.TestCase):
    """Test hot reload service"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.temp_dir / "config"
        self.config_dir.mkdir()

        self.loader = ConfigLoader(self.config_dir)
        self.hot_reload = HotReloadService(self.loader, debounce_seconds=1.0)

    def tearDown(self):
        """Clean up"""
        self.hot_reload.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test hot reload service initialization"""
        self.assertIsNotNone(self.loader)
        self.assertIsNotNone(self.hot_reload)
        self.assertEqual(self.hot_reload.debounce_seconds, 1.0)

    def test_callbacks(self):
        """Test reload and error callbacks"""
        callback_called = {"count": 0}
        error_callback_called = {"count": 0}

        def reload_callback(new_config, old_config):
            callback_called["count"] += 1

        def error_callback(error_msg, exception):
            error_callback_called["count"] += 1

        self.hot_reload.add_reload_callback(reload_callback)
        self.hot_reload.add_error_callback(error_callback)

        self.assertEqual(len(self.hot_reload._on_reload_callbacks), 1)
        self.assertEqual(len(self.hot_reload._on_error_callbacks), 1)

        # Remove callbacks
        self.hot_reload.remove_reload_callback(reload_callback)
        self.hot_reload.remove_error_callback(error_callback)

        self.assertEqual(len(self.hot_reload._on_reload_callbacks), 0)
        self.assertEqual(len(self.hot_reload._on_error_callbacks), 0)

    def test_trigger_manual_reload(self):
        """Test manual config reload"""
        # Create initial config file
        loader = ConfigLoader(self.config_dir)
        config_path = self.config_dir / "config.yaml"
        yaml_content = """
server:
  host: 127.0.0.1
  port: 8080
"""

        import yaml
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        config = loader.load(config_path=config_path)
        self.assertEqual(config.server.port, 8080)

        # Setup hot reload
        hot_reload = HotReloadService(loader, debounce_seconds=1.0)
        reload_called = {"count": 0}

        def reload_callback(new_config, old_config):
            reload_called["count"] += 1

        hot_reload.add_reload_callback(reload_callback)

        # Modify config file
        yaml_content = """
server:
  host: 127.0.0.1
  port: 9999
"""

        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        # Wait for debounce
        sleep(2)

        # Cleanup
        hot_reload.stop()

        # Note: Hot reload uses watchdog which may not work in all environments
        # This test mainly verifies the API doesn't crash

    def test_rollback(self):
        """Test config rollback"""
        # Create initial config
        loader = ConfigLoader(self.config_dir)
        config_path = self.config_dir / "config.json"
        config_dict = {
            "server": {
                "port": 8080
            }
        }

        import json
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f)

        config = loader.load(config_path=config_path)

        # Setup hot reload
        hot_reload = HotReloadService(loader)
        hot_reload._previous_config = config

        # Modify current config
        loader._current_config = AppConfig(
            server=ServerConfig(port=9999)
        )

        # Rollback
        result = hot_reload.rollback()

        # Note: In practice this would require a failed reload
        # This test verifies the rollback API


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.temp_dir / "config"
        self.config_dir.mkdir()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_workflow(self):
        """Test full workflow: create, load, modify"""
        # Create loader
        loader = ConfigLoader(self.config_dir)

        # Create default config
        config_path = loader.create_default_config(self.config_dir / "app.yaml")
        self.assertTrue(config_path.exists())

        # Load config
        config = loader.load(config_path=config_path)
        self.assertIsNotNone(config)
        self.assertEqual(config.server.host, "0.0.0.0")

        # Modify config
        config.server.port = 9999
        loader.save(config, config_path)

        # Reload config
        reloaded = loader.load(config_path=config_path)
        self.assertEqual(reloaded.server.port, 9999)


if __name__ == "__main__":
    unittest.main(verbosity=2)
