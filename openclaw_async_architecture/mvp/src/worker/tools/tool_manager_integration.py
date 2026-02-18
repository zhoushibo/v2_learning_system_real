"""
Tool Manager Integration
========================

工具管理器 - 整合插件系统、中间件架构、配置系统
"""
import asyncio
from pathlib import Path
from typing import Any, Optional, Dict

from plugin_system import PluginLoader, SandboxedRuntime, get_registry
from middleware import MiddlewareChain
from worker.tools.security_middleware import SecurityMiddleware


class ToolManager:
    """
    工具管理器（整合架构）

    职责：
    1. 加载和管理插件
    2. 执行工具（带中间件）
    3. 管理配置和热重载
    4. 提供统一的工具接口
    """

    def __init__(
        self,
        plugin_dir: Optional[Path] = None,
        config_dir: Optional[Path] = None,
        enable_hot_reload: bool = True
    ):
        """
        初始化工具管理器。

        Args:
            plugin_dir: 插件目录
            config_dir: 配置目录
            enable_hot_reload: 是否启用配置热重载
        """
        # 初始化插件系统
        self.plugin_dir = plugin_dir or Path("./plugins")
        self.plugin_loader = PluginLoader(self.plugin_dir)
        self.sandbox_runtime = SandboxedRuntime()

        # 初始化中间件链
        self.middleware_chain = MiddlewareChain()

        # 添加安全中间件（优先级最高）
        self.middleware_chain.add_middleware(SecurityMiddleware(priority=1))

        # 初始化配置系统
        self.config_dir = config_dir or Path("./config")
        self.config_loader = ConfigLoader(self.config_dir)
        self.hot_reload = None

        # 加载配置
        self._load_config()

        # 启用热重载
        if enable_hot_reload:
            self._enable_hot_reload()

    def _load_config(self):
        """加载应用配置"""
        try:
            self.app_config = self.config_loader.load()
            print(f"[ToolManager] Configuration loaded")
        except Exception as e:
            print(f"[ToolManager] Failed to load config: {e}")

    def _enable_hot_reload(self):
        """启用配置热重载"""
        try:
            self.hot_reload = HotReloadService(self.config_loader)

            # 添加配置重载回调
            async def on_config_reload(new_config, old_config):
                print(f"[ToolManager] Config reloaded")
                self.app_config = new_config

            self.hot_reload.add_reload_callback(on_config_reload)

            # 启动热重载
            if self.hot_reload.is_available:
                self.hot_reload.start()
                print(f"[ToolManager] Hot reload enabled")
            else:
                print(f"[ToolManager] Hot reload not available (watchdog disabled)")

        except Exception as e:
            print(f"[ToolManager] Failed to enable hot reload: {e}")

    def load_plugins(self):
        """加载所有插件"""
        loaded = self.plugin_loader.discover_and_load_all()
        print(f"[ToolManager] Loaded {loaded} plugins")

        # 显示加载的工具
        registry = get_registry()
        tools = registry.list_tools()
        print(f"[ToolManager] Available tools: {', '.join(tools)}")

        return loaded

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Any:
        """
        执行工具（带中间件）

        Args:
            tool_name: 工具名称
            parameters: 工具参数
            user_id: 用户ID（可选）

        Returns:
            工具执行结果

        Raises:
            Exception: 工具执行失败
        """
        from middleware import ExecutionContext

        # 获取工具类
        tool_class = self.plugin_loader.get_tool_class(tool_name)
        if not tool_class:
            raise Exception(f"Tool not found: {tool_name}")

        # 实例化工具
        tool = tool_class()

        # 创建执行上下文
        ctx = ExecutionContext(
            tool_name=tool_name,
            parameters=parameters,
            user_id=user_id
        )

        # 定义工具函数
        async def tool_func():
            # 通过砂箱运行时执行
            result = await self.sandbox_runtime.execute_tool(
                tool,
                tool_name,
                parameters,
                skip_validation=True  # 已在 pre_process 中验证
            )
            return result

        # 通过中间件链执行
        result = await self.middleware_chain.execute(ctx, tool_func)

        return result

    def list_tools(self):
        """列出所有可用工具"""
        registry = get_registry()
        return registry.list_tools()

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具信息"""
        registry = get_registry()
        tool = registry.get_tool(tool_name)
        if tool:
            return {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "parameters": [
                    {"name": p.name, "type": p.type, "required": p.required, "description": p.description}
                    for p in tool.parameters
                ]
            }
        return None

    def reload_plugins(self):
        """重新加载插件"""
        registry = get_registry()
        plugin_names = registry.list_plugins()

        for plugin_name in plugin_names:
            self.plugin_loader.reload_plugin(plugin_name)

        print(f"[ToolManager] Reloaded {len(plugin_names)} plugins")

    def shutdown(self):
        """关闭工具管理器"""
        if self.hot_reload:
            self.hot_reload.stop()

        print(f"[ToolManager] Shutdown complete")


# 全局实例（单例）
_tool_manager = None


def get_tool_manager(
    plugin_dir: Optional[Path] = None,
    config_dir: Optional[Path] = None,
    enable_hot_reload: bool = True
) -> ToolManager:
    """
    获取工具管理器实例（单例）

    Args:
        plugin_dir: 插件目录
        config_dir: 配置目录
        enable_hot_reload: 是否启用配置热重载

    Returns:
        ToolManager 实例
    """
    global _tool_manager

    if _tool_manager is None:
        _tool_manager = ToolManager(
            plugin_dir=plugin_dir,
            config_dir=config_dir,
            enable_hot_reload=enable_hot_reload
        )

    return _tool_manager
