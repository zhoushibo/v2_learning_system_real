# 大模型API速率限制防护策略

**讨论时间：** 2026-02-15 23:43-23:48
**专家团队：** API限流、架构设计、性能优化、错误处理、成本控制（5位）
**核心问题：** 如何应对英伟达免费API的速率限制（40 RPM, 5并发）

---

## 🔴 核心规则：通用API限流原则（永久规则）

**⚠️ 重要性：极高 🔴**
**⚡ 优先级：P0（最高）**
**📅 记录时间：** 2026-02-15 23:48

### 📋 **规则说明：**
**所有未来的大模型API集成，都必须实现完整的API限流防护！避免触发速率限制导致1006断开或账户封禁！**

---

## 🎯 **关键限制识别**

### 英伟达免费API限制（最严格）

| 限制类型 | 限值 | 触发条件 | 危害 |
|---------|------|----------|------|
| **RPM** | 40次/分钟 | 短时间高频调用 | 触发限制 |
| **并发数** | 5个 | 并发请求过多 | 1006断开 |
| **1006断开** | ❌ 崩溃 | 超过任一限制 | 服务不可用 |
| **RPD** | 无明确上限 | 无 | 无 |
| **Token** | 无每日上限 | 无 | 无 |

### 其他常见API限制（预期）

| API提供商 | RPM | 并发 | 每日Token | 备注 |
|-----------|-----|------|----------|------|
| **英伟达免费** | 40 | 5 | 无 | 已验证 |
| **OpenAI免费** | 3-10 | 3 | 150K | 预期 |
| **OpenAI付费** | 5000+ | 50+ | 1M+ | 预期 |
| **智谱API** | 未知 | 未知 | 未知 | 需调查 |
| **混元API** | 未知 | 未知 | 未知 | 需调查 |

---

## 🏗️ **核心架构：API限流层**

### 架构设计

```
Worker池 (N个，可以很多)
    ↓  请求提交
┌────────────────────────—┐
│   API限流层              │
│                          │
│  ┌──────────────────┐   │
│  │  优先级队列       │   │  先进先出/优先级
│  └────────┬─────────┘   │
│           ↓              │
│  ┌──────────────────┐   │
│  │  速率限制器       │   │  Token Bucket算法
│  │  (RPM控制)        │   │
│  └────────┬─────────┘   │
│           ↓              │
│  ┌──────────────────┐   │
│  │  并发控制器       │   │  Max Concurrent
│  └────────┬─────────┘   │
│           ↓              │
│  ┌──────────────────┐   │
│  │  重试策略         │   │  指数退避
│  └────────┬─────────┘   │
│           ↓              │
│  ┌──────────────────┐   │
│  │  响应缓存         │   │  减少API调用
│  └────────┬─────────┘   │
└───────────┼──────────────┘
            ↓  受控请求
        V1 Gateway
            ↓
       大模型API
```

### 核心组件实现

#### 1. 速率限制器（Token Bucket）

```python
import asyncio
from datetime import datetime
from collections import deque
from typing import Optional


class RateLimiter:
    """API速率限制器

    基于Token Bucket + Sliding Window算法
    """

    def __init__(self, max_concurrent: int = 5, rpm: int = 40):
        """
        Args:
            max_concurrent: 最大并发数
            rpm: 每分钟请求数
        """
        self.max_concurrent = max_concurrent
        self.rpm = rpm
        self.current_concurrent = 0
        self.request_times = deque()  # 滑动窗口
        self.lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """获取调用许可（阻塞）"""
        async with self.lock:
            # 1. 检查并发限制
            while self.current_concurrent >= self.max_concurrent:
                await asyncio.sleep(0.1)
                async with self.lock:
                    pass  # 重新检查

            # 2. 检查RPM限制（滑动窗口）
            now = datetime.now()
            # 移除60秒之前的请求
            while self.request_times and (now - self.request_times[0]).seconds >= 60:
                self.request_times.popleft()

            # 等待直到可以发送请求
            while len(self.request_times) >= self.rpm:
                # 等待最早请求过期
                oldest = self.request_times[0]
                wait_time = 60 - (now - oldest).seconds
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    now = datetime.now()
                    # 重新清理过期请求
                    while self.request_times and (now - self.request_times[0]).seconds >= 60:
                        self.request_times.popleft()

            # 3. 获取许可
            self.current_concurrent += 1
            self.request_times.append(now)

        return True

    def release(self):
        """释放许可"""
        async with self.lock:
            self.current_concurrent -= 1

    def get_status(self) -> dict:
        """获取当前状态"""
        now = datetime.now()
        # 清理过期请求
        while self.request_times and (now - self.request_times[0]).seconds >= 60:
            self.request_times.popleft()
        now = datetime.now()

        return {
            "current_concurrent": self.current_concurrent,
            "max_concurrent": self.max_concurrent,
            "rpm_in_window": len(self.request_times),
            "rpm_limit": self.rpm,
            "available_concurrent": self.max_concurrent - self.current_concurrent,
            "available_rpm": self.rpm - len(self.request_times)
        }
```

