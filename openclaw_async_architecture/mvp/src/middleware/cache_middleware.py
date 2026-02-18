"""
Cache Middleware
================

Middleware for caching tool results.
"""
from typing import Optional, Dict, Any
import hashlib
import json

from .base_middleware import (
    BaseMiddleware,
    ExecutionContext,
    MiddlewareResult,
)


class CacheMiddleware(BaseMiddleware):
    """
    Result caching middleware.

    Caches tool results to improve performance.
    """

    def __init__(
        self,
        name: str = "cache",
        enabled: bool = True,
        cache_store: Optional[Dict[str, Any]] = None,
        ttl: int = 3600,
        cache_key_prefix: str = "tool_cache"
    ):
        """
        Initialize cache middleware.

        Args:
            name: Middleware name
            enabled: Whether enabled
            cache_store: Cache store (dict by default, can be Redis)
            ttl: TTL in seconds
            cache_key_prefix: Prefix for cache keys
        """
        super().__init__(name, enabled)
        self.priority = 5  # Execute first (highest priority)

        self.ttl = ttl
        self.cache_key_prefix = cache_key_prefix

        # Use provided store or default to in-memory dict
        self._cache = cache_store if cache_store is not None else {}
        self._timestamps = {}  # Cache timestamps

    async def pre_process(self, ctx: ExecutionContext) -> MiddlewareResult:
        """Check cache before tool execution"""
        cache_key = self._generate_cache_key(ctx.tool_name, ctx.parameters)

        # Check if cached
        if cache_key in self._cache:
            cached_value, timestamp = self._cache[cache_key], self._timestamps[cache_key]

            # Check TTL
            from time import time
            if time() - timestamp < self.ttl:
                # Cache hit
                ctx.set_metadata("cache_hit", True)
                ctx.set_metadata("cache_key", cache_key)

                # Return cached result immediately
                return MiddlewareResult(
                    skip_remaining=True,
                    modified_result=cached_value
                )
            else:
                # Cache expired
                del self._cache[cache_key]
                del self._timestamps[cache_key]

        return MiddlewareResult()

    async def post_process(
        self,
        ctx: ExecutionContext,
        tool_result: Any
    ) -> MiddlewareResult:
        """Cache result after tool execution"""
        # Don't cache if there was an error
        if ctx.error:
            return MiddlewareResult()

        # Cache the result
        cache_key = self._generate_cache_key(ctx.tool_name, ctx.parameters)
        self._cache[cache_key] = tool_result

        from time import time
        self._timestamps[cache_key] = time()

        return MiddlewareResult()

    def _generate_cache_key(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key from tool name and parameters"""
        # Create a deterministic string representation
        key_data = {
            "tool": tool_name,
            "params": parameters,
        }

        key_string = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        key_hash = hashlib.md5(key_string.encode('utf-8')).hexdigest()

        return f"{self.cache_key_prefix}:{key_hash}"

    def invalidate(self, tool_name: Optional[str] = None):
        """
        Invalidate cache entries.

        Args:
            tool_name: Tool name to invalidate (None for all)
        """
        if tool_name is None:
            # Invalidate all
            self._cache.clear()
            self._timestamps.clear()
        else:
            # Invalidate specific tool
            keys_to_delete = [
                key for key in self._cache
                if key.startswith(tool_name)
            ]
            for key in keys_to_delete:
                del self._cache[key]
                del self._timestamps[key]

    def get_cache_size(self) -> int:
        """Get current cache size"""
        return len(self._cache)

    def clear_cache(self):
        """Clear all cache"""
        self._cache.clear()
        self._timestamps.clear()
