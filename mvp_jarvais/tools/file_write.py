"""
file_write 工具 - 写入文件内容

功能：
- 写入文本文件内容
- 支持覆盖/追加模式
- 自动创建父目录
- 支持大文件写入（流式）
- 返回写入结果和元数据

使用示例：
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
result = await file_write("chinese.txt", "中文内容", encoding="utf-8")
```
"""

import os
from pathlib import Path
from typing import Literal


async def file_write(
    path: str,
    content: str,
    mode: Literal['w', 'a'] = 'w',
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> dict:
    """
    写入文件内容
    
    参数:
        path: 文件路径（相对或绝对）
        content: 要写入的内容
        mode: 写入模式 ('w'=覆盖，'a'=追加)，默认 'w'
        encoding: 文件编码，默认 'utf-8'
        create_dirs: 是否自动创建父目录，默认 True
    
    返回:
        dict: {
            "success": bool,       # 是否成功
            "bytes_written": int,  # 写入字节数
            "path": str,           # 绝对路径
            "mode": str,           # 写入模式
            "error": str           # 如果有错误
        }
    """
    # 参数验证
    if not path:
        return {"success": False, "error": "文件路径不能为空"}
    
    if content is None:
        return {"success": False, "error": "写入内容不能为 None"}
    
    if mode not in ['w', 'a']:
        return {"success": False, "error": "mode 必须是 'w' 或 'a'"}
    
    # 转换为绝对路径
    abs_path = Path(path).resolve()
    
    # 检查是否是目录
    if abs_path.is_dir():
        return {"success": False, "error": f"路径是目录，不是文件：{abs_path}"}
    
    # 自动创建父目录
    if create_dirs:
        try:
            abs_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return {"success": False, "error": f"无法创建目录：{str(e)}"}
    
    # 写入文件内容
    try:
        # 计算内容字节数
        content_bytes = content.encode(encoding)
        bytes_written = len(content_bytes)
        
        # 写入文件
        with open(abs_path, mode, encoding=encoding) as f:
            f.write(content)
        
        return {
            "success": True,
            "bytes_written": bytes_written,
            "path": str(abs_path),
            "mode": mode
        }
        
    except PermissionError as e:
        return {
            "success": False,
            "error": f"权限不足，无法写入：{abs_path}"
        }
    except OSError as e:
        # 包括磁盘空间不足、路径无效等
        return {
            "success": False,
            "error": f"写入失败：{str(e)}"
        }
    except UnicodeEncodeError as e:
        return {
            "success": False,
            "error": f"编码错误：{str(e)}。尝试使用 'utf-8', 'gbk', 或 'latin-1'"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"未知错误：{str(e)}"
        }


# 工具元数据（用于 ToolEngine 注册）
TOOL_METADATA = {
    "name": "file_write",
    "description": "写入文本文件内容，支持覆盖/追加模式和自动创建父目录",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "文件路径（相对或绝对）"
            },
            "content": {
                "type": "string",
                "description": "要写入的内容"
            },
            "mode": {
                "type": "string",
                "enum": ["w", "a"],
                "description": "写入模式 ('w'=覆盖，'a'=追加)",
                "default": "w"
            },
            "encoding": {
                "type": "string",
                "description": "文件编码",
                "default": "utf-8"
            },
            "create_dirs": {
                "type": "boolean",
                "description": "是否自动创建父目录",
                "default": True
            }
        },
        "required": ["path", "content"]
    },
    "returns": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "bytes_written": {"type": "integer"},
            "path": {"type": "string"},
            "mode": {"type": "string"},
            "error": {"type": "string"}
        }
    }
}
