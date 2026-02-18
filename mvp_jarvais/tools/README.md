# MVP JARVIS 工具集

## 🛠️ 可用工具

### 1. file_read ⭐
**状态：** ✅ 已完成（2026-02-17 21:57）

**功能：** 读取文本文件内容，支持指定行范围和大文件分块读取

**使用示例：**
```python
from mvp_jarvais.tools.file_read import file_read

# 读取完整文件
result = await file_read("README.md")
print(result["content"])

# 读取指定行范围（第 5-15 行）
result = await file_read("large_file.txt", offset=5, limit=10)
print(f"读取了 {result['read_lines']} 行")

# 指定编码
result = await file_read("chinese_file.txt", encoding="gbk")
```

**参数：**
- `path`（必需）：文件路径（相对或绝对）
- `offset`（可选）：从第几行开始读取（1-indexed，0=从第 1 行开始），默认 0
- `limit`（可选）：读取多少行（None=读取全部），默认 None
- `encoding`（可选）：文件编码，默认 'utf-8'

**返回：**
```json
{
  "content": "文件内容",
  "total_lines": 1000,
  "read_lines": 10,
  "size_bytes": 51200,
  "path": "C:\\absolute\\path\\to\\file.txt"
}
```

**错误处理：**
- 文件不存在 → `{"error": "文件不存在：..."}`
- 编码错误 → `{"error": "编码错误：...。尝试使用 'gbk', 'latin-1'..."}`
- 权限不足 → `{"error": "权限不足，无法读取：..."}`

**测试覆盖：** ✅ 14/14 测试通过（100% 覆盖率）

---

### 2. file_write ⭐ **NEW!**
**状态：** ✅ 已完成（2026-02-17 22:03）

**功能：** 写入文本文件内容，支持覆盖/追加模式和自动创建父目录

**使用示例：**
```python
from mvp_jarvais.tools.file_write import file_write

# 覆盖写入
result = await file_write("output.txt", "Hello World!")
print(result["bytes_written"])  # 12

# 追加写入
result = await file_write("log.txt", "New line\n", mode="a")

# 自动创建父目录
result = await file_write("new_dir/sub_dir/file.txt", "Content")

# 指定编码
result = await file_write("chinese.txt", "中文内容", encoding="gbk")
```

**参数：**
- `path`（必需）：文件路径
- `content`（必需）：要写入的内容
- `mode`（可选）：'w'=覆盖，'a'=追加，默认 'w'
- `encoding`（可选）：文件编码，默认 'utf-8'
- `create_dirs`（可选）：自动创建父目录，默认 True

**返回：**
```json
{
  "success": true,
  "bytes_written": 12,
  "path": "C:\\absolute\\path\\to\\file.txt",
  "mode": "w"
}
```

**测试覆盖：** ✅ 13/13 测试通过（100% 覆盖率）

---

### 3. web_search
**状态：** ✅ 已集成（OpenClaw 工具）

**功能：** 网络搜索（Brave Search API）

---

### 3. web_fetch
**状态：** ✅ 已集成（OpenClaw 工具）

**功能：** 抓取网页内容

---

### 4. exec
**状态：** ✅ 已集成（OpenClaw 工具）

**功能：** 执行 Shell 命令

---

### 5. memory_search
**状态：** ✅ 已集成（OpenClaw 工具）

**功能：** 搜索记忆

---

### 6. tts
**状态：** ✅ 已集成（OpenClaw 工具）

**功能：** 文本转语音

---

## 📊 工具统计

| 工具 | 状态 | 来源 | 测试覆盖 |
|------|------|------|---------|
| file_read | ✅ 自研 | MVP JARVIS | 100% (14/14) |
| file_write | ✅ 自研 | MVP JARVIS | 100% (13/13) |
| web_search | ✅ 集成 | OpenClaw | - |
| web_fetch | ✅ 集成 | OpenClaw | - |
| exec | ✅ 集成 | OpenClaw | - |
| memory_search | ✅ 集成 | OpenClaw | - |
| tts | ✅ 集成 | OpenClaw | - |

**总计：** 7 个工具（**2 个自研** + 5 个集成） ⭐

---

## 🚀 开发新工具

参考 `file_read` 工具的实现模板：

1. 创建 `mvp_jarvais/tools/your_tool.py`
2. 实现 `async def your_tool(...)` 函数
3. 定义 `TOOL_METADATA`
4. 编写测试 `mvp_jarvais/tools/tests/test_your_tool.py`
5. 更新本文档

---

**更新时间：** 2026-02-17 21:57
