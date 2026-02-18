# OpenClaw 2.0 异步架构 - 技术方案

**项目时间：** 2026-02-15 21:36
**启动原因：** 解决长任务>10分钟导致界面卡死问题
**目标：** 完全异步架构，主进程永不阻塞

---

## 🎯 核心目标

1. **主进程永不阻塞** - 所有任务异步执行
2. **界面始终响应** - 无任务长度限制
3. **实时进度反馈** - WebSocket推送
4. **任务可管理** - 暂停/取消/重试
5. **高性能** - 支持数千并发任务

---

## 🏗️ 架构设计

### 当前架构（问题）
```
用户消息
    ↓
OpenClaw主进程
    ↓ 等待结果（阻塞）⚠️
    ↓ LLM调用/工具调用（可能很久）
    ↓ 返回结果
    ⏰ >10分钟 → 界面卡死 💀
```

### 新架构（OpenClaw 2.0）
```
用户消息
    ↓
OpenClaw Gateway (主进程)
    ├─ 立即接收消息
    ├─ 提交到任务队列（非阻塞）✅
    ├─ 返回任务ID（<50ms）
    └─ 继续处理下一条消息

任务队列 (Redis)
    ├─ 长任务队列
    ├─ 短任务队列
    └─ 优先级队列
        ↓
    Worker Pool (独立进程)
        ├─ 长任务Worker
        ├─ 短任务Worker
        └─ 动态扩缩容
            ↓
        执行任务（独立隔离）
            ↓
        结果存储 (Redis)
            ↓
        WebSocket推送 → 用户界面 ✅
```

---

## 📦 核心组件

### 1. Gateway (网关层)

**职责：**
- 接收所有用户消息
- 快速任务分类（长/短）
- 提交到队列（<50ms）
- 立即返回任务ID
- WebSocket连接管理

**技术栈：**
- FastAPI (高性能HTTP)
- WebSocket (实时推送)
- Redis (任务分发)

```python
class OpenClawGateway:
    """OpenClaw网关
    
    核心特性：
    - 永不阻塞（所有异步）
    - 极速响应（<50ms）
    - 任务调度
    """
    
    def __init__(
        self,
        task_queue: TaskQueue,
        worker_pool: WorkerPool,
        websocket_manager: WebSocketManager
    ):
        self.task_queue = task_queue
        self.worker_pool = worker_pool
        self.ws_manager = websocket_manager
    
    async def handle_message(self, message: Message):
        """处理消息（极速，<50ms）"""
        # 分类任务
        task_type = classify_task(message)
        
        # 创建任务
        task = Task(
            id=generate_id(),
            type=task_type,
            payload=message,
            priority=message.priority,
            estimated_time=estimate_time(message)
        )
        
        # 提交到队列（异步）
        await self.task_queue.submit(task)
        
        # ⚡ 立即返回（不等待执行）
        return TaskResponse(
            task_id=task.id,
            status="submitted",
            estimated_time=task.estimated_time
        )
```

---

### 2. Task Queue (任务队列)

**职责：**
- 接收所有任务
- 任务分类（长/短/优先级）
- 任务调度
- 超时控制

**技术栈：**
- Redis Streams (高性能队列)
- Redis Pub/Sub (事件通知)
- Redis Sorted Set (优先级)

```python
class TaskQueue:
    """任务队列管理器
    
    分三个队列：
    - 短任务队列（<1分钟）
    - 长任务队列（>=1分钟）
    - 高优先级队列
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.queues = {
            "short": "tasks:short",      # 短任务
            "long": "tasks:long",        # 长任务
            "priority": "tasks:priority" # 高优先
        }
    
    async def submit(self, task: Task):
        """提交任务到队列"""
        # 根据类型选择队列
        if task.priority > 8:
            queue = self.queues["priority"]
        elif task.estimated_time < 60:
            queue = self.queues["short"]
        else:
            queue = self.queues["long"]
        
        # 提交到Redis Stream
        task_data = json.dumps(task.dict())
        await self.redis.xadd(queue, {"task": task_data})
        
        # 发布事件（通知Worker）
        await self.redis.publish(f"tasks:incoming:{queue}", task.id)
    
    async def get_task(self, worker_type: str) -> Optional[Task]:
        """Worker获取任务（阻塞）"""
        queue = self.queues[worker_type]
        data = await self.redis.xread({queue: "$"}, count=1, block=5000)
        
        if data:
            _, messages = data[0]
            for msg_id, msg in messages:
                task_data = json.loads(msg[b"task"])
                await self.redis.xdel(queue, msg_id)
                return Task(**task_data)
        
        return None
```

