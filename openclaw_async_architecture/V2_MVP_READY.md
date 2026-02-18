# V2 MVP 已就绪 - 快速启动指南

---

## 🚀 **当前状态（2026-02-16 03:38）**

### ✅ 服务运行中
```
Gateway: ✅ 运行在 http://127.0.0.1:8000
Worker:  ✅ 运行中，监听Redis队列
Redis:   ✅ 队列和缓存正常
SQLite:  ✅ 持久化存储正常
```

### ✅ 最新测试结果
```
任务: "简单说说V2 MVP的优点"
状态: completed ✅
模型: hunyuan-lite
耗时: 3.19秒
Token: 328个
结论: V2 MVP完全可用！
```

---

## 📋 **启动命令**

### 启动Gateway（窗口1）
```bash
cd C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\mvp
python launcher.py gateway
```

### 启动Worker（窗口2）
```bash
cd C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\mvp
python launcher.py worker
```

---

## 📝 **快速使用**

### Python脚本示例
```python
import requests
import time
import json

# 提交任务
print("提交任务...")
response = requests.post(
    "http://127.0.0.1:8000/tasks",
    json={"content": "介绍一下你自己"}
)
task_id = response.json()["task_id"]
print(f"任务ID: {task_id}")

# 等待完成
print("等待处理...")
for i in range(10):
    response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
    task = response.json()

    if task["status"] == "completed":
        print(f"完成！")
        print(f"模型: {task['metadata']['model']}")
        print(f"耗时: {task['metadata']['latency']:.2f}秒")
        print(f"结果: {task['result'][:200]}...")
        break
    elif task["status"] == "failed":
        print(f"失败: {task.get('error')}")
        break
    else:
        print(f"处理中... ({i+1}/10)")
        time.sleep(1)
```

---

## 🤖 **多模型智能路由**

```
简单任务    → hunyuan   (无RPM限制)
实时任务    → zhipu     (最快1.03秒)
复杂推理    → nvidia1   (思考模式)
大批量      → hunyuan   (并发5)
```

---

## 📊 **当前系统能力**

| 能力 | 数值 | 说明 |
|------|------|------|
| 并发 | 16 | 5混元+10NVIDIA+1智谱 |
| 响应时间 | 1-7秒 | 取决于任务类型 |
| 支持模型 | 5个 | 智谱、混元、NVIDIA×2、SiliconFlow |
| 存储 | 三层 | SQLite+Redis+ChromaDB |

---

## 🎯 **推荐使用场景**

### 1. 日常任务（新会话）
```python
# 简单问答、翻译、总结
requests.post("http://127.0.0.1:8000/tasks",
    json={"content": "简单任务"})
```

### 2. 复杂任务
```python
# 深度分析、创意写作、技术文档
requests.post("http://127.0.0.1:8000/tasks",
    json={"content": "深入分析..."})
```

### 3. 批量任务
```python
# 多个任务并发提交
for i in range(10):
    requests.post("http://127.0.0.1:8000/tasks",
        json={"content": f"任务{i}"})
```

---

## ⚠️ **注意事项**

1. **先启动Gateway，再启动Worker**
2. **两个窗口都要运行**
3. **Gateway端口：8000**
4. **V1需要运行在18790端口**

---

## 📁 **关键文件**

| 文件 | 用途 |
|------|------|
| `launcher.py` | 启动脚本 |
| `quick_test.py` | 快速测试脚本 |
| `V2_MVP_USAGE_GUIDE.md` | 完整使用指南 |
| `mvp/src/gateway/main.py` | Gateway代码 |
| `mvp/src/worker/main.py` | Worker代码 |

---

## 🎉 **测试成功！**

✅ Gateway运行正常
✅ Worker运行正常
✅ 任务提交成功
✅ 任务执行成功
✅ 多模型路由正常

**V2 MVP已就绪，可以在新会话中开始实际工作！**

---

**文档版本：** v1.0
**创建时间：** 2026-02-16 03:38
**维护者：** Claw + 博
**状态：** 🟢 **可用** - 系统已测试通过
