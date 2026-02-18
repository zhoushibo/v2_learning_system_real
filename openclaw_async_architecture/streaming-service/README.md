# OpenClaw流式响应Gateway

## 🎯 简介

实时流式LLM对话服务，解决"经常卡住了"的用户体验问题。

### 核心特性

- ⚡ **实时流式输出** - 边生边出，不用等待完整响应
- 🚀 **性能优化** - 首字输出2-3秒，完整响应3-5秒
- 🔄 **HTTP连接复用** - 避免重复TLS握手
- 📊 **性能监控** - 详细分段计时和性能目标检查
- 💬 **多API支持** - NVIDIA、智谱、混元

---

## 🏗️ 架构

```
用户 → WebSocket客户端
       ↓
   Gateway (FastAPI + WebSocket)
       ↓
   StreamServer
       ↓
   StreamChatService
       ↓
   LLM API (NVIDIA/智谱/混元)
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd streaming-service
pip install -r requirements.txt
```

### 2. 启动Gateway

```bash
python launcher.py
```

**输出示例：**
```
============================================================
OpenClaw流式响应Gateway
============================================================

配置:
  主机: 0.0.0.0
  端口: 8001
  WebSocket: ws://0.0.0.0:8001/ws/stream/{session_id}
  健康检查: http://0.0.0.0:8001/health

============================================================
```

### 3. 测试Gateway

```bash
# 新终端
cd streaming-service
python tests/test_websocket_client.py
```

---

## 📡 API使用

### WebSocket端点

**URL:** `ws://127.0.0.1:8001/ws/stream/{session_id}`

**参数：**
- `session_id` - 会话ID（可选，建议唯一标识）

### 消息格式（客户端→服务器）

```json
{
    "message": "用户消息内容",
    "provider": "nvidia2"
}
```

**字段说明：**
- `message` - 必需，用户消息
- `provider` - 可选，API提供商：
  - `nvidia1` - NVIDIA主账户（复杂推理）
  - `nvidia2` - NVIDIA备用（推荐，更快）
  - `zhipu` - 智谱（国内，最快但并发限制）
  - `hunyuan` - 混元（国内，推荐）

### 输出格式（服务器→客户端）

#### 文本块

直接发送文本字符串（流式输出）

#### 完成信号

```json
{
    "type": "done"
}
```

#### 错误消息

```json
{
    "type": "error",
    "message": "错误信息"
}
```

---

## 🧪 测试

### 自动化测试

```bash
python tests/test_websocket_client.py
```

**测试内容：**
1. ✅ 基础WebSocket连接
2. ✅ 混元API性能（国内）
3. ✅ 多次调用（热连接）
4. ✅ Gateway健康检查

### 预期结果

```
[PERF] 首字输出: 2000ms
人工智能是...

[OK] 测试完成！总字符数: 36
```

---

## 📊 性能指标

| API类型 | 首字输出 | 完整响应 | 备注 |
|---------|----------|----------|------|
| 国内API | <1秒 | <3秒 | 智谱/混元 |
| 国外API（热连接） | <3秒 | <5秒 | NVIDIA |
| 国外API（首次） | <8秒 | <10秒 | NVIDIA（冷启动） |

### 优化效果

| 场景 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 首字输出 | 13.3秒 | 2.0秒 | **6.5倍** ⚡ |
| 完整响应 | 14.2秒 | 2.4秒 | **5.9倍** ⚡ |

---

## 🔧 配置

### 端口配置

默认端口：`8001`

修改方式：编辑 `launcher.py` 或 `gateway.py`

### API配置

API配置位于：`openclaw_async_architecture/API_CONFIG_FINAL.json`

支持的API：
- NVIDIA×2（复杂推理）
- 智谱（速度最快）
- 混元（国内推荐）

---

## 📁 项目结构

```
streaming-service/
├── src/
│   └── gateway.py              # FastAPI Gateway（WebSocket端点）
├── tests/
│   └── test_websocket_client.py # WebSocket测试客户端
├── launcher.py                 # 启动脚本
├── requirements.txt            # Python依赖
└── README.md                   # 本文档

依赖（../../mvp/src）:
├── streaming/
│   ├── stream_server.py        # WebSocket服务器
│   ├── connection_manager.py   # 连接管理
│   ├── llm_stream.py           # LLM流式调用
│   ├── performance_monitor.py  # 性能监控
│   └── http_client.py          # HTTP客户端管理
```

---

## 📝 使用示例

### Python客户端（websockets）

```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://127.0.0.1:8001/ws/stream/my-session-001"

    async with websockets.connect(uri) as websocket:
        # 发送消息
        message = {
            "message": "用一句话介绍什么是人工智能",
            "provider": "nvidia2"
        }

        await websocket.send(json.dumps(message))

        # 接收流式响应
        response = ""
        while True:
            try:
                data = await websocket.recv()

                # 检查是否为JSON（完成/错误信号）
                try:
                    parsed = json.loads(data)
                    if parsed.get("type") == "done":
                        break
                except json.JSONDecodeError:
                    # 普通文本，直接输出
                    response += data
                    print(data, end="", flush=True)

            except Exception as e:
                print(f"Error: {e}")
                break

asyncio.run(chat())
```

---

## 🛠️ 进阶功能

### 监控端点

**健康检查：**
```bash
curl http://127.0.0.1:8001/health
```

**统计信息：**
```bash
curl http://127.0.0.1:8001/stats
```

### PM2部署

```bash
pm2 start launcher.py --name claw-streaming-gateway
pm2 logs claw-streaming-gateway
pm2 stop claw-streaming-gateway
```

---

## 🐛 故障排查

### Gateway启动失败

**错误：** `ModuleNotFoundError: No module named 'streaming'`

**解决：**
```bash
# 确保在正确的目录
cd C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\streaming-service

# 检查PYTHONPATH
echo %PYTHONPATH%
```

### WebSocket连接失败

**错误：** `Connection refused`

**解决：**
1. 确保Gateway已启动：`python launcher.py`
2. 检查端口是否被占用：`netstat -ano | findstr 8001`

### API调用失败

**错误：** `404 Not Found` 或 `401 Unauthorized`

**解决：**
1. 检查API配置：`API_CONFIG_FINAL.json`
2. 确认API Key有效
3. 查看Gateway日志

---

## 📚 相关文档

- **性能目标：** `memory/PROJECT_STREAMING_PERFORMANCE_TARGETS.md`
- **V2架构：** `openclaw_async_architecture/mvp/README.md`
- **API配置：** `openclaw_async_architecture/API_CONFIG_FINAL.json`

---

## 🎯 未来规划

- [ ] 集成到V2 Gateway（统一架构）
- [ ] 取消机制（用户主动中断）
- [ ] 心跳检测（假死连接检测）
- [ ] 对话上下文保持
- [ ] 多会话支持

---

**版本：** 1.0.0
**更新时间：** 2026-02-17
**维护者：** Claw
