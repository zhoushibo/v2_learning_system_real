# OpenClaw 2.0 - 开发规范制定

**文档时间：** 2026-02-15 21:55
**会议轮次：** 第四轮专家会议（开发规范）

---

## 🎯 开发规范目标

1. **Git工作流标准** - 清晰的分支管理
2. **编码规范统一** - Python最佳实践
3. **测试覆盖要求** - ≥80%覆盖率
4. **CI/CD自动化** - 自动检查和部署
5. **安全规范** - 防止漏洞
6. **文档完整** - 易于维护

---

## 📋 Git工作流规范

### 分支策略

```
main (生产分支)
  ↓ 只合并release分支
  
release/v2.0.0 (发布分支)
  ↓ 从develop分出
  
develop (开发主分支)
  ↓ 合并所有feature分支
  ↓ 测试通过
  
feature/gateway (功能分支)  ← 你的工作分支
feature/task-queue
feature/worker-pool

bugfix/worker-crash (修复分支)

hotfix/security-patch (紧急修复，从main分出)
```

---

### 分支命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| **功能** | `feature/模块-功能描述` | `feature/gateway-async-submit` |
| **修复** | `bugfix/问题描述` | `bugfix/worker-memory-leak` |
| **紧急修复** | `hotfix/问题描述` | `hotfix/redis-timeout` |
| **发布** | `release/vX.Y.Z` | `release/v2.0.0` |
| **文档** | `docs/文档类型` | `docs/api-reference` |
| **测试** | `test/测试范围` | `test/concurrent-tasks` |

---

### 提交信息规范

**Conventional Commits格式：**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）：**
- `feat` - 新功能
- `fix` - Bug修复
- `docs` - 文档
- `style` - 格式
- `refactor` - 重构
- `perf` - 性能优化
- `test` - 测试
- `build` - 构建
- `ci` - CI/CD
- `chore` - 其他

**作用域（scope）：**
- `gateway` - Gateway模块
- `queue` - 任务队列
- `worker` - Worker池
- `websocket` - WebSocket推送
- `store` - 结果存储
- `api` - API接口
- `ui` - 前端界面

**示例：**

```bash
# ✅ 好的提交
git commit -m "feat(gateway): 实现异步任务提交功能

- 添加TaskQueue集成
- 实现任务分类逻辑
- 添加超时保护
响应时间从>10分钟降低到<50ms

Closes #1"
```

```bash
# ✅ 修复提交
git commit -m "fix(worker): 修复Worker内存泄漏问题

添加内存限制：
- Worker内存上限500MB
- 超标自动重启

Fixes #42"
```

```bash
# ✅ 性能优化
git commit -m "perf(queue): 优化任务队列性能

使用Redis Streams替代List：
- 吞吐量提升10倍
- 支持优先级队列
- 支持任务超时

Benchmark: https://..."
```

---

### Pull Request规范

**PR模板：**

```markdown
## 📋 描述
简要说明这个PR做什么

## 🎯 变更类型
- [ ] 新功能
- [ ] Bug修复
- [ ] 性能优化
- [ ] 文档更新
- [ ] 重构

## 🧪 测试
- [ ] 单元测试已添加/更新
- [ ] 集成测试已通过
- [ ] 性能测试已通过
- [ ] 手动测试已通过

## ✅ 检查清单
- [ ] 代码符合PEP8
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] 无敏感信息泄露

## 📝 相关Issue
Closes #(issue号)

## 📸 截图（如适用）
```

**PR Checklist（必须全部通过）：**
- [ ] 单元测试覆盖率 ≥80%
- [ ] 通过所有CI/CD检查
- [ ] 代码审查通过
- [ ] 文档已更新
- [ ] 无安全漏洞

---

## 🔧 编码规范

### Python编码标准（PEP8）

