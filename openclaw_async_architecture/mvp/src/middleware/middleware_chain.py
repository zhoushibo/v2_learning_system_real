"""
Middleware Chain
================

Manages execution of middleware chain.
"""
from typing import List, Optional, Callable, Any, Coroutine
import asyncio
import traceback

from .base_middleware import (
    BaseMiddleware,
    ExecutionContext,
    MiddlewareResult,
    MiddlewareOrder,
)


class MiddlewareChain:
    """
    Middleware chain that executes middlewares in order.
    """

    def __init__(self):
        self._pre_process_middlewares: List[BaseMiddleware] = []
        self._post_process_middlewares: List[BaseMiddleware] = []
        self._on_error_middlewares: List[BaseMiddleware] = []

    def add_middleware(self, middleware: BaseMiddleware) -> 'MiddlewareChain':
        """
        Add a middleware to the chain.

        Args:
            middleware: Middleware instance

        Returns:
            Self for chaining
        """
        if not isinstance(middleware, BaseMiddleware):
            raise TypeError(f"Middleware must inherit from BaseMiddleware, got {type(middleware)}")

        self._pre_process_middlewares.append(middleware)
        self._post_process_middlewares.append(middleware)
        self._on_error_middlewares.append(middleware)

        # Sort by priority (lower first)
        self._sort_middlewares()

        return self

    def remove_middleware(self, middleware_name: str) -> bool:
        """
        Remove a middleware by name.

        Args:
            middleware_name: Middleware name

        Returns:
            True if removed, False if not found
        """
        found_before = any(m.name == middleware_name for m in self._pre_process_middlewares)

        self._pre_process_middlewares = [
            m for m in self._pre_process_middlewares
            if m.name != middleware_name
        ]
        self._post_process_middlewares = [
            m for m in self._post_process_middlewares
            if m.name != middleware_name
        ]
        self._on_error_middlewares = [
            m for m in self._on_error_middlewares
            if m.name != middleware_name
        ]

        return found_before

    def get_middleware(self, middleware_name: str) -> Optional[BaseMiddleware]:
        """
        Get middleware by name.

        Args:
            middleware_name: Middleware name

        Returns:
            Middleware instance or None
        """
        for m in self._pre_process_middlewares:
            if m.name == middleware_name:
                return m
        return None

    def list_middlewares(self) -> List[str]:
        """List all middleware names"""
        return [m.name for m in self._pre_process_middlewares]

    def enable_middleware(self, middleware_name: str) -> bool:
        """Enable a middleware"""
        middleware = self.get_middleware(middleware_name)
        if middleware:
            middleware.enabled = True
            return True
        return False

    def disable_middleware(self, middleware_name: str) -> bool:
        """Disable a middleware"""
        middleware = self.get_middleware(middleware_name)
        if middleware:
            middleware.enabled = False
            return True
        return False

    def _sort_middlewares(self):
        """Sort middlewares by priority"""
        self._pre_process_middlewares.sort(key=lambda m: m.priority)
        self._post_process_middlewares.sort(key=lambda m: m.priority)
        self._on_error_middlewares.sort(key=lambda m: m.priority)

    async def execute_pre_process(self, ctx: ExecutionContext) -> bool:
        """
        Execute all pre-process middlewares.

        Args:
            ctx: Execution context

        Returns:
            True to continue execution, False to stop
        """
        for middleware in self._pre_process_middlewares:
            if not middleware.enabled:
                continue

            try:
                result: MiddlewareResult = await middleware.pre_process(ctx)

                if result.error:
                    ctx.error = result.error
                    return False

                # Check for cache hit (middleware sets modified_result)
                if result.skip_remaining and result.modified_result is not None:
                    # Cache hit: save result in context and stop execution
                    ctx.result = result.modified_result
                    ctx.set_metadata("cached", True)
                    return False

                if result.skip_remaining:
                    # Don't execute tool_func
                    return False

                if result.modified_params:
                    ctx.update_params(result.modified_params)

            except Exception as e:
                ctx.error = f"Pre-process middleware {middleware.name} failed: {e}"
                print(f"[MiddlewareChain] Pre-process error in {middleware.name}: {e}")
                traceback.print_exc()
                return False

        return True

    async def execute_post_process(
        self,
        ctx: ExecutionContext,
        tool_result: Any
    ) -> Any:
        """
        Execute all post-process middlewares.

        Args:
            ctx: Execution context
            tool_result: Result from tool execution

        Returns:
            Final result (may be modified by middlewares)
        """
        result = tool_result

        for middleware in self._post_process_middlewares:
            if not middleware.enabled:
                continue

            try:
                mr: MiddlewareResult = await middleware.post_process(ctx, result)

                if mr.modified_result is not None:
                    result = mr.modified_result

                if mr.skip_remaining:
                    break

            except Exception as e:
                ctx.error = f"Post-process middleware {middleware.name} failed: {e}"
                print(f"[MiddlewareChain] Post-process error in {middleware.name}: {e}")
                traceback.print_exc()

        return result

    async def execute_error_handling(
        self,
        ctx: ExecutionContext,
        error: Exception
    ) -> bool:
        """
        Execute error handling middlewares.

        Args:
            ctx: Execution context
            error: Exception that occurred

        Returns:
            True if error was handled, False to re-raise
        """
        handled = False

        for middleware in self._on_error_middlewares:
            if not middleware.enabled:
                continue

            try:
                result: MiddlewareResult = await middleware.on_error(ctx, error)

                if result.success and not result.error:
                    handled = True
                    # Error was handled, don't execute remaining error handlers
                    break

            except Exception as e:
                print(f"[MiddlewareChain] Error handler {middleware.name} itself failed: {e}")
                traceback.print_exc()

        return handled

    async def execute(
        self,
        ctx: ExecutionContext,
        tool_func: Callable[[], Coroutine[Any, Any, Any]]
    ) -> Any:
        """
        Execute middleware chain with tool function.

        Args:
            ctx: Execution context
            tool_func: Async tool function to execute

        Returns:
            Tool result (possibly modified by post-process middlewares)
        """
        from datetime import datetime

        # Pre-process
        continue_execution = await self.execute_pre_process(ctx)
        if not continue_execution:
            # Pre-process stopped (e.g., cache hit or rate limit)
            # Check if there's a cached result
            if ctx.result is not None:
                return ctx.result
            return None

        # Execute tool
        try:
            ctx.start_time = datetime.now()

            result = await tool_func()

            ctx.end_time = datetime.now()
            ctx.result = result

        except Exception as e:
            ctx.end_time = datetime.now()
            ctx.error = str(e)

            # Error handling
            handled = await self.execute_error_handling(ctx, e)

            if not handled:
                # Re-raise if not handled
                raise

            return None

        # Post-process
        final_result = await self.execute_post_process(ctx, result)

        return final_result

    def clear(self):
        """Clear all middlewares"""
        self._pre_process_middlewares.clear()
        self._post_process_middlewares.clear()
        self._on_error_middlewares.clear()

    @property
    def count(self) -> int:
        """Get number of middlewares in chain"""
        return len(self._pre_process_middlewares)
