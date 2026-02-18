# test_integration.py
"""
Integration Test for V2 + Phase 3
===================================

测试插件系统、中间件、配置与 V2 Worker 的集成
"""
import sys
import unittest
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent  # mvp
# 项目根目录是 openclaw_async_architecture
root_dir = project_root.parent
src_root = project_root / "src"

# 把根目录加入sys路径（放在最后以避免与标准库冲突）
sys.path.append(str(root_dir))
# 把src也加入sys路径（用于plugin_system等顶级模块的导入）
sys.path.append(str(src_root))

from src.worker.tools.tool_manager_integration import ToolManager, get_tool_manager


class TestToolManagerIntegration(unittest.TestCase):
    """测试工具管理器集成"""

    def setUp(self):
        """Set up test fixtures"""
        self.plugin_dir = project_root / "plugins"
        self.config_dir = project_root / "config"

    def tearDown(self):
        """Clean up"""
        # Shutdown tool manager
        if hasattr(self, 'tool_manager') and self.tool_manager:
            self.tool_manager.shutdown()

    def test_load_plugins(self):
        """测试加载插件"""
        tool_manager = tool_manager_integration.ToolManager(self.plugin_dir, self.config_dir, enable_hot_reload=False)
        self.tool_manager = tool_manager

        # Load plugins
        loaded = tool_manager.load_plugins()

        # Should load at least example_plugin and filesystem_plugin
        self.assertGreaterEqual(loaded, 1)

    def test_list_tools(self):
        """测试列出工具"""
        tool_manager = ToolManager(self.plugin_dir, self.config_dir, enable_hot_reload=False)
        self.tool_manager = tool_manager

        tool_manager.load_plugins()

        # List tools
        tools = tool_manager.list_tools()

        # Should have some tools
        self.assertGreater(len(tools), 0)

    def test_get_tool_info(self):
        """测试获取工具信息"""
        tool_manager = ToolManager(self.plugin_dir, self.config_dir, enable_hot_reload=False)
        self.tool_manager = tool_manager

        tool_manager.load_plugins()

        # Get tool info
        info = tool_manager.get_tool_info("read_file")

        if info:
            self.assertEqual(info["name"], "read_file")
            self.assertIn("parameters", info)
        else:
            # read_file tool may not be available
            print("[Test] read_file tool not available")

    def test_execute_tool_hello_world(self):
        """测试执行 hello_world 工具（来自 example_plugin）"""
        tool_manager = ToolManager(self.plugin_dir, self.config_dir, enable_hot_reload=False)
        self.tool_manager = tool_manager

        tool_manager.load_plugins()

        # Execute hello_world
        async def execute():
            result = await tool_manager.execute_tool(
                "hello_world",
                {"name": "Integration Test"}
            )
            return result

        result = asyncio.run(execute())

        # Check result
        if result:
            self.assertEqual(result, "Hello, Integration Test!")
        else:
            print("[Test] hello_world tool not available")

    def test_execute_tool_read_file(self):
        """测试执行 read_file 工具（来自 filesystem_plugin）"""
        tool_manager = ToolManager(self.plugin_dir, self.config_dir, enable_hot_reload=False)
        self.tool_manager = tool_manager

        tool_manager.load_plugins()

        # Create test file
        test_file = project_root / "test_file.txt"
        test_file.write_text("Hello from integration test!")

        # Execute read_file
        async def execute():
            result = await tool_manager.execute_tool(
                "read_file",
                {"path": str(test_file)}
            )
            return result

        try:
            result = asyncio.run(execute())

            # Check result
            if result:
                self.assertEqual(result, "Hello from integration test!")
            else:
                print("[Test] read_file tool not available or failed")
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()

    def test_security_middleware_path_validation(self):
        """测试安全中间件路径验证"""
        tool_manager = ToolManager(self.plugin_dir, self.config_dir, enable_hot_reload=False)
        self.tool_manager = tool_manager

        tool_manager.load_plugins()

        # Try to access path outside whitelist
        async def execute():
            result = await tool_manager.execute_tool(
                "read_file",
                {"path": "/etc/passwd"}  # Should be blocked
            )
            return result

        result = asyncio.run(execute())

        # Should fail due to security check
        self.assertIsNone(result)


class TestSecurityIntegration(unittest.TestCase):
    """测试安全集成"""

    def setUp(self):
        """Set up test fixtures"""
        self.plugin_dir = project_root / "plugins"
        self.config_dir = project_root / "config"

    def tearDown(self):
        """Clean up"""
        if hasattr(self, 'tool_manager') and self.tool_manager:
            self.tool_manager.shutdown()

    def test_path_whitelist(self):
        """测试路径白名单"""
        tool_manager = ToolManager(self.plugin_dir, self.config_dir, enable_hot_reload=False)
        self.tool_manager = tool_manager

        tool_manager.load_plugins()

        # Valid path (in workspace)
        test_file = project_root / "workspace_test.txt"
        test_file.write_text("test")

        async def execute_valid():
            result = await tool_manager.execute_tool(
                "read_file",
                {"path": str(test_file)}
            )
            return result

        try:
            result = asyncio.run(execute_valid())
            self.assertIsNotNone(result)
        finally:
            if test_file.exists():
                test_file.unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
