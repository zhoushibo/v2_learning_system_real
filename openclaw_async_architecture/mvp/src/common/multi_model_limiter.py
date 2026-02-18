"""多模型速率限制器 - 支持5个模型的并发和RPM控制"""
import asyncio
import time
import threading
from typing import Dict, Optional
from collections import deque
import json

# 加载API配置
API_CONFIG_PATH = r'C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\API_CONFIG_FINAL.json'

with open(API_CONFIG_PATH, 'r', encoding='utf-8') as f:
    API_CONFIG = json.load(f)['api_configs']


class MultiModelRateLimiter:
    """
    多模型速率限制器

    支持5个模型的并发限制和RPM控制：
    - 智谱: 1并发，RPM未知
    - 混元: 5并发，无RPM限制
    - NVIDIA 1: 5并发，40 RPM
    - NVIDIA 2: 5并发，40 RPM
    - SiliconFlow: 5 RPM（embeddings）
    """

    def __init__(self):
        # 并发限制（每个模型独立控制）
        self.concurrency_limits = {
            "zhipu": API_CONFIG['zhipu']['max_concurrent'],
            "hunyuan": API_CONFIG['hunyuan']['max_concurrent'],
            "nvidia1": API_CONFIG['nvidia1']['max_concurrent'],
            "nvidia2": API_CONFIG['nvidia2']['max_concurrent'],
            "siliconflow": None,  # Embeddings暂时不限并发
        }

        # RPM限制（请求/分钟）
        def parse_rpm(value):
            if value == "unknown" or value == "unlimited":
                return None
            return int(value)

        self.rpm_limits = {
            "zhipu": parse_rpm(API_CONFIG['zhipu']['max_rpm']),
            "hunyuan": parse_rpm(API_CONFIG['hunyuan']['max_rpm']),
            "nvidia1": parse_rpm(API_CONFIG['nvidia1']['max_rpm']),
            "nvidia2": parse_rpm(API_CONFIG['nvidia2']['max_rpm']),
            "siliconflow": parse_rpm(API_CONFIG['siliconflow']['max_rpm']),
        }

        # 当前并发数
        self.current_concurrency = {model: 0 for model in self.concurrency_limits.keys()}

        # RPM追踪（记录请求时间戳）
        self.request_history = {model: deque() for model in self.rpm_limits.keys()}

        # 并发锁（每个模型独立）
        self.concurrency_locks = {
            model: threading.Semaphore(limit)
            for model, limit in self.concurrency_limits.items()
            if limit is not None
        }

        # RPM锁
        self.rpm_lock = threading.Lock()

        print("="*60)
        print("多模型速率限制器初始化 [OK]")
        print("="*60)
        print("\n[统计] 并发限制：")
        for model, limit in self.concurrency_limits.items():
            print(f"  {model:12s}: {limit} 并发")
        print("\n[限制] RPM限制：")
        for model, limit in self.rpm_limits.items():
            print(f"  {model:12s}: {limit if limit else '无限制'} RPM")
        print("="*60)

    def acquire_concurrency(self, model: str) -> bool:
        """
        获取并发资源

        Args:
            model: 模型名称

        Returns:
            是否成功获取
        """
        if model == "siliconflow":
            return True  # Embeddings不限并发

        # 检查模型是否存在
        if model not in self.concurrency_locks:
            print(f"[WARN] 未知模型: {model}")
            return False

        # 尝试获取并发锁（非阻塞）
        acquired = self.concurrency_locks[model].acquire(blocking=False)

        if acquired:
            self.current_concurrency[model] += 1
            print(f"[Concurrency] {model}: 获取成功 (当前: {self.current_concurrency[model]}/{self.concurrency_limits[model]})")
        else:
            print(f"[Concurrency] {model}: 达到上限 {self.concurrency_limits[model]}")

        return acquired

    def release_concurrency(self, model: str):
        """释放并发资源"""
        if model not in self.concurrency_locks:
            return

        if self.current_concurrency[model] > 0:
            self.current_concurrency[model] -= 1
            self.concurrency_locks[model].release()
            print(f"[Concurrency] {model}: 释放 (当前: {self.current_concurrency[model]}/{self.concurrency_limits[model]})")

    def check_rpm_limit(self, model: str) -> bool:
        """
        检查RPM限制

        Args:
            model: 模型名称

        Returns:
            是否可以发送请求（未超限）
        """
        if model == "siliconflow":
            rpm_limit = self.rpm_limits.get(model, 0)
        else:
            rpm_limit = self.rpm_limits.get(model)

        # 无限制
        if rpm_limit is None:
            return True

        with self.rpm_lock:
            now = time.time()
            history = self.request_history[model]

            # 清理60秒前的请求记录
            cutoff = now - 60
            while history and history[0] < cutoff:
                history.popleft()

            # 检查是否超限
            if len(history) >= rpm_limit:
                print(f"[RPM] {model}: 达到限制 {len(history)}/{rpm_limit} RPM")
                return False

            # 记录本次请求
            history.append(now)
            print(f"[RPM] {model}: 记录请求 ({len(history)}/{rpm_limit} RPM)")
            return True

    def get_available_model(self, preferred_models: list) -> Optional[str]:
        """
        获取可用的模型（按优先级）

        Args:
            preferred_models: 优先级列表

        Returns:
            可用的模型名称，或None
        """
        for model in preferred_models:
            # 检查并发
            if not self.acquire_concurrency(model):
                continue

            # 检查RPM
            if not self.check_rpm_limit(model):
                self.release_concurrency(model)
                continue

            return model

        return None

    def get_status(self) -> Dict:
        """获取所有模型的状态"""
        status = {}

        for model in self.concurrency_limits.keys():
            # 并发状态
            concurrency_current = self.current_concurrency[model]
            concurrency_limit = self.concurrency_limits[model]

            # RPM状态
            rpm_current = 0
            rpm_limit = self.rpm_limits[model]

            if rpm_limit is not None:
                with self.rpm_lock:
                    now = time.time()
                    cutoff = now - 60
                    history = self.request_history[model]
                    rpm_current = len([t for t in history if t >= cutoff])

            status[model] = {
                "concurrency": {
                    "current": concurrency_current,
                    "limit": concurrency_limit,
                    "available": concurrency_limit - concurrency_current
                },
                "rpm": {
                    "current": rpm_current if rpm_limit else None,
                    "limit": rpm_limit
                }
            }

        return status


# 全局实例
limiter_instance = None

def get_rate_limiter():
    """获取速率限制器实例"""
    global limiter_instance
    if limiter_instance is None:
        limiter_instance = MultiModelRateLimiter()
    return limiter_instance


if __name__ == "__main__":
    # 测试
    limiter = MultiModelRateLimiter()

    print("\n1️⃣ 测试并发限制")
    limiter.acquire_concurrency("zhipu")
    limiter.acquire_concurrency("zhipu")  # 应该失败（只有1并发）

    print("\n2️⃣ 测试RPM限制")
    for i in range(42):  # 超过NVIDIA限制（40）
        result = limiter.check_rpm_limit("nvidia1")
        if not result:
            print(f"RPM限制触发: {i+1}/40")
            break

    print("\n3️⃣ 状态查询")
    status = limiter.get_status()
    import json
    print(json.dumps(status, indent=2, ensure_ascii=False))