```python
# ✅ 好的代码
from typing import Optional, List
import asyncio
import logging

from .config import get_config
from .logger import get_logger

logger = get_logger(__name__)


class TaskQueue:
    """任务队列管理器
    
    职责：
    - 任务提交
    - 任务调度
    - 任务超时控制
    """
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.max_queue_length = 10000
        
        # 队列配置
        self.queues = {
            "short": "tasks:short",
            "long": "tasks:long",
            "priority": "tasks:priority"
        }
    
    async def submit_task(self, task: Task) -> str:
        """提交任务到队列
        
        Args:
            task: 任务对象
            
        Returns:
            任务ID
            
        Raises:
            QueueFullError: 队列已满
            TaskValidationError: 任务验证失败
        """
        # 1. 验证任务
        self._validate_task(task)
        
        # 2. 选择队列
        queue = self._select_queue(task)
        
        # 3. 提交到Redis
        task_id = await self._submit_to_redis(queue, task)
        
        # 4. 发布事件
        await self._publish_event(queue, task_id)
        
        logger.info(f"任务 {task_id} 已提交到 {queue}")
        return task_id
    
    def _validate_task(self, task: Task) -> None:
        """验证任务"""
        if not task.id:
            raise TaskValidationError("任务ID不能为空")
        
        if not task.payload:
            raise TaskValidationError("任务负载不能为空")
        
        if len(task.payload) > MAX_PAYLOAD_SIZE:
            raise TaskValidationError(f"任务负载过大: {len(task.payload)} bytes")


# ❌ 错误的代码
class taskqueue:  # 应该PascalCase
    def __init__(self):
        self.redis = Redis(self.host, self.port, self.db)  # 配置硬编码
        self.maxsize = 10000  # 常量应该全大写
    
    async def submit(self, t):  # 函数名太短
        if t.payload.size > 10000000:  # 魔法值
            raise Exception("too big")  # 异常不具体
        
        res = self.xadd(..., {'task': json.dumps(t)})  # 行太长
        return res
```

---

### 函数规范

```python
# ✅ 好的函数
async def submit_task_with_retry(
    self,
    task: Task,
    max_retries: int = 3,
    backoff: int = 60
) -> Tuple[str, int]:
    """提交任务带重试
    
    Args:
        task: 要提交的任务
        max_retries: 最大重试次数，默认3次
        backoff: 重试间隔（秒），默认60秒
        
    Returns:
        (task_id, attempt_count)
        
    Raises:
        TaskSubmissionError: 重试后仍失败
        
    Example:
        >>> task_queue = TaskQueue(redis)
        >>> task_id, attempts = await task_queue.submit_task_with_retry(
        ...     task, max_retries=2
        ... )
        >>> print(f"任务{task_id}在{attempts}次后提交成功")
    """
    for attempt in range(max_retries + 1):
        try:
            task_id = await self.submit_task(task)
            return task_id, attempt + 1
            
        except QueueFullError as e:
            if attempt == max_retries:
                raise TaskSubmissionError(f"重试{max_retries}次后仍失败: {e}")
            
            logger.warning(f"任务提交失败，{backoff}秒后重试...", e)
            await asyncio.sleep(backoff)


# ❌ 错误的函数
async def execute(t, timeout=300):
    """执行任务"""  # 缺少docstring
    
    # 函数太长（>50行）
    result = None
    try:
        conn = await redis.connect()
        queue = conn.get_queue()
        if queue.full():
            # ...很多逻辑
            pass
        # ...还有更多
        # ...超过50行
    except Exception as e:  # 异常捕获太宽泛
        logger.error(e)
    finally:
        await conn.close()
    
    return result
```

---

### 异常处理规范

```python
# ✅ 好的异常处理
async def execute_task(self, task: Task) -> Result:
    """执行任务（多层异常捕获）"""
    try:
        # 执行任务
        result = await self._do_execute(task)
        return Result(success=True, data=result)
        
    except TimeoutError as e:
        logger.warning(f"任务 {task.id} 超时", e)
        return Result(
            success=False,
            error="timeout",
            message="任务执行超时"
        )
        
    except MemoryError as e:
        logger.error(f"任务 {task.id} 内存溢出", e)
        self._cleanup_memory()
        return Result(
            success=False,
            error="memory_limit",
            message="任务内存超出限制"
        )
        
    except QueueFullError as e:
        logger.warning(f"任务 {task.id} 队列已满", e)
        # 自动重试
        return await self._retry_task(task)
        
    except TaskValidationError as e:
        logger.error(f"任务 {task.id} 验证失败", e)
        return Result(
            success=False,
            error="validation",
            message=str(e)
        )
        
    except Exception as e:
        logger.error(f"任务 {task.id} 未知异常", e)
        return Result(
            success=False,
            error="unknown",
            message=f"任务执行失败: {e}"
        )


# ❌ 错误的异常处理
async def execute_task(self, task):
    """执行任务（异常处理不当）"""
    try:
        result = await self._do_execute(task)
        return result
    except:  # ⚠️ 太宽泛，隐藏错误
        return {"error": True}  # ⚠️ 没有日志
```

