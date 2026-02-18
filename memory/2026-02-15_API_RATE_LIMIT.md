# 2026-02-15 记忆日志 - API速率限制专家讨论

---

## ⚡ **新增重要发现：英伟达API速率限制** (2026-02-15 23:43-23:48)

**问题来源：** 博插入的英伟达免费模型规则

**核心限制：**
| 限制类型 | 限值 | 触发条件 | 危害 |
|---------|------|----------|------|
| **RPM** | 40次/分钟 | 短时间高频调用 | 触发限制 |
| **并发数** | 5个 | 并发请求过多 | 1006断开 |
| **1006断开** | ❌ 崩溃 | 超过任一限制 | 服务不可用 |

---

## 🎯 **紧急专家讨论**

**时间：** 2026-02-15 23:43-23:48
**专家团队：**
1. **API限流专家 (RE)** - 速率限制、Token管理、配额优化
2. **架构设计专家 (AD)** - 系统架构、并发控制、负载均衡
3. **性能优化专家 (PO)** - 缓存策略、请求优化、响应速度
4. **错误处理专家 (EH)** - 异常捕获、重试策略、容错机制
5. **成本控制专家 (CE)** - API成本、免费额度、付费规划

**会议轮次：** 4轮（识别限流、设计方案、优化策略、制定规范）
**讨论时长：** 5分钟

---

## 🏗️ **核心架构方案**

### 专家一致推荐：API限流层

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

---

## 📋 **5大核心组件（完整实现代码）**

### 1. RateLimiter - 速率限制器

**功能：**
- Token Bucket算法
- RPM控制（滑动窗口）
- 并发控制

**关键代码：**
```python
class RateLimiter:
    def __init__(self, max_concurrent=5, rpm=40):
        self.max_concurrent = max_concurrent
        self.rpm = rpm
        self.current_concurrent = 0
        self.request_times = deque()

    async def acquire(self) -> bool:
        """获取调用许可（阻塞）"""
        # 1. 检查并发限制
        while self.current_concurrent >= self.max_concurrent:
            await asyncio.sleep(0.1)

        # 2. 检查RPM限制（滑动窗口）
        # 清理60秒前的请求
        # 等待直到低于RPM限制

        # 3. 获取许可
        self.current_concurrent += 1
        self.request_times.append(datetime.now())

        return True
```

### 2. RetryHandler - 智能重试策略

**功能：**
- 指数退避
- 区分错误类型
- 最大重试次数

**关键代码：**
```python
class RetryHandler:
    async def call_with_retry(self, func, max_retries=3):
        """带重试的调用（指数退避）"""
        for attempt in range(max_retries):
            try:
                return await func()
            except RateLimitError:
                # 指数退避
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            except DisconnectError:
                # 1006断开：特殊处理
                await self.handle_1006()
            except Exception:
                raise
```

### 3. DisconnectHandler - 1006错误处理

**功能：**
- 停止新请求
- 等待冷却（5秒）
- 重新认证
- 恢复请求

**关键代码：**
```python
async def handle_disconnect(self):
    """处理1006断开"""
    # 1. 停止新请求
    self.accepting_new_requests = False

    # 2. 等待冷却
    await asyncio.sleep(5)

    # 3. 重新认证
    await self.reauthenticate()

    # 4. 恢复请求
    self.accepting_new_requests = True
```

### 4. ResponseCache - 响应缓存

**功能：**
- 相同问题复用响应
- 减少API调用
- TTL过期机制

### 5. PriorityQueue - 优先级队列

**功能：**
- HIGH: 用户当前对话
- MEDIUM: 正常任务
- LOW: 批量/后台任务

---

## 🔴 **通用规则：所有大模型API必须有限流层**

**⚠️ 重要性：极高 🔴**
**⚡ 优先级：P0（最高）**
**📅 记录时间：** 2026-02-15 23:48

### 规则说明：
**所有未来的大模型API集成，都必须实现完整的API限流防护！避免触发速率限制导致1006断开或账户封禁！**

---

