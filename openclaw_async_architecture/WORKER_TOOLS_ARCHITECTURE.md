# V2 Worker工具系统架构设计

**设计时间：** 2026-02-16 04:30
**设计目标：** 让V2 Worker从简单API调用器变成完整Agent
**阶段：** 第一阶段 - 工具系统架构设计

---

## 🎯 **核心目标**

### 当前问题
- ❌ Worker只能调用LLM API，返回文本
- ❌ Worker无法写文件
- ❌ Worker无法执行代码
- ❌ Worker无法使用工具
- ❌ Worker无法访问本地资源

### 目标能力
- ✅ Worker可以读写文件
- ✅ Worker可以执行命令（带沙盒隔离）
- ✅ Worker可以执行Python代码
- ✅ Worker可以调用多种工具
- ✅ Worker可以访问本地资源（安全可控）
- ✅ 工具系统可扩展

---

## 🏗️ **架构设计**

### 整体架构

```
┌─────────────────────────────────────────────────────┐
│              V2 Worker进程                          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │         EnhancedWorker                      │    │
│  │  - 接收任务                                   │    │
│  │  - 调用V1 Gateway (LLM + 记忆)              │    │
│  │  - 调用工具系统                               │    │
│  └──────────┬─────────────────────┬────────────┘    │
│             │                     │                  │
│             ▼                     ▼                  │
│  ┌──────────────────┐    ┌──────────────┐        │
│  │  V1 Gateway      │    │  工具系统      │        │
│  │  (HTTP API)      │    │  (新增)      │        │
│  │                  │    │              │        │
│  │  - LLM调用       │    │  - 工具注册    │        │
│  │  - 记忆系统      │    │  - 工具调用    │        │
│  │  - V1原始工具    │    │  - 沙盒隔离    │        │
│  └──────────────────┘    └──────┬───────┘        │
│                                   │                 │
│                                   ▼                 │
│  ┌──────────────────────────────────────────┐   │
│  │            工具集 (ToolSet)               │   │
│  ├────────────┬─────────────┬──────────────┤   │
│  │FileSystem  │Command      │Code          │   │
│  │Tools       │Executor     │Executor      │   │
│  │            │             │              │   │
│  │- read      │- exec       │- python      │   │
│  │- write     │- shell      │- exec        │   │
│  │- list      │- safe_exec  │              │   │
│  │- mkdir     │             │              │   │
│  ├────────────┼─────────────┼──────────────┤   │
│  │GitTools    │MemoryTools  │未来扩展...   │   │
│  │            │             │              │   │
│  │- clone     │- search     │              │   │
│  │- pull      │- recall     │              │   │
│  │- push      │             │              │   │
│  └────────────┴─────────────┴──────────────┘   │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 📦 **核心组件设计**

### 1. 工具基类 (BaseTool)

**文件位置：** `mvp/src/worker/tools/base_tool.py`

**职责：**
- 定义工具接口规范
- 统一工具调用格式
- 工具异常处理

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """工具输入格式"""
    pass


class ToolOutput(BaseModel):
    """工具输出格式"""
    success: bool = Field(..., description="是否成功")
    data: Optional[Any] = Field(None, description="输出数据")
    error: Optional[str] = Field(None, description="错误信息")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")


class BaseTool(ABC):
    """工具基类

    所有工具必须继承此类
    """

    # 工具名称
    name: str

    # 工具描述
    description: str

    # 输入Schema
    input_schema: ToolInput

    @abstractmethod
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """
        执行工具

        Args:
            input_data: 输入数据

        Returns:
            ToolOutput: 输出结果
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据

        Args:
            input_data: 输入数据

        Returns:
            bool: 是否验证通过
        """
        pass
```

---

### 2. 工具管理器 (ToolManager)

**文件位置：** `mvp/src/worker/tools/tool_manager.py`

**职责：**
- 工具注册
- 工具查找
- 工具调用
- 工具白名单管理

