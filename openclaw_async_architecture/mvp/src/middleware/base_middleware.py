"""
Middleware Architecture
=======================

Middleware system for preprocessing and postprocessing tool execution.
"""
from enum import Enum
from typing import Optional, Dict, Any, Coroutine
from datetime import datetime


class MiddlewareResult:
    """Result from middleware execution"""

    def __init__(
        self,
        success: bool = True,
        skip_remaining: bool = False,
        modified_params: Optional[Dict[str, Any]] = None,
        modified_result: Optional[Any] = None,
        error: Optional[str] = None
    ):
        self.success = success
        self.skip_remaining = skip_remaining
        self.modified_params = modified_params
        self.modified_result = modified_result
        self.error = error


class ExecutionContext:
    """Context passed through middleware chain"""

    def __init__(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.tool_name = tool_name
        self.parameters = parameters
        self.original_parameters = parameters.copy()
        self.user_id = user_id
        self.metadata = metadata or {}

        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.result: Optional[Any] = None
        self.error: Optional[str] = None

        # Middleware-specific data
        self.middleware_data: Dict[str, Any] = {}

    @property
    def duration_ms(self) -> Optional[float]:
        """Get execution duration in milliseconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None

    def update_params(self, new_params: Dict[str, Any]):
        """Update parameters (used by middleware)"""
        self.parameters.update(new_params)

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)

    def set_metadata(self, key: str, value: Any):
        """Set metadata value"""
        self.metadata[key] = value

    def get_middleware_data(self, key: str, default: Any = None) -> Any:
        """Get middleware-specific data"""
        return self.middleware_data.get(key, default)

    def set_middleware_data(self, key: str, value: Any):
        """Set middleware-specific data"""
        self.middleware_data[key] = value


class MiddlewareOrder(str, Enum):
    """Middleware execution order"""
    PRE_PROCESS = "pre_process"  # Before tool execution
    POST_PROCESS = "post_process"  # After tool execution
    ON_ERROR = "on_error"  # When tool execution fails


class BaseMiddleware:
    """Base class for all middlewares"""

    def __init__(self, name: str, enabled: bool = True, priority: int = 100):
        self.name = name
        self.enabled = enabled
        self.priority = priority  # Lower priority executes first

    async def pre_process(self, ctx: ExecutionContext) -> MiddlewareResult:
        """
        Pre-process before tool execution.

        Args:
            ctx: Execution context

        Returns:
            MiddlewareResult (set skip_remaining=True to stop chain)
        """
        return MiddlewareResult()

    async def post_process(
        self,
        ctx: ExecutionContext,
        tool_result: Any
    ) -> MiddlewareResult:
        """
        Post-process after tool execution.

        Args:
            ctx: Execution context
            tool_result: Result from tool execution

        Returns:
            MiddlewareResult (modified_result can be set)
        """
        return MiddlewareResult()

    async def on_error(
        self,
        ctx: ExecutionContext,
        error: Exception
    ) -> MiddlewareResult:
        """
        Handle errors from tool execution.

        Args:
            ctx: Execution context
            error: Exception that occurred

        Returns:
            MiddlewareResult (error can be handled or re-raised)
        """
        return MiddlewareResult(success=False, error=str(error))

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, enabled={self.enabled}, priority={self.priority})"