---

### 3. Worker Pool (工作池)

**职责：**
- 独立进程执行任务
- 任务隔离
- 资源限制
- 自动恢复

**技术栈：**
- Multiprocessing (Python)
- Process Pool (进程池)
- Resource Manager (资源控制)

```python
class WorkerPool:
    """Worker池管理器
    
    特性：
    - 长任务Worker（独立进程）
    - 短任务Worker（协程池）
    - 动态扩缩容
    - 崩溃自动恢复
    """
    
    POOL_TYPES = {
        "long": {
            "worker_class": LongTaskWorker,
            "min_workers": 2,
            "max_workers": 10,
            "max_lifetime": 3600  # 1小时
        },
        "short": {
            "worker_class": ShortTaskWorker,
            "min_workers": 5,
            "max_workers": 20,
            "max_lifetime": 300   # 5分钟
        }
    }
    
    def __init__(self, task_queue: TaskQueue, result_store: ResultStore):
        self.task_queue = task_queue
        self.result_store = result_store
        self.workers = {}
        self.monitoring = True
    
    async def start(self):
        """启动Worker池"""
        for pool_type, config in self.POOL_TYPES.items():
            self.workers[pool_type] = []
            
            # 启动最小数量Worker
            for i in range(config["min_workers"]):
                worker = self._create_worker(pool_type, i)
                await worker.start()
                self.workers[pool_type].append(worker)
        
        # 启动监控协程
        asyncio.create_task(self._monitor_workers())
    
    async def _monitor_workers(self):
        """监控Worker健康状态"""
        while self.monitoring:
            for pool_type, workers in self.workers.items():
                config = self.POOL_TYPES[pool_type]
                
                # 动态扩缩容
                queue_length = await self.task_queue.get_length(pool_type)
                target_workers = min(
                    max(queue_length // 10, config["min_workers"]),
                    config["max_workers"]
                )
                
                # 扩容
                if len(workers) < target_workers:
                    for i in range(target_workers - len(workers)):
                        worker = self._create_worker(pool_type, len(workers))
                        await worker.start()
                        workers.append(worker)
                
                # 缩容
                elif len(workers) > target_workers:
                    for _ in range(len(workers) - target_workers):
                        worker = workers.pop()
                        await worker.stop()
            
            await asyncio.sleep(30)  # 每30秒检查一次


class BaseWorker:
    """Worker基类"""
    
    def __init__(
        self,
        worker_id: str,
        task_queue: TaskQueue,
        result_store: ResultStore
    ):
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.result_store = result_store
        self.running = False
    
    async def start(self):
        """启动Worker"""
        self.running = True
        asyncio.create_task(self._work_loop())
    
    async def _work_loop(self):
        """工作循环"""
        while self.running:
            # 获取任务（阻塞等待）
            task = await self.task_queue.get_task(self.worker_type)
            
            if task:
                await self._execute_task(task)
    
    async def _execute_task(self, task: Task):
        """执行任务"""
        try:
            # 更新状态
            await self.result_store.update_status(task.id, "running")
            
            # 执行任务
            result = await self._do_execute(task)
            
            # 保存结果
            await self.result_store.save_result(task.id, result)
            
        except Exception as e:
            # 任务失败
            await self.result_store.save_error(task.id, str(e))


class LongTaskWorker(BaseWorker):
    """长任务Worker（独立进程）"""
    
    worker_type = "long"
    
    async def _do_execute(self, task: Task):
        """执行长任务（在新进程中）"""
        # 使用sessions_spawn隔离执行
        result = await sessions_spawn(
            task=task.payload,
            cleanup="delete",
            timeout=86400  # 24小时
        )
        return result


class ShortTaskWorker(BaseWorker):
    """短任务Worker（协程池）"""
    
    worker_type = "short"
    
    async def _do_execute(self, task: Task):
        """执行短任务（直接执行）"""
        # 直接执行LLM调用
        result = await call_llm(task.payload)
        return result
```