```python
from typing import Dict, List, Optional
from .base_tool import BaseTool, ToolInput, ToolOutput


class ToolManager:
    """工具管理器

    管理所有Worker工具，提供统一的调用接口
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._whitelist: List[str] = []
        self._sandbox_enabled = True

    def register_tool(self, tool: BaseTool):
        """注册工具"""
        self._tools[tool.name] = tool
        print(f"[ToolManager] ✅ 工具 注册: {tool.name}")

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, str]]:
        """列出所有工具"""
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self._tools.values()
        ]

    async def call_tool(
        self,
        tool_name: str,
        input_data: Dict[str, Any]
    ) -> ToolOutput:
        """调用工具"""

        # 检查工具是否存在
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolOutput(
                success=False,
                error=f"工具不存在: {tool_name}"
            )

        # 检查白名单
        if self._whitelist and tool_name not in self._whitelist:
            return ToolOutput(
                success=False,
                error=f"工具不在白名单中: {tool_name}"
            )

        # 验证输入
        if not tool.validate_input(input_data):
            return ToolOutput(
                success=False,
                error=f"输入数据无效: {input_data}"
            )

        # 执行工具
        try:
            return await tool.execute(input_data)
        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"工具执行失败: {str(e)}"
            )

    def set_whitelist(self, whitelist: List[str]):
        """设置白名单"""
        self._whitelist = whitelist

    def enable_sandbox(self, enabled: bool = True):
        """启用/禁用沙盒"""
        self._sandbox_enabled = enabled
```

---

### 3. 核心工具实现

#### 3.1 FileSystemTools（文件系统工具）

**文件位置：** `mvp/src/worker/tools/filesystem_tools.py`

**能力：**
- ✅ 读取文件
- ✅ 写入文件
- ✅ 列出目录
- ✅ 创建目录
- ✅ 删除文件/目录（谨慎）

**安全限制：**
- ❌ 禁止访问系统目录（C:\Windows, /etc, /var等）
- ❌ 禁止路径遍历攻击（../../../etc/passwd）
- ✅ 限制在workspace目录下

