# P3：V2 CLI 整合 V2 学习系统 - 设计方案

## 🎯 目标
在 V2 CLI 中添加 `learn` 命令，让用户可以直接通过 CLI 使用 V2 学习系统

## 📋 功能需求

### 命令格式
```bash
v2 learn "主题" [选项]
```

### 选项
- `--workers, -w <num>`: Worker 数量（默认：3）
- `--perspectives, -p <num>`: 学习视角数量（默认：3）
- `--output, -o <file>`: 输出文件路径（可选）
- `--format, -f <format>`: 输出格式（text/json/markdown，默认：text）
- `--model <model>`: 指定模型（默认：使用配置的主模型）

### 示例
```bash
# 基础用法
v2 learn "Python 异步编程"

# 指定 Worker 数量
v2 learn "React Hooks" -w 5

# 指定视角数量
v2 learn "机器学习" -p 5

# 输出到文件
v2 learn "Docker 容器化" -o docker_notes.md -f markdown

# 使用特定模型
v2 learn "量子计算" --model "z-ai/glm4.7"
```

## 🏗️ 技术实现

### 1. 导入 V2 学习系统
```python
from v2_learning_system_real import LearningEngine
from v2_learning_system_real.llm.openai import OpenAIProvider
```

### 2. 创建 learn 命令
```python
@app.command()
async def learn(
    topic: str,
    workers: int = typer.Option(3, "--workers", "-w"),
    perspectives: int = typer.Option(3, "--perspectives", "-p"),
    output: Optional[str] = typer.Option(None, "--output", "-o"),
    format: str = typer.Option("text", "--format", "-f"),
    model: Optional[str] = typer.Option(None, "--model")
):
    """
    使用 V2 学习系统学习新主题
    
    TOPIC: 要学习的主题
    
    示例:
        v2 learn "Python 异步编程"
        v2 learn "React Hooks" -w 5
        v2 learn "Docker" -o docker.md -f markdown
    """
    # 实现逻辑
```

### 3. 执行学习
```python
# 初始化学习引擎
engine = LearningEngine(num_workers=workers, model=model)

# 执行并行学习
results = await engine.parallel_learning(topic, num_perspectives=perspectives)

# 输出结果
if output:
    save_to_file(results, output, format)
else:
    display_results(results, format)
```

## 📊 输出格式

### Text 格式（默认）
```
📚 学习主题：Python 异步编程
================================================================================

视角 1: technical
--------------------------------------------------------------------------------
• Python 异步编程基于 asyncio 库
• 使用 async/await 语法
• 核心概念：Event Loop、Task、Future

视角 2: practical
--------------------------------------------------------------------------------
• 适用于 I/O 密集型任务
• 常见场景：网络请求、文件操作、数据库查询
• 性能提升：10-100 倍（取决于场景）

视角 3: theoretical
--------------------------------------------------------------------------------
• 异步 vs 同步 vs 并行
• 协程与线程的区别
• Python GIL 对异步的影响

================================================================================
✅ 学习完成！耗时：12.5 秒
```

### Markdown 格式
```markdown
# Python 异步编程

## 视角 1: technical
- Python 异步编程基于 asyncio 库
- 使用 async/await 语法
- 核心概念：Event Loop、Task、Future

## 视角 2: practical
...
```

### JSON 格式
```json
{
  "topic": "Python 异步编程",
  "duration_seconds": 12.5,
  "perspectives": [
    {
      "name": "technical",
      "result": "..."
    },
    ...
  ]
}
```

## ✅ 验收标准
- [ ] 基础命令可用
- [ ] 所有选项正常工作
- [ ] 输出格式正确
- [ ] 错误处理完善（API 失败、网络错误等）
- [ ] 性能良好（<15 秒完成 3 视角学习）
- [ ] 文档完整

## 📝 实施步骤
1. 在 V2 CLI 中添加 learn 命令（30 分钟）
2. 实现学习逻辑（30 分钟）
3. 实现输出格式化（30 分钟）
4. 测试所有场景（30 分钟）
5. 更新文档（15 分钟）

**总时间：** 约 2 小时
