"""
Middleware System
=================

Middleware system for preprocessing and postprocessing tool execution.

Components:
- base_middleware: Base class for middlewares
- middleware_chain: Execution chain manager
- builtin_middlewares: Built-in middlewares (logging, monitoring, rate limiting)
- cache_middleware: Result caching middleware

Usage:
    from src.middleware import MiddlewareChain, LoggingMiddleware, CacheMiddleware

    # Create chain
    chain = MiddlewareChain()
    chain.add_middleware(LoggingMiddleware())
    chain.add_middleware(CacheMiddleware())

    # Execute
    import asyncio
    async def tool_func():
        return "Result"

    from src.middleware import ExecutionContext
    ctx = ExecutionContext("test_tool", {"param": "value"})

    result = await chain.execute(ctx, tool_func)
"""

from .base_middleware import (
    BaseMiddleware,
    MiddlewareResult,
    ExecutionContext,
    MiddlewareOrder,
)
from .middleware_chain import MiddlewareChain
from .builtin_middlewares import (
    LoggingMiddleware,
    MonitoringMiddleware,
    RateLimitMiddleware,
)
from .cache_middleware import CacheMiddleware
from .config_loader import MiddlewareConfigLoader

__all__ = [
    # Base
    "BaseMiddleware",
    "MiddlewareResult",
    "ExecutionContext",
    "MiddlewareOrder",
    # Chain
    "MiddlewareChain",
    # Built-in
    "LoggingMiddleware",
    "MonitoringMiddleware",
    "RateLimitMiddleware",
    "CacheMiddleware",
    "MiddlewareConfigLoader",
]

__version__ = "1.0.0"