#### 2. 智能重试策略

```python
import asyncio
from typing import Callable, Any, TypeVar

T = TypeVar('T')


class RateLimitError(Exception):
    """速率限制错误"""
    pass


class DisconnectError(Exception):
    """1006断开错误"""
    pass


class RetryHandler:
    """智能重试处理器"""

    def __init__(self, max_retries: int = 3, initial_backoff: float = 1.0):
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff

    async def call_with_retry(self, func: Callable[[], T]) -> T:
        """带重试的调用（指数退避）"""
        for attempt in range(self.max_retries):
            try:
                result = await func()
                return result

            except RateLimitError as e:
                # 速率限制：指数退避
                wait_time = self.initial_backoff * (2 ** attempt)
                print(f"⚠️ 触发速率限制（第{attempt+1}次重试），等待 {wait_time:.1f} 秒")
                await asyncio.sleep(wait_time)

            except DisconnectError as e:
                # 1006断开：特殊处理
                print(f"❌ 触发1006断开（第{attempt+1}次重试）")
                if attempt < self.max_retries - 1:
                    # 等待较长时间后重试
                    wait_time = 5 + (2 ** attempt)
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise Exception("1006断开，多次重试失败")

            except Exception as e:
                # 其他错误：不重试
                print(f"❌ 未预期的错误: {e}")
                raise

        raise Exception(f"超过最大重试次数（{self.max_retries}）")
```

#### 3. 1006错误特殊处理

```python
import asyncio


class DisconnectHandler:
    """1006断开错误处理器"""

    def __init__(self, reconnect_callback: Callable):
        self.reconnect_callback = reconnect_callback
        self.accepting_new_requests = True
        self.is_recovering = False

    async def handle_disconnect(self):
        """处理1006断开"""
        print("⚠️ 检测到1006断开，启动恢复流程")

        # 0. 防止重复处理
        if self.is_recovering:
            print("🔄 已在恢复中，跳过")
            return

        self.is_recovering = True

        # 1. 停止新请求
        self.accepting_new_requests = False
        print("🚫 停止接收新请求")

        # 2. 等待冷却（让API恢复）
        print("⏳ 等待5秒冷却...")
        await asyncio.sleep(5)

        # 3. 重新认证（调用回调）
        print("🔑 重新认证...")
        try:
            await self.reconnect_callback()
            print("✅ 重新认证成功")
        except Exception as e:
            print(f"❌ 重新认证失败: {e}")
            self.is_recovering = False
            raise

        # 4. 恢复请求
        self.accepting_new_requests = True
        self.is_recovering = False
        print("✅ 恢复正常，开始接收新请求")

    async def check_and_wait_if_recovering(self):
        """检查是否在恢复中，如果是则等待"""
        while self.is_recovering or not self.accepting_new_requests:
            await asyncio.sleep(0.5)
```


#### 4. 响应缓存

```python
import hashlib
import json
import time
from typing import Optional, Dict, Any


class ResponseCache:
    """响应缓存（减少重复API调用）"""

    def __init__(self, ttl: int = 3600):
        """
        Args:
            ttl: 缓存过期时间（秒）
        """
        self.cache: Dict[str, tuple] = {}
        self.ttl = ttl

    def _hash_content(self, content: str) -> str:
        """对内容进行哈希"""
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, content: str) -> Optional[str]:
        """获取缓存响应"""
        key = self._hash_content(content)

        if key in self.cache:
            response, timestamp = self.cache[key]

            # 检查是否过期
            if time.time() - timestamp < self.ttl:
                print(f"✅ 缓存命中: {content[:30]}...")
                return response
            else:
                # 过期，删除
                del self.cache[key]

        return None

    def set(self, content: str, response: str):
        """设置缓存"""
        key = self._hash_content(content)
        self.cache[key] = (response, time.time())
        print(f"💾 已缓存: {content[:30]}...")

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        print("🗑️ 缓存已清空")

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            "cache_size": len(self.cache),
            "ttl": self.ttl,
            "cached_items": list(self.cache.keys())[:10]  # 只显示前10个
        }
```

