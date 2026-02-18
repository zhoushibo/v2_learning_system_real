# V2 MVP 使用指南

---

## 🚀 **快速启动**

### 1. 启动服务

#### 启动Gateway
```bash
cd C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\mvp
python launcher.py gateway
```

**输出：**
```
🚀 启动 Gateway (http://127.0.0.1:8000)
Store] SQLite L3持久化层已初始化 ✅
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### 启动Worker（新窗口）
```bash
cd C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\mvp
python launcher.py worker
```

**输出：**
```
🔧 启动 Worker
增强型Worker启动 ✅
✅ LoadBalancer就绪
✅ 5模型智能路由就绪
✅ 并发+RPM双重限流就绪

✅ Redis队列连接成功
✅ 存储模式: hybrid

🔴 Worker开始监听Redis队列...
```

---

## 📊 **健康检查**

### 检查Gateway状态
```bash
python -c "import requests; print(requests.get('http://127.0.0.1:8000/health').json())"
```

**响应：**
```json
{
  "status": "ok",
  "gateway_running": true,
  "components": {
    "redis_queue": true,
    "redis_cache": true,
    "sqlite_persistence": true,
    "storage_mode": "hybrid"
  },
  "v1_compatible": true
}
```

---

## 🎯 **提交任务**

### 提交任务示例
```python
import requests

# 提交任务
response = requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": "介绍一下你自己"}
)

print(response.json())
```

**响应：**
```json
{
  "task_id": "dd817cdf-22a6-4b63-9505-29e738ef5b54",
  "status": "pending",
  "message": "任务已提交，正在处理..."
}
```

---

## 📝 **查询任务**

### 查询任务状态和结果
```python
import requests

# 查询任务
task_id = "dd817cdf-22a6-4b63-9505-29e738ef5b54"
response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")

result = response.json()
print(f"状态: {result['status']}")
print(f"结果: {result['result']}")
```

**响应：**
```json
{
  "task_id": "dd817cdf-22a6-4b63-9505-29e738ef5b54",
  "status": "completed",
  "result": "我是腾讯混元大模型...",
  "error": null,
  "metadata": {
    "model": "hunyuan-lite",
    "latency": 1.40,
    "usage": {
      "prompt_tokens": 6,
      "completion_tokens": 66,
      "total_tokens": 72
    }
  }
}
```

---

## 🧪 **完整测试流程**

### Python测试脚本
```python
import requests
import time
import json

# 1. 提交任务
print("1. 提交任务...")
task_content = "介绍一下你自己，用简短的话"
response = requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": task_content}
)

task_id = response.json()["task_id"]
print(f"   任务ID: {task_id}")

# 2. 等待任务完成
print("2. 等待任务处理...")
for i in range(10):
    response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
    task = response.json()

    if task["status"] == "completed":
        print(f"   ✅ 任务完成！")
        break
    elif task["status"] == "failed":
        print(f"   ❌ 任务失败: {task['error']}")
        break
    else:
        print(f"   ⏳ 处理中... ({i+1}/10)")
        time.sleep(1)