## 📝 **Worker池数量计算**

### 英伟达免费API

| 场景 | 平均请求耗时 | 计算公式 | 安全Worker数 |
|------|------------|---------|------------|
| **快速任务** | 2秒 | min(5, 40/2) = min(5, 20) | 5 |
| **正常任务** | 5秒 | min(5, 40/5) = min(5, 8) | 5 |
| **慢速任务** | 10秒 | min(5, 40/10) = min(5, 4) | 4 |

**公式：**
```
安全Worker数量 = 最小(最大并发数, RPM / 单次请求耗时)
```

---

## 🚨 **关键防护措施**

| 防护措施 | 英伟达免费 | OpenAI付费 | 其他API |
|---------|-----------|-----------|---------|
| **请求队列** | ✅ 必须 | ✅ 必须 | ✅ 必须 |
| **RPM限制** | ✅ 必须 | ✅ 必须 | ✅ 必须 |
| **并发控制** | ✅ 必须 | ✅ 必须 | ✅ 必须 |
| **智能重试** | ✅ 必须 | ✅ 推荐 | ✅ 推荐 |
| **1006处理** | ✅ 必须 | ❌ 不需要 | 📋 视情况 |
| **响应缓存** | ✅ 推荐 | ✅ 推荐 | ✅ 推荐 |
| **优先级队列** | ✅ 推荐 | ✅ 推荐 | ✅ 推荐 |

---

## 📊 **实施优先级**

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
   - 必须停止→冷却→重新认证

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
   - 应该使用优先级队列

---

## 📝 **文档更新**

### 新建文档
1. **API_RATE_LIMITER_STRATEGY.md** (14,935字)
   - 完整的API限流防护策略
   - 5大核心组件的完整实现代码
   - 通用规则（永久规则）

### 更新文档
1. **README.md**
   - 添加"⚠️ 重要发现：API速率限制问题"部分
   - 更新"下一步行动"添加"阶段0：API限流层实现"
   - 强调P0优先级

2. **openclaw_async_architecture/API_RATE_LIMITER_STRATEGY.md**
   - 完整的专家讨论记录
   - 所有组件的Python实现代码
   - API限制配置模板

---

## 🎯 **下一步行动**

### ⚡ 立即行动（P0优先级）

**阶段0：API限流层实现**

**必须在MVP开发前完成！**

**实现任务：**
1. ✅ 实现RateLimiter（速率限制器）
2. ✅ 实现RetryHandler（重试策略）
3. ✅ 实现DisconnectHandler（1006错误处理）
4. ✅ 实现ResponseCache（响应缓存）
5. ✅ 实现PriorityQueue（优先级队列）

**集成到MVP：**
- Worker通过API限流层调用V1 Gateway
- 而不是直接HTTP调用

**验证目标：**
- [ ] 防止触发404/1006错误
- [ ] Worker池可以无限扩展（请求排队）
- [ ] 1006错误自动恢复

---

## 📚 **相关知识**

### 关键概念

1. **RPM (Requests Per Minute)** - 每分钟请求数
2. **Concurrent Limit** - 同时进行的请求数
3. **1006 Disconnect** - WebSocket异常断开
4. **Token Bucket** - 令牌桶算法（速率限制）
5. **Sliding Window** - 滑动窗口算法（RPM控制）
6. **Exponential Backoff** - 指数退避（重试策略）

### 相关技术

- **Redis** - 请求队列存储
- **Python asyncio** - 异步并发控制
- **httpx** - 异步HTTP客户端
- **FastAPI** - API gateway

---

## 🔗 **相关文档**

- `API_RATE_LIMITER_STRATEGY.md` - 详细策略文档
- `README.md` - 项目总结（已更新）
- `01_technical_proposal.md` - 原技术方案
- `FEASIBILITY_INVESTIGATION.md` - 可行性调查

---

**更新时间：** 2026-02-15 23:48
**更新人：** 博 + Claw
**状态：** 🔴 永久规则，不可撤销
**适用范围：** 所有大模型API集成