---

## 🧪 测试规范

### 测试覆盖要求

| 模块 | 最低覆盖率 | 推荐覆盖率 |
|------|-----------|------------|
| **Gateway** | 90% | 95% |
| **TaskQueue** | 85% | 90% |
| **WorkerPool** | 80% | 85% |
| **ResultStore** | 85% | 90% |
| **WebSocket** | 80% | 85% |

**总体覆盖率：≥80%**

---

### 单元测试示例

```python
# tests/unit/test_task_queue.py
import pytest
from task_queue import TaskQueue
from task import Task
from exceptions import QueueFullError


class TestTaskQueue:
    """任务队列测试"""
    
    @pytest.fixture
    async def task_queue(self, redis_mock):
        """测试 fixture"""
        return TaskQueue(redis_mock)
    
    @pytest.fixture
    def sample_task(self):
        """示例任务"""
        return Task(
            id="test-001",
            type="short",
            payload={"query": "test"},
            priority=5
        )
    
    @pytest.mark.asyncio
    async def test_submit_task_success(self, task_queue, sample_task):
        """测试任务提交成功"""
        # 提交任务
        task_id = await task_queue.submit_task(sample_task)
        
        # 断言
        assert task_id is not None
        assert task_id == sample_task.id
    
    @pytest.mark.asyncio
    async def test_submit_task_queue_full(self, task_queue, sample_task):
        """测试队列已满"""
        # 模拟队列已满
        task_queue._get_queue_length = lambda: 10000 + 1
        
        # 提交任务应该抛出异常
        with pytest.raises(QueueFullError):
            await task_queue.submit_task(sample_task)
    
    @pytest.mark.asyncio
    async def test_validate_task_empty_id(self, task_queue):
        """测试任务验证（空ID）"""
        # 创建无效任务
        invalid_task = Task(id="", type="short", payload={})
        
        # 应该抛出验证错误
        with pytest.raises(TaskValidationError):
            await task_queue.submit_task(invalid_task)
    
    @pytest.mark.parametrize("task_type,expected_queue", [
        ("short", "tasks:short"),
        ("long", "tasks:long"),
        ("priority", "tasks:priority"),
    ])
    @pytest.mark.asyncio
    async def test_queue_selection(self, task_queue, sample_task, task_type, expected_queue):
        """测试队列选择逻辑"""
        # 设置任务类型
        sample_task.type = task_type
        
        # 提交任务
        await task_queue.submit_task(sample_task)
        
        # 验证使用了正确的队列
        selected_queue = task_queue._select_queue(sample_task)
        assert selected_queue == expected_queue
```

---

### 集成测试示例

```python
# tests/integration/test_full_workflow.py
import pytest
from gateway import OpenClawGateway
from task_queue import TaskQueue
from worker_pool import WorkerPool


@pytest.mark.asyncio
async def test_full_workflow_integration(redis, websocket_mock):
    """测试完整工作流"""
    # 1. 初始化组件
    task_queue = TaskQueue(redis)
    worker_pool = WorkerPool(task_queue)
    gateway = OpenClawGateway(task_queue, worker_pool, websocket_mock)
    
    # 2. 启动Worker池
    await worker_pool.start()
    
    # 3. 提交任务
    message = Message(
        session_id="session-001",
        content="帮我处理1000个文件",
        priority=5
    )
    
    response = await gateway.handle_message(message)
    
    # 4. 验证响应
    assert response.status == "submitted"
    assert response.task_id is not None
    assert response.response_time < 0.05  # <50ms
    
    # 5. 等待任务完成
    result = await worker_pool.wait_for_task(response.task_id, timeout=60)
    
    # 6. 验证结果
    assert result.status == "completed"
    assert result.data is not None
    
    # 7. 清理
    await worker_pool.stop()
```

