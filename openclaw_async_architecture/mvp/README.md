# OpenClaw V2 MVP

最小可行性产品 - 验证异步任务处理架构

## 🎯 MVP目标

验证核心假设：
- ✅ Worker能否通过HTTP API调用V1？（已验证）
- [ ] 长任务是否阻塞Gateway界面？
- [ ] 是否支持取消/重试任务？
- [ ] 性能是否符合预期（<50ms响应）？

## 🏗️ 架构

```
用户 → Gateway (FastAPI) → Redis Queue → Worker → V1 Gateway
                                ↓
                             Redis Store
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd mvp
pip install -r requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件（使用默认配置即可）
```

### 3. 启动Redis

确保Redis已启动（默认127.0.0.1:6379）

```bash
redis-cli ping  # 应该返回 PONG
```

### 4. 启动Gateway（终端1）

```bash
python launcher.py gateway
```

访问：http://127.0.0.1:8000

### 5. 启动Worker（终端2）

```bash
python launcher.py worker
```

## 📡 API使用

### 提交任务

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"content": "帮我分析一下什么是人工智能"}'
```

**响应（立即返回，<50ms）：**
```json
{
  "task_id": "abc-123",
  "status": "pending",
  "message": "任务已提交，正在处理中"
}
```

### 查询任务状态

```bash
curl http://127.0.0.1:8000/tasks/{task_id}
```

**响应：**
```json
{
  "task_id": "abc-123",
  "status": "completed",
  "content": "帮我分析一下什么是人工智能",
  "result": "人工智能（AI）是...",
  "created_at": "2026-02-15T23:00:00",
  "updated_at": "2026-02-15T23:00:05"
}
```

## 🧪 测试

### 测试脚本

```bash
cd mvp
python tests/test_mvp.py
```

### 预期结果

1. **提交任务** - 立即返回task_id（<50ms）
2. **Worker处理** - 后台执行，不阻塞界面
3. **获取结果** - 等待完成后返回

## 📊 验证目标

| 目标 | 验证方法 | 预期结果 |
|------|----------|----------|
| **不阻塞界面** | 提交长任务，立即提交新任务 | Gateway始终响应（<50ms） |
| **Worker正常执行** | 查看Worker日志 | 任务成功执行 |
| **Worker调用V1** | 查看Worker响应内容 | V1成功响应 |

## 📁 项目结构

```
mvp/
├── src/
│   ├── gateway/      # Gateway (FastAPI)
│   ├── queue/        # Redis任务队列
│   ├── worker/       # Worker执行器（HTTP调用V1）
│   ├── store/        # Redis结果存储
│   └── common/       # 公共模块（配置、模型）
├── tests/            # 测试脚本
├── launcher.py       # 启动脚本
├── requirements.txt  # 依赖
└── README.md
```

## 🔍 关键代码

### Worker执行任务

```python
async def execute_task(self, task: Task) -> Task:
    response = await self.client.post(
        f"{self.v1_url}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {self.v1_token}",
            "x-openclaw-agent-id": self.v1_agent_id
        },
        json={
            "model": "openclaw",
            "messages": [{"role": "user", "content": task.content}]
        }
    )
    # 处理响应...
```

## 📝 注意事项

1. **Redis必须先启动**，否则启动失败
2. **V1 Gateway (18790)** 必须运行，否则Worker无法执行任务
3. **长任务测试** - 可以用任务："帮我写一个完整的HTTP服务器实现"

## ✅ 成功标志

- [ ] Gateway启动成功（访问 http://127.0.0.1:8000 返回状态）
- [ ] Worker启动成功（日志显示"✅ Redis连接成功"）
- [ ] 提交任务立即返回（<50ms）
- [ ] Worker成功执行任务
- [ ] 长任务不阻塞Gateway界面

---

**下一步验证测试：** `python tests/test_mvp.py`