---

### 4. Result Store (结果存储)

**职责：**
- 存储任务结果
- 状态管理
- 过期清理

**技术栈：**
- Redis (结果缓存)
- SQLite (持久化)

```python
class ResultStore:
    """结果存储管理器"""
    
    def __init__(self, redis_client, sqlite_db):
        self.redis = redis_client
        self.sqlite = sqlite_db
    
    async def save_result(self, task_id: str, result: Any):
        """保存结果"""
        # Redis缓存（24小时）
        await self.redis.setex(
            f"result:{task_id}",
            86400,
            json.dumps(result)
        )
        
        # SQLite持久化
        await self.sqlite.execute(
            "INSERT INTO results (task_id, result, created_at) VALUES (?, ?, ?)",
            (task_id, json.dumps(result), now())
        )
    
    async def get_result(self, task_id: str) -> Optional[dict]:
        """获取结果"""
        # 先查Redis
        cached = await self.redis.get(f"result:{task_id}")
        if cached:
            return json.loads(cached)
        
        # 查SQLite
        row = await self.sqlite.fetch_one(
            "SELECT result FROM results WHERE task_id = ?",
            (task_id,)
        )
        
        if row:
            return json.loads(row["result"])
        
        return None
```

---

### 5. WebSocket Manager (实时推送)

**职责：**
- 管理WebSocket连接
- 任务进度推送
- 结果推送

```python
class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.connections = {}  # session_id -> WebSocket
    
    async def connect(self, session_id: str, websocket: WebSocket):
        """新连接"""
        self.connections[session_id] = websocket
    
    async def disconnect(self, session_id: str):
        """断开连接"""
        if session_id in self.connections:
            del self.connections[session_id]
    
    async def send_progress(self, task_id: str, progress: dict):
        """推送进度"""
        task = await get_task_info(task_id)
        session_id = task.session_id
        
        if session_id in self.connections:
            await self.connections[session_id].send_json({
                "type": "progress",
                "task_id": task_id,
                "data": progress
            })
    
    async def send_result(self, task_id: str, result: dict):
        """推送结果"""
        task = await get_task_info(task_id)
        session_id = task.session_id
        
        if session_id in self.connections:
            await self.connections[session_id].send_json({
                "type": "result",
                "task_id": task_id,
                "data": result
            })
```

---

## 📊 性能指标

| 指标 | 目标 | 当前 | 改善 |
|------|------|------|------|
| **响应时间** | <50ms | 可能>10分钟 | ∞倍 |
| **并发任务** | 1000+ | 1（阻塞） | 1000倍 |
| **任务超时** | 无限制 | 10分钟 | 移除 |
| **界面卡死** | 0% | 100%（长任务） | 彻底解决 |
| **Worker数量** | 2-20动态 | 0 | 新增 |
| **内存占用** | <500MB | 300MB | +67% |

---

## 🛡️ 安全与可靠性

### 1. 任务隔离
- 长任务：独立进程（sessions_spawn）
- 短任务：协程池隔离
- 失败不影响主进程

### 2. 超时保护
- 短任务：5分钟超时
- 长任务：24小时超时
- 绝对超时：7天

### 3. 崩溃恢复
- Worker崩溃自动重启
- 任务自动重试
- 状态持久化

### 4. 资源限制
- Worker内存上限：500MB
- 最大并发：50 per Worker
- 队列长度限制：10000

---

## 🚀 实施计划

### Week 1: 基础架构
- Day 1-2: Gateway + 任务队列
- Day 3-4: Worker池基础
- Day 5: WebSocket推送

### Week 2: 完善与优化
- Day 1-2: 任务管理API
- Day 3-4: 性能优化
- Day 5: 全面测试 + 部署

---

**技术方案完成时间：** 2026-02-15 21:45
**总耗时：** 9分钟
