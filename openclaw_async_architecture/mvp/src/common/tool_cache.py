# -*- coding: utf-8 -*-
"""工具结果缓存 - Phase 2性能优化"""

from abc import ABC, abstractmethod
from typing import Optional, Any
import hashlib
import json
from datetime import datetime, timedelta
from ..common.connection_pool import redis_pool


class BaseCache(ABC):
    """缓存基类"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存"""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """清空缓存"""
        pass


class ToolResultCache(BaseCache):
    """
    工具结果缓存（基于Redis）

    缓存策略：
    - Key: tool_name:hash(input_args)
    - Value: JSON字符串
    - TTL: 默认1小时（可配置）
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        初始化

        Args:
            max_size: 最大缓存条目数（使用LRU淘汰）
            default_ttl: 默认TTL（秒）
        """
        self.redis_client = redis_pool.client
        self.prefix = "tools:result:"
        self.default_ttl = default_ttl
        self.max_size = max_size

    def _make_key(self, tool_name: str, args: dict) -> str:
        """生成缓存键

        Args:
            tool_name: 工具名称
            args: 工具参数

        Returns:
            缓存键
        """
        # 对参数进行规范化处理（排序键名）
        normalized_args = json.dumps(args, sort_keys=True, ensure_ascii=False)
        # 计算MD5哈希
        hash_obj = hashlib.md5(normalized_args.encode('utf-8'))
        return f"{self.prefix}{tool_name}:{hash_obj.hexdigest()}"

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            cached = self.redis_client.get(key)
            if cached:
                data = json.loads(cached)
                return data.get("result")
            return None
        except Exception:
            return None

    def get_by_tool(self, tool_name: str, args: dict) -> Optional[Any]:
        """通过工具名和参数获取缓存"""
        key = self._make_key(tool_name, args)
        return self.get(key)

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存"""
        try:
            if ttl is None:
                ttl = self.default_ttl

            data = {
                "result": value,
                "timestamp": datetime.now().isoformat()
            }

            self.redis_client.setex(key, ttl, json.dumps(data))
            return True
        except Exception:
            return False

    def set_by_tool(self, tool_name: str, args: dict, result: Any, ttl: int = None) -> bool:
        """通过工具名和参数设置缓存"""
        key = self._make_key(tool_name, args)
        return self.set(key, result, ttl)

    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception:
            return False

    def delete_by_tool(self, tool_name: str, args: dict) -> bool:
        """通过工具名和参数删除缓存"""
        key = self._make_key(tool_name, args)
        return self.delete(key)

    def clear(self) -> bool:
        """清空所有工具结果缓存"""
        try:
            keys = self.redis_client.keys(f"{self.prefix}*")
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception:
            return False

    def clear_by_tool(self, tool_name: str) -> bool:
        """清空指定工具的缓存"""
        try:
            keys = self.redis_client.keys(f"{self.prefix}{tool_name}:*")
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception:
            return False

    def get_stats(self) -> dict:
        """获取缓存统计"""
        stats = {
            "total_keys": 0,
            "tools": {}
        }

        try:
            keys = self.redis_client.keys(f"{self.prefix}*")
            stats["total_keys"] = len(keys)

            # 按工具分组统计
            for key in keys:
                # 提取工具名
                parts = key.split(":")
                if len(parts) >= 3:
                    tool_name = parts[2]
                    if tool_name not in stats["tools"]:
                        stats["tools"][tool_name] = 0
                    stats["tools"][tool_name] += 1

        except Exception:
            pass

        return stats

    def invalidate_by_pattern(self, pattern: str) -> int:
        """根据模式使缓存失效

        Args:
            pattern: 匹配模式（如 "read_file:*"）

        Returns:
            失效的缓存数量
        """
        try:
            keys = self.redis_client.keys(f"{self.prefix}{pattern}")
            if keys:
                self.redis_client.delete(*keys)
                return len(keys)
            return 0
        except Exception:
            return 0


# 全局单例
tool_cache = ToolResultCache(max_size=1000, default_ttl=3600)
