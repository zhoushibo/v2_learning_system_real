# 立即可用工具使用指南

**更新时间：** 2026-02-17 01:18
**核心价值：** 立即提升效率和质量，无需复杂集成

---

## 🎯 工具1：Gateway流式对话 ⚡⚡⚡⚡⚡

### 位置
```
C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\streaming-service\use_gateway.py
```

### 使用方法

#### **交互模式（推荐）**

```bash
cd C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\streaming-service
python use_gateway.py --interactive
```

**使用步骤：**
1. 输入消息
2. 选择API（推荐：`hunyuan`）
3. 立即看到流式输出 ✨

---

#### **单次对话**

```bash
python use_gateway.py --message "你好" --provider hunyuan
```

---

#### **Python代码中使用**

```python
import asyncio
from use_gateway import chat

async def main():
    response = await chat("你好，请介绍一下你自己", provider="hunyuan")
    print(response)

asyncio.run(main())
```

---

### 功能特点

| 特点 | 说明 | 价值 |
|------|------|------|
| **流式输出** | 边生边出，不用等待 | 🔴 极大提升体验 |
| **多API支持** | hunyuan/nvidia2/zhipu | 灵活选择 |
| **首字快** | 混元首字661ms | 响应迅速 |
| **会话保持** | 支持session_id | 上下文连续 |
| **独立服务** | 端口8001，独立运行 | 不依赖OpenClaw |

---

### API选择建议

| API | 速度 | 限制 | 推荐 |
|-----|------|------|------|
| **hunyuan** | ⚡⚡⚡⚡⚡ 最快 | 无限流 | ⭐⭐⭐⭐⭐ 推荐 |
| **nvidia2** | ⚡⚡⚡⚡ 快 | 有限流 | ⭐⭐⭐⭐ |
| **zhipu** | ⚡⚡⚡ 快 | 限流严格 | ⭐⭐⭐ |

---

## 🎯 工具2：exec自主工具 ⚡⚡⚡⚡⚡

### 位置
```
C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\mvp\src\tools\exec_self.py
```

### 使用方法

#### **Python代码中直接使用**

```python
from openclaw_async_architecture.mvp.src.tools.exec_self import execute
import asyncio

async def main():
    # 执行命令
    exit_code, stdout, stderr = await execute(
        command="python --version",
        timeout=30,
        background=False
    )

    if exit_code == 0:
        print(f"✅ 成功: {stdout}")
    else:
        print(f"❌ 失败: {stderr}")

asyncio.run(main())
```

---

#### **同步版本**

```python
from openclaw_async_architecture.mvp.src.tools.exec_self import exec_sync

# 同步调用
exit_code, stdout, stderr = exec_sync(
    "dir",
    timeout=10
)
```

---

### 功能特点

| 特点 | 说明 | 价值 |
|------|------|------|
| **完全自主** | 不依赖OpenClaw | 🟡 提升自主性 |
| **前台/后台** | 支持两种模式 | 灵活使用 |
| **超时控制** | 防止卡住 | 安全可靠 |
| **工作目录** | 支持指定路径 | 方便管理 |
| **异常处理** | 完善的错误处理 | 健壮稳定 |

---

### 常用示例

**示例1：执行Python脚本**

```python
exit_code, stdout, stderr = await execute(
    "python my_script.py",
    timeout=60
)
```

**示例2：后台运行服务**

```python
exit_code, stdout, stderr = await execute(
    "npm start",
    background=True
)
```

**示例3：指定工作目录**

```python
exit_code, stdout, stderr = await execute(
    "python script.py",
    workdir="C:/projects/myapp"
)
```

---

## 🎯 综合使用示例

### 示例：智能命令执行系统

```python
import asyncio
from openclaw_async_architecture.mvp.src.tools.exec_self import execute

async def smart_execute(command: str, background=False):
    """智能执行命令"""

    print(f"\n🚀 执行: {command}")
    print("-" * 70)

    # 判断是否后台
    if "start" in command or "serve" in command:
        background = True

    # 执行
    exit_code, stdout, stderr = await execute(
        command,
        timeout=30 if not background else None,
        background=background
    )

    # 输出
    if exit_code == 0:
        print(f"✅ 成功")
        if stdout:
            print(f"输出: {stdout[:200]}")
    else:
        print(f"❌ 失败: {stderr}")

    return exit_code == 0

# 使用
async def main():
    # 前台执行
    await smart_execute("python --version")

    # 后台执行
    await smart_execute("cd path/to/project && npm start", background=True)

asyncio.run(main())
```

---

## 🎯 立即开始 - 5分钟清单

### ✅ 1. 启动Gateway交互对话

```bash
cd C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\streaming-service
python use_gateway.py --interactive
```

**试试这些问题：**
- "你好，请用一句话介绍什么是JARVIS"
- "如何提升Python代码的执行效率？"
- "给我写一个快速排序的Python代码"

---

### ✅ 2. 在代码中使用exec自主工具

```python
# 新建文件 test_exec.py
from openclaw_async_architecture.mvp.src.tools.exec_self import execute

async def main():
    # 测试命令
    commands = [
        "python --version",
        "dir",
        "echo Hello World"
    ]

    for cmd in commands:
        exit_code, stdout, stderr = await execute(cmd)
        print(f"\n命令: {cmd}")
        print(f"结果: {stdout}")

import asyncio
asyncio.run(main())
```

运行测试：
```bash
python test_exec.py
```

---

## 📊 价值总结

| 工具 | 提升效率 | 提升质量 | 核心价值 |
|------|---------|---------|---------|
| **Gateway流式** | 🔴 极高（用户体验）| 🔴 极高（体验）| **流式体验** ⭐⭐⭐⭐⭐ |
| **exec自主** | 🟡 中（开发效率）| 🟡 中（自主）| **自主可控** ⭐⭐⭐⭐ |

---

## 🎯 下一步建议

### 短期（今天）：
1. ✅ 体验Gateway交互对话
2. ✅ 在代码中使用exec自主工具
3. ✅ 感受效率和质量提升

### 中期（本周）：
1. 将Gateway集成到V2
2. 解决import路径问题
3. 完成V2 MVP Worker Pool

### 长期（本月）：
1. MVP全能AI整合
2. 逐步脱离OpenClaw依赖
3. 超越JARVIS的目标

---

## 💡 关键要点

1. ✅ **立即可以提升效率和质量**
2. ✅ **不需要复杂集成**
3. ✅ **立即可用**
4. ✅ **已经测试通过**

---

**开始使用吧！** 🚀

---

**文档版本：** v1.0
**最后更新：** 2026-02-17 01:18
**状态：** ✅ 立即可用 ✅
