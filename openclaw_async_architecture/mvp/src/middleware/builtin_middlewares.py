"""
Built-in Middlewares
====================

Common middlewares for logging, monitoring, rate limiting, and caching.
"""
import time
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from .base_middleware import (
    BaseMiddleware,
    ExecutionContext,
    MiddlewareResult,
)


class LoggingMiddleware(BaseMiddleware):
    """
    Logging middleware for structured logging.

    Logs all tool executions with context information.
    """

    def __init__(
        self,
        name: str = "logging",
        enabled: bool = True,
        log_level: str = "INFO",
        include_params: bool = True
    ):
        super().__init__(name, enabled, priority=10)
        self.log_level = log_level
        self.include_params = include_params

    async def pre_process(self, ctx: ExecutionContext) -> MiddlewareResult:
        """Log before tool execution"""
        log_data = {
            "event": "tool_start",
            "tool": ctx.tool_name,
            "user": ctx.user_id,
            "timestamp": datetime.now().isoformat(),
        }

        if self.include_params:
            log_data["params"] = self._sanitize_params(ctx.parameters)

        self._log(log_data)
        return MiddlewareResult()

    async def post_process(
        self,
        ctx: ExecutionContext,
        tool_result: Any
    ) -> MiddlewareResult:
        """Log after tool execution"""
        log_data = {
            "event": "tool_end",
            "tool": ctx.tool_name,
            "user": ctx.user_id,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": ctx.duration_ms,
            "success": ctx.error is None,
        }

        if ctx.error:
            log_data["error"] = ctx.error

        self._log(log_data)
        return MiddlewareResult()

    async def on_error(
        self,
        ctx: ExecutionContext,
        error: Exception
    ) -> MiddlewareResult:
        """Log errors"""
        log_data = {
            "event": "tool_error",
            "tool": ctx.tool_name,
            "user": ctx.user_id,
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "error_type": type(error).__name__,
        }

        self._log(log_data)
        return MiddlewareResult(success=False, error=str(error))

    def _log(self, data: Dict[str, Any]):
        """Log data to console"""
        print(f"[{self.name.upper()}] {json.dumps(data, ensure_ascii=False)}")

    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from parameters"""
        sensitive_keys = ["password", "token", "secret", "key", "api_key"]

        sanitized = {}
        for key, value in params.items():
            if any(sk in key.lower() for sk in sensitive_keys):
                sanitized[key] = "*****"
            else:
                sanitized[key] = value

        return sanitized


class MonitoringMiddleware(BaseMiddleware):
    """
    Monitoring middleware for performance tracking.

    Tracks execution time, error rates, and throughput.
    """

    def __init__(self, name: str = "monitoring", enabled: bool = True):
        super().__init__(name, enabled)
        self.priority = 20  # Execute after logging

        # Statistics
        self._stats: Dict[str, Dict[str, Any]] = {}

    async def post_process(
        self,
        ctx: ExecutionContext,
        tool_result: Any
    ) -> MiddlewareResult:
        """Update statistics after tool execution"""
        tool_name = ctx.tool_name

        # Initialize stats if needed
        if tool_name not in self._stats:
            self._stats[tool_name] = {
                "call_count": 0,
                "success_count": 0,
                "error_count": 0,
                "total_duration_ms": 0,
                "min_duration_ms": float('inf'),
                "max_duration_ms": 0,
            }

        stats = self._stats[tool_name]
        stats["call_count"] += 1

        if ctx.duration_ms is not None:
            stats["total_duration_ms"] += ctx.duration_ms
            stats["min_duration_ms"] = min(stats["min_duration_ms"], ctx.duration_ms)
            stats["max_duration_ms"] = max(stats["max_duration_ms"], ctx.duration_ms)

        if ctx.error:
            stats["error_count"] += 1
        else:
            stats["success_count"] += 1

        return MiddlewareResult()

    def get_stats(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a tool or all tools.

        Args:
            tool_name: Tool name (None for all tools)

        Returns:
            Statistics dict
        """
        if tool_name:
            stats = self._stats.get(tool_name, {})
            if stats and stats["call_count"] > 0:
                stats["avg_duration_ms"] = stats["total_duration_ms"] / stats["call_count"]
            return stats.copy()
        else:
            result = {}
            for tn, st in self._stats.items():
                result[tn] = st.copy()
                if st["call_count"] > 0:
                    result[tn]["avg_duration_ms"] = st["total_duration_ms"] / st["call_count"]
            return result

    def reset_stats(self, tool_name: Optional[str] = None):
        """Reset statistics"""
        if tool_name:
            if tool_name in self._stats:
                del self._stats[tool_name]
        else:
            self._stats.clear()


class RateLimitMiddleware(BaseMiddleware):
    """
    Rate limiting middleware.

    Limits tool execution rate per user or globally.
    """

    def __init__(
        self,
        name: str = "rate_limit",
        enabled: bool = True,
        max_requests: int = 100,
        window_seconds: int = 60
    ):
        super().__init__(name, enabled)
        self.priority = 30  # Execute before logging

        self.max_requests = max_requests
        self.window_seconds = window_seconds

        # Request history: {user_id: [timestamp1, timestamp2, ...]}
        self._history: Dict[str, List[float]] = {}

    async def pre_process(self, ctx: ExecutionContext) -> MiddlewareResult:
        """Check rate limit"""
        # Use user_id for per-user rate limiting
        # If no user_id, use "global" key
        user_key = ctx.user_id or "global"

        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        if user_key not in self._history:
            self._history[user_key] = []
        self._history[user_key] = [
            ts for ts in self._history[user_key]
            if ts > window_start
        ]

        # Check rate limit
        if len(self._history[user_key]) >= self.max_requests:
            return MiddlewareResult(
                success=False,
                skip_remaining=True,
                error=f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds} seconds"
            )

        # Add current request
        self._history[user_key].append(now)

        return MiddlewareResult()

    def get_remaining_requests(self, user_id: Optional[str] = None) -> int:
        """
        Get remaining requests for user.

        Args:
            user_id: User ID (None for global)

        Returns:
            Number of remaining requests
        """
        user_key = user_id or "global"

        if user_key not in self._history:
            return self.max_requests

        now = time.time()
        window_start = now - self.window_seconds

        recent_count = sum(
            1 for ts in self._history[user_key]
            if ts > window_start
        )

        return max(0, self.max_requests - recent_count)
