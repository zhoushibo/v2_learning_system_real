# test_simplified_integration.py
"""
Simplified Integration Test
===========================

简化集成测试 - 直接测试插件系统和中间件
"""
import sys
from pathlib import Path

# 项目根目录
root_dir = Path(__file__).parent.parent
src_dir = root_dir / "src"

# 把 src 加入 sys.path
sys.path.insert(0, str(src_dir))

# 直接导入（避免 __init__.py 的导入循环）
import plugin_system
import middleware


class TestSimplifiedIntegration:
    """简化集成测试"""

    def test_plugin_system(self):
        """测试插件系统"""
        print("[Test] Testing plugin system...")

        # 加载插件
        plugin_dir = Path(__file__).parent / "plugins"
        print(f"[Test] Plugin dir: {plugin_dir}")
        print(f"[Test] Plugin dir exists: {plugin_dir.exists()}")

        loader = plugin_system.PluginLoader(plugin_dir)
        loaded = loader.discover_and_load_all()

        print(f"[Test] Loaded {loaded} plugins")

        # 列出工具
        registry = plugin_system.get_registry()
        tools = registry.list_tools()
        print(f"[Test] Available tools: {tools}")

        assert len(tools) > 0, "Should have at least one tool"

    def test_middleware_system(self):
        """测试中间件系统"""
        print("[Test] Testing middleware system...")

        # 创建中间件链
        chain = middleware.MiddlewareChain()
        chain.add_middleware(middleware.LoggingMiddleware())

        print(f"[Test] Created middleware chain with {chain.count} middlewares")

        assert chain.count > 0, "Should have at least one middleware"


if __name__ == "__main__":
    test = TestSimplifiedIntegration()

    print("=== Starting Simplified Integration Tests ===")

    try:
        test.test_plugin_system()
        print("[Test] Plugin system: PASS")
    except Exception as e:
        print(f"[Test] Plugin system: FAIL - {e}")

    try:
        test.test_middleware_system()
        print("[Test] Middleware system: PASS")
    except Exception as e:
        print(f"[Test] Middleware system: FAIL - {e}")

    print("=== Tests Complete ===")