# 3. 显示结果
print("3. 任务结果:")
print(f"   状态: {task['status']}")
print(f"   模型: {task['metadata']['model']}")
print(f"   耗时: {task['metadata']['latency']:.2f}秒")
print(f"   Token: {task['metadata']['usage']['total_tokens']}")
print(f"   结果: {task['result']}")
```

---

## 🤖 **多模型智能路由**

### 自动模型选择
```
简单任务 → hunyuan（无RPM限制，速度快）
实时任务 → zhipu（1.03秒，最快）
复杂推理 → nvidia1（思考模式）
大批量 → hunyuan（并发5）
```

### 5模型支持
| 模型 | 速度 | 并发 | RPM | 上下文 | 最适合 |
|------|------|------|-----|--------|--------|
| **zhipu** | 1.03秒 🥇 | 1 | ? | 200K | 实时交互 |
| **hunyuan** | 1.20秒 🥈 | 5 | 无 ⚡ | 256K | 大批量 |
| **nvidia1** | 7.17秒 | 5 | 40 | 128K | 复杂推理 |
| **nvidia2** | 2.68秒 🥉 | 5 | 40 | 128K | 通用任务 |
| **siliconflow** | 0.10秒 | - | 5 | - | Embeddings |

---

## 📋 **任务类型示例**

### 1. 简单问答
```python
requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": "什么是AI？"}
)
```
**路由到：** hunyuan 或 nvidia2

### 2. 复杂推理
```python
requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": "深入分析人工智能对社会的影响"}
)
```
**路由到：** nvidia1（思考模式）

### 3. 快速响应
```python
requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": "现在马上回答：你好"}
)
```
**路由到：** zhipu（最快）

### 4. 批量任务
```python
for i in range(10):
    requests.post(
        "http://127.0.0.1:8000/tasks",
        json={"content": f"翻译第{i+1}句"}
    )
```
**路由到：** hunyuan（无RPM限制）

---

## 🔧 **高级功能**

### 查询所有任务
```python
response = requests.get("http://127.0.0.1:8000/tasks")
tasks = response.json()["tasks"]
for task in tasks:
    print(f"{task['task_id']}: {task['status']}")
```

### 查看任务统计
```python
response = requests.get("http://127.0.0.1:8000/tasks/stats")
stats = response.json()
print(f"总任务数: {stats['total']}")
print(f"完成: {stats['completed']}")
print(f"失败: {stats['failed']}")
```

---

## 🚨 **常见问题**

### Q1: Worker没有处理任务？
**A:** 检查Worker是否启动
```bash
# 查看Worker日志
# 应该看到 "🔴 Worker开始监听Redis队列..."
```

### Q2: 任务状态一直是pending？
**A:** 检查Redis连接
```bash
# 在Worker启动日志中应该看到：
# ✅ Redis队列连接成功
```

### Q3: 任务失败？
**A:** 查看错误信息
```python
response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
task = response.json()
print(f"错误: {task['error']}")
```

### Q4: 如何使用特定模型？
**A:** 当前版本自动选择最优模型，未来可支持手动指定

---

## 📊 **性能指标**

### 实测性能
| 指标 | 数值 | 说明 |
|------|------|------|
| **Gateway响应** | <5ms | 极快 |
| **任务提交** | <10ms | 即时 |
| **任务执行** | 1-7秒 | 取决于模型 |
| **并发能力** | 16 | 5混元+10NVIDIA+1智谱 |

### 优化建议
1. 使用批量任务时选择hunyuan（无RPM限制）
2. 需要快速响应使用zhipu
3. 复杂推理使用nvidia1（思考模式）

---

## 🎯 **下一步工作**

### 短期（1-2天）
- [ ] 在新会话中使用V2 MVP处理实际任务
- [ ] 测试不同任务类型的路由
- [ ] 监控系统性能

### 中期（1周）
- [ ] 集成到ARES系统
- [ ] 添加更多任务类型
- [ ] 优化负载均衡策略

### 长期（1个月）
- [ ] 开发Web UI
- [ ] 添加任务优先级
- [ ] 实现任务调度器

---

## 📝 **启动检查清单**

启动前检查：
- [ ] Python 3.11已安装
- [ ] 依赖已安装（`pip install -r requirements.txt`）
- [ ] Redis服务器运行（可选，系统会自动检查）
- [ ] V1 Gateway运行在`http://127.0.0.1:18790`
- [ ] API密钥配置正确（`API_CONFIG_FINAL.json`）

启动后验证：
- [ ] Gateway成功启动（访问 http://127.0.0.1:8000/health）
- [ ] Worker成功启动（看到"Worker开始监听Redis队列"）
- [ ] 测试任务提交成功
- [ ] 测试任务执行成功

---

**文档版本：** v1.0
**最后更新：** 2026-02-16 03:35
**维护者：** Claw + 博
**状态：** 🟢 **可用** - V2 MVP已测试通过