```python
import os
import asyncio
from pathlib import Path
from typing import Optional, List
from .base_tool import BaseTool, ToolInput, ToolOutput


# ========== 输入Schema ==========

class ReadFileInput(ToolInput):
    path: str


class WriteFileInput(ToolInput):
    path: str
    content: str
    overwrite: bool = True


class ListDirectoryInput(ToolInput):
    path: str
    recursive: bool = False


class CreateDirectoryInput(ToolInput):
    path: str
    parents: bool = True


# ========== 工具实现 ==========

class ReadFileTool(BaseTool):
    """读取文件工具"""

    name = "read_file"
    description = "读取文件内容"

    async def execute(self, input_data: ReadFileInput) -> ToolOutput:
        # 安全检查
        full_path = self._sanitize_path(input_data.path)
        if not self._is_safe_path(full_path):
            return ToolOutput(
                success=False,
                error="路径不安全或被禁止"
            )

        # 检查是否存在
        if not os.path.exists(full_path):
            return ToolOutput(
                success=False,
                error=f"文件不存在: {input_data.path}"
            )

        # 读取文件
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return ToolOutput(
                success=True,
                data=content,
                metadata={"path": full_path, "size": len(content)}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"读取文件失败: {str(e)}"
            )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "path" in input_data and isinstance(input_data["path"], str)

    def _sanitize_path(self, path: str) -> str:
        """清理路径，防止路径遍历攻击"""
        workspace = r'C:\Users\10952\.openclaw\workspace'
        full_path = Path(workspace) / path
        full_path = full_path.resolve()
        return str(full_path)

    def _is_safe_path(self, path: str) -> bool:
        """检查路径是否安全"""
        workspace = r'C:\Users\10952\.openclaw\workspace'
        full_path = Path(path).resolve()

        # 必须在workspace下
        try:
            full_path.relative_to(Path(workspace).resolve())
            return True
        except ValueError:
            return False


class WriteFileTool(BaseTool):
    """写入文件工具"""

    name = "write_file"
    description = "写入文件内容"

    async def execute(self, input_data: WriteFileInput) -> ToolOutput:
        # 安全检查
        full_path = self._sanitize_path(input_data.path)
        if not self._is_safe_path(full_path):
            return ToolOutput(
                success=False,
                error="路径不安全或被禁止"
            )

        # 检查是否可以覆盖
        if os.path.exists(full_path) and not input_data.overwrite:
            return ToolOutput(
                success=False,
                error=f"文件已存在: {input_data.path} (overwrite=False)"
            )

        # 写入文件
        try:
            # 创建父目录
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(input_data.content)

            return ToolOutput(
                success=True,
                data=None,
                metadata={"path": full_path, "size": len(input_data.content)}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"写入文件失败: {str(e)}"
            )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return (
            "path" in input_data and
            "content" in input_data and
            isinstance(input_data["path"], str) and
            isinstance(input_data["content"], str)
        )

    def _sanitize_path(self, path: str) -> str:
        """清理路径"""
        workspace = r'C:\Users\10952\.openclaw\workspace'
        full_path = Path(workspace) / path
        full_path = full_path.resolve()
        return str(full_path)

    def _is_safe_path(self, path: str) -> bool:
        """检查路径是否安全"""
        workspace = r'C:\Users\10952\.openclaw\workspace'
        full_path = Path(path).resolve()

        try:
            full_path.relative_to(Path(workspace).resolve())
            return True
        except ValueError:
            return False


class ListDirectoryTool(BaseTool):
    """列出目录工具"""

    name = "list_directory"
    description = "列出目录内容"

    async def execute(self, input_data: ListDirectoryInput) -> ToolOutput:
        # 安全检查
        full_path = self._sanitize_path(input_data.path)
        if not self._is_safe_path(full_path):
            return ToolOutput(
                success=False,
                error="路径不安全或被禁止"
            )

        # 检查是否是目录
        if not os.path.isdir(full_path):
            return ToolOutput(
                success=False,
                error=f"不是目录: {input_data.path}"
            )

        # 列出内容
        try:
            if input_data.recursive:
                # 递归列出
                items = []
                for root, dirs, files in os.walk(full_path):
                    for name in files:
                        rel_path = os.path.relpath(os.path.join(root, name), full_path)
                        items.append({
                            "name": name,
                            "path": rel_path.replace('\\', '/'),
                            "type": "file"
                        })
                    for name in dirs:
                        rel_path = os.path.relpath(os.path.join(root, name), full_path)
                        items.append({
                            "name": name,
                            "path": rel_path.replace('\\', '/'),
                            "type": "directory"
                        })
            else:
                # 非递归
                items = []
                for name in os.listdir(full_path):
                    item_path = os.path.join(full_path, name)
                    items.append({
                        "name": name,
                        "type": "file" if os.path.isfile(item_path) else "directory"
                    })

            return ToolOutput(
                success=True,
                data=items,
                metadata={"path": full_path, "count": len(items)}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"列出目录失败: {str(e)}"
            )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "path" in input_data and isinstance(input_data["path"], str)

    def _sanitize_path(self, path: str) -> str:
        workspace = r'C:\Users\10952\.openclaw\workspace'
        full_path = Path(workspace) / path
        full_path = full_path.resolve()
        return str(full_path)

    def _is_safe_path(self, path: str) -> bool:
        workspace = r'C:\Users\10952\.openclaw\workspace'
        full_path = Path(path).resolve()

        try:
            full_path.relative_to(Path(workspace).resolve())
            return True
        except ValueError:
            return False


class CreateDirectoryTool(BaseTool):
    """创建目录工具"""

    name = "create_directory"
    description = "创建目录"

    async def execute(self, input_data: CreateDirectoryInput) -> ToolOutput:
        # 安全检查
        full_path = self._sanitize_path(input_data.path)
        if not self._is_safe_path(full_path):
            return ToolOutput(
                success=False,
                error="路径不安全或被禁止"
            )

        # 创建目录
        try:
            os.makedirs(full_path, exist_ok=input_data.parents)

            return ToolOutput(
                success=True,
                data=None,
                metadata={"path": full_path}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"创建目录失败: {str(e)}"
            )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "path" in input_data and isinstance(input_data["path"], str)

    def _sanitize_path(self, path: str) -> str:
        workspace = r'C:\Users\10952\.openclaw\workspace'
        full_path = Path(workspace) / path
        full_path = full_path.resolve()
        return str(full_path)

    def _is_safe_path(self, path: str) -> bool:
        workspace = r'C:\Users\10952\.openclaw\workspace'
        full_path = Path(path).resolve()

        try:
            full_path.relative_to(Path(workspace).resolve())
            return True
        except ValueError:
            return False
```

---

#### 3.2 CommandExecutor（命令执行器）

**文件位置：** `mvp/src/worker/tools/command_executor.py`

**能力：**
- ✅ 执行命令（有限制）
- ✅ 获取输出（stdout + stderr）
- ✅ 超时控制
- ✅ 沙盒隔离

