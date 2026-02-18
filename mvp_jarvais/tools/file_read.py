"""
file_read 工具 - 读取文件内容

功能：
- 读取文本文件内容
- 支持指定行范围（offset/limit）
- 支持大文件分块读取（逐行，不一次性加载）
- 返回文件内容和元数据

使用示例：
```python
from mvp_jarvais.tools.file_read import file_read

# 读取完整文件
result = await file_read("README.md")
print(result["content"])

# 读取指定行范围（第 5-15 行）
result = await file_read("large_file.txt", offset=5, limit=10)
print(result["read_lines"])  # 10

# 指定编码
result = await file_read("chinese_file.txt", encoding="gbk")
```
"""

import os
from pathlib import Path
from typing import Optional


async def file_read(
    path: str,
    offset: int = 0,
    limit: Optional[int] = None,
    encoding: str = 'utf-8'
) -> dict:
    """
    读取文件内容
    
    参数:
        path: 文件路径（相对或绝对）
        offset: 从第几行开始读取（1-indexed，0=从第 1 行开始）
        limit: 读取多少行（None=读取全部）
        encoding: 文件编码（默认 utf-8）
    
    返回:
        dict: {
            "content": str,       # 文件内容
            "total_lines": int,   # 总行数（如果读取全部）
            "read_lines": int,    # 实际读取行数
            "size_bytes": int,    # 文件大小
            "path": str,          # 文件路径（绝对路径）
            "error": str          # 如果有错误
        }
    """
    # 参数验证
    if not path:
        return {"error": "文件路径不能为空"}
    
    if offset < 0:
        return {"error": "offset 必须 >= 0"}
    
    if limit is not None and limit <= 0:
        return {"error": "limit 必须 > 0 或 None"}
    
    # 转换为绝对路径
    abs_path = Path(path).resolve()
    
    # 检查文件是否存在
    if not abs_path.exists():
        return {"error": f"文件不存在：{abs_path}"}
    
    # 检查是否是文件（不是目录）
    if not abs_path.is_file():
        return {"error": f"不是文件：{abs_path}"}
    
    # 检查文件大小
    try:
        size_bytes = abs_path.stat().st_size
    except Exception as e:
        return {"error": f"无法获取文件大小：{str(e)}"}
    
    # 读取文件内容（逐行读取，支持大文件）
    try:
        lines = []
        total_lines = 0
        read_lines = 0
        reached_limit = False
        
        with open(abs_path, 'r', encoding=encoding, errors='replace') as f:
            for i, line in enumerate(f, 1):
                total_lines = i
                
                # 跳过 offset 之前的行
                if offset > 0 and i < offset:
                    continue
                
                # 检查是否达到 limit
                if limit is not None and read_lines >= limit:
                    reached_limit = True
                    continue  # 继续读取以统计 total_lines，但不再添加内容
                
                lines.append(line)
                read_lines += 1
        
        # 合并内容
        content = ''.join(lines)
        
        return {
            "content": content,
            "total_lines": total_lines,
            "read_lines": read_lines,
            "size_bytes": size_bytes,
            "path": str(abs_path)
        }
        
    except UnicodeDecodeError as e:
        return {
            "error": f"编码错误：{str(e)}。尝试使用 'gbk', 'latin-1', 或 'utf-8-sig'"
        }
    except PermissionError as e:
        return {
            "error": f"权限不足，无法读取：{abs_path}"
        }
    except Exception as e:
        return {
            "error": f"读取失败：{str(e)}"
        }


# 工具元数据（用于 ToolEngine 注册）
TOOL_METADATA = {
    "name": "file_read",
    "description": "读取文本文件内容，支持指定行范围和大文件分块读取",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "文件路径（相对或绝对）"
            },
            "offset": {
                "type": "integer",
                "description": "从第几行开始读取（1-indexed，0=从第 1 行开始）",
                "default": 0
            },
            "limit": {
                "type": "integer",
                "description": "读取多少行（None=读取全部）",
                "default": None
            },
            "encoding": {
                "type": "string",
                "description": "文件编码",
                "default": "utf-8"
            }
        },
        "required": ["path"]
    },
    "returns": {
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "total_lines": {"type": "integer"},
            "read_lines": {"type": "integer"},
            "size_bytes": {"type": "integer"},
            "path": {"type": "string"},
            "error": {"type": "string"}
        }
    }
}