---

## 🚀 CI/CD配置

### GitHub Actions配置

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements_test.txt
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Format check with black
      run: |
        pip install black
        black --check .
    
    - name: Type check with mypy
      run: |
        pip install mypy
        mypy . --config-file mypy.ini
    
    - name: Test with pytest
      run: |
        pytest tests/ --cov=openclaw_v2 --cov-report=xml --cov-report=html
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security scan
      uses: PyCQA/bandit-action@master
      with:
        path: ./
    
    - name: Check for secrets
      uses: trufflesecurity/trufflehog@main
      with:
        path: ./
```

---

## 🔒 安全规范

### 敏感信息处理

```python
# ✅ 好的代码
from config import get_config
from cryptography.fernet import Fernet

config = get_config()

# 从环境变量读取
redis_password = os.environ.get("REDIS_PASSWORD")
api_key = os.environ.get("OPENAI_API_KEY")

# 加密存储
def encrypt_data(data: str) -> str:
    """加密数据"""
    key = os.environ.get("ENCRYPTION_KEY")
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

# 日志中不记录敏感信息
logger.info(f"用户 {user_id} 执行搜索")  # ✅ 好
# logger.info(f"用户密码: {password}")  # ❌ 禁止

# ❌ 错误的代码
redis_password = "my_secret_password"  # 硬编码 ❌
api_key = "sk-1234567890"  # 硬编码 ❌

logger.debug(f"完整请求: {request}")  # 可能包含敏感信息 ❌
```

---

### 输入验证

```python
# ✅ 好的代码
from pydantic import BaseModel, validator, constr

class TaskPayload(BaseModel):
    """任务负载"""
    
    query: constr(max_length=10000)
    session_id: constr(max_length=100)
    priority: int = 5
    
    @validator("priority")
    def validate_priority(cls, v):
        if not 0 <= v <= 10:
            raise ValueError("优先级必须在0-10之间")
        return v


async def handle_message(message: dict):
    """处理消息"""
    # 验证输入
    payload = TaskPayload(**message)
    
    # 执行...
    pass

# ❌ 错误的代码
async def handle_message(message: dict):
    """处理消息（无验证）"""
    query = message["query"]  # 可能不存在 ❌
    priority = message["priority"]  # 可能不是数字 ❌
```

---

## 📚 文档规范

### 代码文档

```python
# ✅ 好的文档
class TaskQueue:
    """任务队列管理器
    
    职责：
    - 接收所有任务
    - 任务分类（长/短/优先级）
    - 任务调度
    - 超时控制
    
    配置：
    - max_queue_length: 最大队列长度（10000）
    - max_ttl: 任务最大存活时间（7天）
    
    性能：
    - 吞吐量：>10000 tasks/sec
    - 延迟：<10ms（本地Redis）
    - 可靠率：99.99%
    
    示例：
        >>> queue = TaskQueue(redis_client)
        >>> task_id = await queue.submit_task(task)
        >>> print(f"任务已提交: {task_id}")
    """
    
    def __init__(self, redis_client: Redis, config: Config):
        """初始化任务队列
        
        Args:
            redis_client: Redis客户端实例
            config: 配置对象
        
        Raises:
            ConnectionError: Redis连接失败
        """
        pass

# ❌ 错误的文档
class TaskQueue:
    """任务队列"""
    
    def __init__(self, redis_client):
        pass
```

---

## 📊 项目状态跟踪

### 开发进度

| 组件 | 状态 | 进度 | 预计完成 |
|------|------|------|----------|
| **Gateway** | 🔄 开发中 | 60% | Day 2 |
| **TaskQueue** | 🔄 开发中 | 40% | Day 1 |
| **WorkerPool** | ⏳ 未开始 | 0% | Day 3 |
| **ResultStore** | ⏳ 未开始 | 0% | Day 4 |
| **WebSocket** | ⏳ 未开始 | 0% | Day 5 |

---

**文档完成时间：** 2026-02-15 22:00
**总耗时：** 5分钟
**规范完成度：** 100% ✅