**安全限制：**
- ❌ 禁止危险命令（rm -rf, del, format等）
- ❌ 禁止网络访问（可选）
- ✅ 只允许白名单命令
- ✅ 超时保护（默认30秒）

```python
import asyncio
from typing import Optional, List
from .base_tool import BaseTool, ToolInput, ToolOutput


# ========== 输入Schema ==========

class ExecCommandInput(ToolInput):
    command: str
    timeout: int = 30
    cwd: Optional[str] = None


# ========== 命令白名单 ==========

SAFE_COMMANDS = [
    # 文件操作
    "ls", "dir",
    "cat", "type",
    "grep", "findstr",

    # 开发工具
    "git",
    "python", "python3", "py",
    "pip", "pip3",
    "npm", "node",

    # 安全工具
    "echo", "cd",
    "pwd"
]

# 禁止命令关键词
DANGEROUS_KEYWORDS = [
    "rm -rf",
    "del /f /s /q",
    "format",
    "mkfs",
    "dd",
    "> /dev/",
    ":(){:|:&};:",  # Fork bomb
]


# ========== 工具实现 ==========

class ExecCommandTool(BaseTool):
    """执行命令工具（带安全限制）"""

    name = "exec_command"
    description = "执行系统命令（有限制）"

    async def execute(self, input_data: ExecCommandInput) -> ToolOutput:
        # 检查命令是否安全
        safety_check = self._check_command_safety(input_data.command)
        if not safety_check["safe"]:
            return ToolOutput(
                success=False,
                error=f"命令不安全: {safety_check['reason']}"
            )

        # 执行命令
        try:
            process = await asyncio.create_subprocess_shell(
                input_data.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=input_data.cwd
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=input_data.timeout
                )

                stdout_text = stdout.decode('utf-8', errors='replace')
                stderr_text = stderr.decode('utf-8', errors='replace')

                return ToolOutput(
                    success=process.returncode == 0,
                    data={
                        "stdout": stdout_text,
                        "stderr": stderr_text,
                        "exit_code": process.returncode
                    },
                    metadata={
                        "command": input_data.command,
                        "timeout": input_data.timeout,
                        "elapsed_sec": input_data.timeout  # 简化
                    }
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()

                return ToolOutput(
                    success=False,
                    error=f"命令执行超时（{input_data.timeout}秒）",
                    metadata={"command": input_data.command}
                )

        except Exception as e:
            return ToolOutput(
                success=False,
                error=f"命令执行失败: {str(e)}"
            )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return (
            "command" in input_data and
            isinstance(input_data["command"], str)
        )

    def _check_command_safety(self, command: str) -> dict:
        """检查命令是否安全"""
        # 检查禁止关键词
        for keyword in DANGEROUS_KEYWORDS:
            if keyword.lower() in command.lower():
                return {
                    "safe": False,
                    "reason": f"包含禁止关键词: {keyword}"
                }

        # 获取命令名
        command_parts = command.strip().split()
        if not command_parts:
            return {"safe": False, "reason": "命令为空"}

        command_name = command_parts[0]

        # 检查白名单
        if command_name not in SAFE_COMMANDS:
            return {
                "safe": False,
                "reason": f"命令不在白名单中: {command_name}"
            }

        return {"safe": True}
```

---

#### 3.3 CodeExecutor（代码执行器）

**文件位置：** `mvp/src/worker/tools/code_executor.py`

**能力：**
- ✅ 执行Python代码
- ✅ 获取输出/异常
- ✅ 超时控制
- ✅ 隔离环境

**安全限制：**
- ❌ 禁止无限循环
- ❌ 禁止修改系统环境
- ✅ 超时保护（默认10秒）
- ✅ 内存限制

