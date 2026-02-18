"""
学习缓存系统

降低API调用频率，节省成本，避免限流
"""
import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LearningCache:
    """学习缓存系统"""

    def __init__(self, cache_file: Optional[Path] = None):
        """
        初始化缓存

        Args:
            cache_file: 缓存文件路径
        """
        if cache_file:
            self.cache_file = cache_file
        else:
            self.cache_file = Path(__file__).parent.parent / "data" / "learning_cache.json"

        self.cache: Dict[str, dict] = {}
        self._load_cache()

    def _get_cache_key(self, topic: str, perspective: str, style: str = "deep_analysis") -> str:
        """
        生成缓存键

        Args:
            topic: 学习主题
            perspective: 学习视角
            style: 学习风格

        Returns:
            缓存键（MD5哈希）
        """
        key_str = f"{topic}:{perspective}:{style}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, topic: str, perspective: str, style: str = "deep_analysis") -> Optional[dict]:
        """
        获取缓存结果

        Args:
            topic: 学习主题
            perspective: 学习视角
            style: 学习风格

        Returns:
            缓存结果，如果不存在返回None
        """
        key = self._get_cache_key(topic, perspective, style)

        if key in self.cache:
            result = self.cache[key]
            logger.info(f"✅ 缓存命中: {topic} ({perspective})")
            return result

        logger.info(f"❌ 缓存未命中: {topic} ({perspective})")
        return None

    def set(self, topic: str, perspective: str, result: dict, style: str = "deep_analysis"):
        """
        设置缓存

        Args:
            topic: 学习主题
            perspective: 学习视角
            result: 学习结果
            style: 学习风格
        """
        key = self._get_cache_key(topic, perspective, style)

        self.cache[key] = {
            "topic": topic,
            "perspective": perspective,
            "style": style,
            "result": result,
            "cached_at": datetime.now().isoformat()
        }

        logger.info(f"💾 缓存保存: {topic} ({perspective})")
        self._save_cache()

    def _load_cache(self):
        """加载缓存文件"""
        if self.cache_file and self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache = data.get("cache", {})
                logger.info(f"✅ 加载缓存: {len(self.cache)} 条记录")
            except Exception as e:
                logger.warning(f"加载缓存失败: {e}")
                self.cache = {}

    def _save_cache(self):
        """保存缓存文件"""
        if self.cache_file:
            try:
                self.cache_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "cache": self.cache,
                        "last_updated": datetime.now().isoformat()
                    }, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"保存缓存失败: {e}")

    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            "total_entries": len(self.cache),
            "cache_file": str(self.cache_file) if self.cache_file else None
        }

    def clear(self):
        """清空缓存"""
        self.cache = {}
        self._save_cache()
        logger.info("🗑️ 缓存已清空")
