"""
Token Bucket算法验证测试
验证令牌桶限流器的正确性和性能
"""
import time
import asyncio
from typing import Optional


class TokenBucket:
    """令牌桶限流器"""

    def __init__(self, rate: float, capacity: int):
        """
        Args:
            rate: 令牌生成速率（每秒令牌数）
            capacity: 桶容量（最大令牌数）
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()

    def try_acquire(self) -> bool:
        """
        尝试获取一个令牌

        Returns:
            True（成功）/ False（令牌不足）
        """
        # 补充令牌
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

        # 检查令牌
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def get_tokens(self) -> int:
        """获取当前令牌数"""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.rate
        return int(min(self.capacity, self.tokens + new_tokens))


async def test_basic():
    """基础测试：验证限流"""
    print("=== 基础测试 ===")

    # 1 token/s，容量5
    bucket = TokenBucket(rate=1, capacity=5)

    # 初始应该有5个令牌
    assert bucket.try_acquire() == True
    assert bucket.try_acquire() == True
    assert bucket.try_acquire() == True
    assert bucket.try_acquire() == True
    assert bucket.try_acquire() == True
    assert bucket.try_acquire() == False  # 第6个应该失败
    print("✓ 基础限流测试通过")


async def test_refill():
    """令牌补充测试"""
    print("=== 令牌补充测试 ===")

    bucket = TokenBucket(rate=10, capacity=10)

    # 消耗所有令牌
    for _ in range(10):
        assert bucket.try_acquire() == True
    assert bucket.try_acquire() == False

    # 等待0.1秒，应该补充1个令牌
    await asyncio.sleep(0.1)
    assert bucket.try_acquire() == True  # 应该成功
    assert bucket.try_acquire() == False  # 应该失败

    # 等待0.5秒，应该补充5个令牌
    await asyncio.sleep(0.5)
    for _ in range(5):
        assert bucket.try_acquire() == True

    print("✓ 令牌补充测试通过")


async def test_rpm():
    """RPM限流测试：40 RPM = 0.667 tokens/s"""
    print("=== RPM限流测试 ===")

    # 40 RPM = 40/60 tokens/s = 0.667 tokens/s
    bucket = TokenBucket(rate=40/60, capacity=40)

    # 消耗所有令牌
    success_count = 0
    for _ in range(100):
        if bucket.try_acquire():
            success_count += 1

    print(f"初始成功获取: {success_count} 个令牌")
    assert success_count == 40, f"应该有40个令牌，实际: {success_count}"

    # 所有令牌都用完
    assert bucket.try_acquire() == False

    # 等待1.5秒，应该补充40/60 × 1.5 = 1 个令牌
    await asyncio.sleep(1.5)

    # 检查令牌数
    tokens = bucket.get_tokens()
    print(f"1.5秒后有 {tokens} 个令牌")
    assert tokens >= 1, f"1.5秒后应该至少有1个令牌，实际: {tokens}"
    assert bucket.try_acquire() == True, "应该能够获取令牌"
    assert bucket.try_acquire() == False, "应该没有更多令牌"

    print("✓ RPM限流测试通过")


async def main():
    """运行所有测试"""
    print("开始 Token Bucket 验证测试\n")

    await test_basic()
    await test_refill()
    await test_rpm()

    print("\n=== 所有测试通过 ✓ ===")


if __name__ == "__main__":
    asyncio.run(main())