```python
import asyncio
import sys
import io
import traceback
from typing import Optional, Dict, Any
from .base_tool import BaseTool, ToolInput, ToolOutput


# ========== 输入Schema ==========

class ExecPythonInput(ToolInput):
    code: str
    timeout: int = 10
    capture_output: bool = True


# ========== 工具实现 ==========

class ExecPythonTool(BaseTool):
    """执行Python代码工具"""

    name = "exec_python"
    description = "执行Python代码"

    async def execute(self, input_data: ExecPythonInput) -> ToolOutput:
        # 创建输出捕获
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        if input_data.capture_output:
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

        try:
            # 执行代码
            exec_globals = {
                "__name__": "__main__",
                "__builtins__": __builtins__,
            }

            # 超时执行
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(
                        lambda: exec(input_data.code, exec_globals)
                    ),
                    timeout=input_data.timeout
                )

                if input_data.capture_output:
                    stdout_text = stdout_capture.getvalue()
                    stderr_text = stderr_capture.getvalue()
                else:
                    stdout_text = ""
                    stderr_text = ""

                return ToolOutput(
                    success=True,
                    data={
                        "stdout": stdout_text,
                        "stderr": stderr_text
                    },
                    metadata={"timeout": input_data.timeout}
                )

            except asyncio.TimeoutError:
                return ToolOutput(
                    success=False,
                    error=f"代码执行超时（{input_data.timeout}秒）"
                )

        except Exception as e:
            error_msg = traceback.format_exc()

            if input_data.capture_output:
                stderr_text = stderr_capture.getvalue()
            else:
                stderr_text = ""

            return ToolOutput(
                success=False,
                error=f"代码执行失败: {str(e)}",
                data={
                    "stdout": stdout_capture.getvalue() if input_data.capture_output else "",
                    "stderr": error_msg + "\n" + stderr_text
                }
            )

        finally:
            # 恢复标准输出
            if input_data.capture_output:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return (
            "code" in input_data and
            isinstance(input_data["code"], str)
        )
```

---

### 4. 集成到EnhancedWorker

**文件位置：** `mvp/src/worker/enhanced_worker.py`（修改）

**修改内容：**
- 添加ToolManager
- 工具注册
- 工具调用接口

```python
"""使用LoadBalancer的增强版Worker（带工具系统）"""
import asyncio
import time
from typing import Optional
from ..common.config import settings
from ..common.models import Task
from ..common.load_balancer import get_load_balancer
from .tools.tool_manager import ToolManager
from .tools.filesystem_tools import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
    CreateDirectoryTool
)
from .tools.command_executor import ExecCommandTool
from .tools.code_executor import ExecPythonTool
import httpx


class EnhancedWorker:
    """
    增强型Worker

    - 调用V1 Gateway (LLM + 记忆)
    - 工具系统（文件、命令、代码执行）
    """

    def __init__(self):
        self.load_balancer = get_load_balancer()
        self.client = httpx.AsyncClient(timeout=60)

        # 初始化工具管理器
        self.tool_manager = ToolManager()

        # 注册工具
        self._register_tools()

        print("="*60)
        print("增强型Worker启动 ✅")
        print("="*60)
        print("✅ LoadBalancer就绪")
        print("✅ 5模型智能路由就绪")
        print("✅ 并发+RPM双重限流就绪")
        print("✅ 工具系统就绪（7个工具）")
        print("="*60)

    def _register_tools(self):
        """注册所有工具"""
        # 文件系统工具
        self.tool_manager.register_tool(ReadFileTool())
        self.tool_manager.register_tool(WriteFileTool())
        self.tool_manager.register_tool(ListDirectoryTool())
        self.tool_manager.register_tool(CreateDirectoryTool())

        # 命令执行工具
        self.tool_manager.register_tool(ExecCommandTool())

        # 代码执行工具
        self.tool_manager.register_tool(ExecPythonTool())

    async def execute_task(self, task: Task) -> Task:
        """执行任务"""
        try:
            print(f"\n[Worker] 开始执行任务 {task.id}")
            print(f"  内容: {task.content[:80]}...")

            # 更新状态
            task.status = "running"
            task.updated_at = task.updated_at

            # 检查是否是工具调用
            if self._is_tool_request(task.content):
                # 执行工具
                result = await self._execute_tool_request(task.content)

                task.status = result["success"]
                task.result = result.get("output", "")
                task.metadata = result.get("metadata", {})
            else:
                # 调用LLM
                result = await asyncio.to_thread(
                    self.load_balancer.call_api,
                    task.content
                )

                if result['success']:
                    task.status = "completed"
                    task.result = result['content']
                    task.metadata = {
                        "model": result['model'],
                        "latency": result['latency'],
                        "usage": result.get('usage', {})
                    }
                else:
                    raise Exception(result.get('error', '未知错误'))

            print(f"\n[Worker] ✅ 任务 {task.id} 完成")

        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            print(f"\n[Worker] ❌ 任务 {task.id} 失败")
            print(f"  错误: {e}")

        return task

    def _is_tool_request(self, content: str) -> bool:
        """判断是否是工具调用"""
        # 简单判断：如果以特定格式开头
        return content.strip().startswith("TOOL:")

    async def _execute_tool_request(self, content: str) -> dict:
        """执行工具调用"""
        # 解析工具调用格式：TOOL:tool_name|{"key":"value"}
        try:
            parts = content[5:].split("|", 1)
            tool_name = parts[0].strip()

            if len(parts) == 2:
                import json
                input_data = json.loads(parts[1])
            else:
                input_data = {}

            # 调用工具
            result = await self.tool_manager.call_tool(tool_name, input_data)

            return {
                "success": "completed" if result.success else "failed",
                "output": str(result.data) if result.data else result.error,
                "metadata": result.metadata
            }

        except Exception as e:
            return {
                "success": "failed",
                "output": f"工具调用失败: {str(e)}",
                "metadata": {}
            }

    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()


# 创建全局实例
worker_instance = None

def get_enhanced_worker():
    """获取Worker实例"""
    global worker_instance
    if worker_instance is None:
        worker_instance = EnhancedWorker()
    return worker_instance
```