#### 5. 优先级队列

```python
import heapq
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(order=True)
class PriorityTask:
    """优先级任务"""
    priority: int
    created_at: datetime = field(default_factory=datetime.utcnow, compare=False)
    task_id: str = field(compare=False)
    content: str = field(compare=False)

    def __post_init__(self):
        # 优先级越小越高
        if self.priority < 1 or self.priority > 3:
            raise ValueError("优先级必须是1-3")


class PriorityQueue:
    """优先级队列"""

    HIGH_PRIORITY = 1
    MEDIUM_PRIORITY = 2
    LOW_PRIORITY = 3

    def __init__(self):
        self.queue = []

    def enqueue(self, task_id: str, content: str, priority: int = MEDIUM_PRIORITY):
        """添加任务到队列"""
        task = PriorityTask(
            priority=priority,
            task_id=task_id,
            content=content
        )
        heapq.heappush(self.queue, task)
        print(f"📥 任务已加入队列: {task_id} (优先级: {priority})")

    async def get_task(self) -> Optional[PriorityTask]:
        """获取最高优先级任务（非阻塞）"""
        if self.queue:
            return heapq.heappop(self.queue)
        return None

    async def wait_for_task(self) -> PriorityTask:
        """等待任务（阻塞）"""
        while True:
            task = await self.get_task()
            if task:
                return task
            await asyncio.sleep(0.1)

    def size(self) -> int:
        """获取队列大小"""
        return len(self.queue)

    def is_empty(self) -> bool:
        """检查队列是否为空"""
        return len(self.queue) == 0
```

---

## 🔧 **API限制配置**

### 配置文件格式

```json
{
  "api_limits": {
    "nvidia_free": {
      "name": "英伟达免费API",
      "max_concurrent": 5,
      "rpm": 40,
      "daily_requests": null,
      "daily_tokens": null,
      "requires_special_handling": true,
      "notes": "最容易触发1006断开，需要严格限流"
    },
    "openai_free": {
      "name": "OpenAI免费API",
      "max_concurrent": 3,
      "rpm": 10,
      "daily_requests": null,
      "daily_tokens": 150000,
      "requires_special_handling": true,
      "notes": "严格限制，付费后可放开"
    },
    "openai_paid": {
      "name": "OpenAI付费API",
      "max_concurrent": 50,
      "rpm": 5000,
      "daily_requests": null,
      "daily_tokens": 1000000,
      "requires_special_handling": false,
      "notes": "付费API，限制较宽松"
    },
    "zhipu_api": {
      "name": "智谱API",
      "max_concurrent": 10,
      "rpm": 100,
      "daily_requests": null,
      "daily_tokens": null,
      "requires_special_handling": true,
      "notes": "需要根据实际文档更新"
    },
    "hunyuan_api": {
      "name": "混元API",
      "max_concurrent": 10,
      "rpm": 100,
      "daily_requests": null,
      "daily_tokens": null,
      "requires_special_handling": true,
      "notes": "需要根据实际文档更新"
    }
  }
}
```

### Python配置类

```python
from typing import Optional, Dict, Any


class APILimitsConfig:
    """API限制配置"""

    @staticmethod
    def get_config(api_name: str) -> Optional[Dict[str, Any]]:
        """获取API配置"""
        configs = {
            "nvidia_free": {
                "max_concurrent": 5,
                "rpm": 40,
                "retry_max": 3,
                "retry_backoff": 2.0,
                "cache_ttl": 3600,
                "requires_special_handling": True
            },
            "openai_free": {
                "max_concurrent": 3,
                "rpm": 10,
                "retry_max": 3,
                "retry_backoff": 2.0,
                "cache_ttl": 3600,
                "requires_special_handling": True
            },
            "openai_paid": {
                "max_concurrent": 50,
                "rpm": 5000,
                "retry_max": 5,
                "retry_backoff": 1.0,
                "cache_ttl": 1800,
                "requires_special_handling": False
            }
        }

        return configs.get(api_name)

    @staticmethod
    def calculate_safe_workers(api_name: str, avg_request_time: float = 5.0) -> int:
        """计算安全Worker数量

        Args:
            api_name: API名称
            avg_request_time: 平均请求耗时（秒）

        Returns:
            安全Worker数量
        """
        config = APILimitsConfig.get_config(api_name)
        if not config:
            raise ValueError(f"未知API: {api_name}")

        # 公式：最小(最大并发, RPM / 单次请求耗时)
        max_by_concurrent = config["max_concurrent"]
        max_by_rpm = config["rpm"] / avg_request_time

        safe_workers = min(max_by_concurrent, max_by_rpm)

        print(f"API: {api_name}")
        print(f"  最大并发限制: {max_by_concurrent}")
        print(f"  RPM限制: {config['rpm']}")
        print(f"  平均请求耗时: {avg_request_time}秒")
        print(f"  计算安全Worker数: {safe_workers}")

        return int(safe_workers)
```