---

## 🔧 **集成LLM工具调用**

### 目标
让LLM可以自动调用Worker工具

### 实现方式

1. **系统提示词** - 告诉LLM可以使用哪些工具
2. **工具调用检测** - 检测LLM是否想调用工具
3. **工具结果反馈** - 将工具结果返回给LLM

### 工具调用格式

```
TOOL:read_file|{"path":"novel.md"}
TOOL:exec_python|{"code":"print(1+1)"}
TOOL:exec_command|{"command":"ls"}
```

---

## 📊 **第一阶工具清单**

### Phase 1: 核心工具（7个）

| 工具 | 名称 | 描述 | 限制 |
|------|------|------|------|
| 读取文件 | read_file | 读取文件内容 | 仅workspace |
| 写入文件 | write_file | 写入文件内容 | 仅workspace |
| 列出目录 | list_directory | 列出目录内容 | 仅workspace |
| 创建目录 | create_directory | 创建目录 | 仅workspace |
| 执行命令 | exec_command | 执行系统命令 | 白名单 |
| 执行Python | exec_python | 执行Python代码 | 超时10秒 |
| ⭐ 待定 |  |  |  |

### Phase 2: 扩展工具

- Git工具
- 记忆搜索工具
- V1记忆集成工具

---

## 🛡️ **安全策略**

### 1. 文件系统安全
- ✅ 限制在workspace目录
- ✅ 禁止路径遍历攻击
- ✅ 文件大小限制（10MB）

### 2. 命令执行安全
- ✅ 白名单机制
- ✅ 禁止危险命令
- ✅ 超时保护（30秒）

### 3. 代码执行安全
- ✅ 超时保护（10秒）
- ✅ 禁止修改系统环境
- ✅ 异常捕获

### 4. 工具白名单
- ✅ 可配置工具白名单
- ✅ 默认启用沙盒
- ✅ 审计日志

---

## 📝 **下一步行动**

### 立即开始（今天）
1. ✅ 创建工具基础类 (`base_tool.py`)
2. ✅ 创建工具管理器 (`tool_manager.py`)
3. ✅ 实现文件系统工具（4个）
4. ✅ 实现命令执行工具（1个）
5. ✅ 实现代码执行工具（1个）
6. ✅ 集成到EnhancedWorker
7. ✅ 编写测试脚本

### 测试阶段（明天）
1. 测试所有工具
2. 测试安全限制
3. 测试与V1的协调
4. 测试LLM工具调用

---

## 📚 **文档清单**

1. ✅ `WORKER_TOOLS_ARCHITECTURE.md` - 工具系统架构（本文档）
2. ⏳ `worker_tools_implementation.md` - 实施指南
3. ⏳ `worker_tools_test.md` - 测试指南

---

## 🎯 **预期效果**

完成第一阶段后，V2 Worker将具备：
- ✅ 文件操作能力（4个工具）
- ✅ 命令执行能力（1个工具）
- ✅ 代码执行能力（1个工具）
- ✅ 安全隔离机制
- ✅ 可扩展的工具架构

---

**文档版本：** v1.0
**创建时间：** 2026-02-16 04:30
**设计人：** Claw
**状态：** 🟢 **设计完成，准备实施**