---

## 📊 **Worker池数量计算**

### 英伟达免费API

| 场景 | 平均请求耗时 | 计算公式 | 安全Worker数 |
|------|------------|---------|------------|
| **快速任务** | 2秒 | min(5, 40/2) = min(5, 20) | 5 |
| **正常任务** | 5秒 | min(5, 40/5) = min(5, 8) | 5 |
| **慢速任务** | 10秒 | min(5, 40/10) = min(5, 4) | 4 |

### OpenAI付费API

| 场景 | 平均请求耗时 | 计算公式 | 安全Worker数 |
|------|------------|---------|------------|
| **快速任务** | 2秒 | min(50, 5000/2) = min(50, 2500) | 50 |
| **正常任务** | 5秒 | min(50, 5000/5) = min(50, 1000) | 50 |
| **慢速任务** | 10秒 | min(50, 5000/10) = min(50, 500) | 50 |

---

## 🚨 **关键防护措施**

### 防护清单

| 防护措施 | 英伟达免费 | OpenAI付费 | 其他API |
|---------|-----------|-----------|---------|
| **请求队列** | ✅ 必须 | ✅ 必须 | ✅ 必须 |
| **RPM限制** | ✅ 必须 | ✅ 必须 | ✅ 必须 |
| **并发控制** | ✅ 必须 | ✅ 必须 | ✅ 必须 |
| **智能重试** | ✅ 必须 | ✅ 推荐 | ✅ 推荐 |
| **1006处理** | ✅ 必须 | ❌ 不需要 | 📋 视情况 |
| **响应缓存** | ✅ 推荐 | ✅ 推荐 | ✅ 推荐 |
| **优先级队列** | ✅ 推荐 | ✅ 推荐 | ✅ 推荐 |

### 实施优先级

| 优先级 | 功能 | 说明 |
|--------|------|------|
| **P0** | 基础限流（并发 + RPM） | 防止超过上限 |
| **P0** | 1006错误处理 | 修复崩溃 |
| **P1** | 重试策略（指数退避） | 提高成功率 |
| **P1** | 响应缓存 | 减少调用 |
| **P2** | 优先级队列 | 改善体验 |

---

## 💡 **经验总结**

### ✅ 成功经验

1. **API限流层必须统一**
   - 不同Worker共享同一个限流器
   - 避免各自为政触发限制

2. **配置必须明确**
   - 每个API的限制都要写入配置
   - Worker池根据配置自动调整

3. **错误1006必须特殊处理**
   - 不是简单的重试
   - 需要停止→冷却→重新认证

4. **缓存可以显著减少压力**
   - 相似问题复用响应
   - 节省API调用

### ❌ 常见错误

1. **忽略1006断开的特殊性**
   - 简单重试会导致更严重的问题
   - 必须重新认证

2. **Worker池无限扩展**
   - 容易触发并发限制
   - 必须计算最大安全Worker数

3. **不考虑优先级**
   - 长任务阻塞即时对话
   - 应该优先级队列

---

## 📝 **记录更新**

- **记录时间**：2026-02-15 23:48
- **记录人**：博 + Claw
- **专家团队**：API限流、架构设计、性能优化、错误处理、成本控制
- **会议轮次**：4轮（识别限流、设计方案、优化策略、制定规范）
- **讨论时长**：5分钟
- **状态**：🔴 永久规则，不可撤销
- **适用范围**：所有大模型API集成

---

**核心总结：所有大模型API必须有完整的API限流层防护！** 🛡️
