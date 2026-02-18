"""
TaskLogger - 全链路任务日志追踪系统

功能：
1. 自动记录每个步骤的开始/结束时间
2. 计算耗时
3. 记录成功/失败状态
4. 捕获错误详情和堆栈
5. 生成时间线报告
6. 支持嵌套任务追踪

使用场景：
- 诊断 OpenClaw 慢/卡/无响应问题
- 性能分析
- 错误定位
"""

import asyncio
import time
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import traceback
import sys

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class TaskStep:
    """任务步骤记录"""
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    error: Optional[str] = None
    error_trace: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List['TaskStep'] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "status": self.status.value,
            "error": self.error,
            "error_trace": self.error_trace,
            "metadata": self.metadata,
            "children": [child.to_dict() for child in self.children]
        }


class TaskLogger:
    """
    全链路任务日志追踪器

    使用方式：
    logger = TaskLogger("用户任务")
    async with logger.step("初始化"):
        # 执行初始化
        pass

    async with logger.step("调用工具", metadata={"tool": "web_search"}):
        # 调用工具
        pass

    # 生成报告
    report = logger.generate_report()
    print(report)
    """

    def __init__(self, task_name: str, log_level: int = logging.INFO):
        """
        初始化任务日志器

        Args:
            task_name: 任务名称
            log_level: 日志级别
        """
        self.task_name = task_name
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.status = TaskStatus.PENDING
        self.root_step: Optional[TaskStep] = None
        self.current_step: Optional[TaskStep] = None
        self.steps: List[TaskStep] = []
        self.log_level = log_level

        # 配置日志
        self._setup_logging()

        logger.info(f"📋 任务日志器初始化：{task_name}")

    def _setup_logging(self):
        """配置日志输出"""
        # 确保日志输出到控制台
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(self.log_level)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(self.log_level)

    def step(self, name: str, metadata: Optional[Dict] = None) -> 'TaskStepContext':
        """
        创建一个步骤上下文

        Args:
            name: 步骤名称
            metadata: 额外元数据

        Returns:
            TaskStepContext 上下文管理器
        """
        return TaskStepContext(self, name, metadata)

    def _start_step(self, name: str, metadata: Optional[Dict] = None) -> TaskStep:
        """开始一个步骤"""
        step = TaskStep(
            name=name,
            start_time=time.time(),
            metadata=metadata or {}
        )

        if self.current_step:
            self.current_step.children.append(step)
        elif not self.root_step:
            self.root_step = step

        self.current_step = step
        self.steps.append(step)

        logger.info(f"▶️  开始：{name}")
        return step

    def _end_step(self, step: TaskStep, success: bool = True, error: Optional[str] = None):
        """结束一个步骤"""
        step.end_time = time.time()
        step.duration = step.end_time - step.start_time

        if success:
            step.status = TaskStatus.SUCCESS
            logger.info(f"✅ 完成：{step.name} (耗时：{step.duration:.3f}秒)")
        else:
            step.status = TaskStatus.FAILED
            step.error = error
            step.error_trace = traceback.format_exc()
            logger.error(f"❌ 失败：{step.name} - {error}")

        # 返回到父步骤
        if self.current_step and self.current_step.children and self.current_step.children[-1] == step:
            # 找到父步骤
            parent = None
            for s in reversed(self.steps):
                if step in s.children:
                    parent = s
                    break
            self.current_step = parent

    def generate_report(self, format: str = "text") -> str:
        """
        生成任务报告

        Args:
            format: 输出格式 ("text", "json", "markdown")

        Returns:
            格式化的报告
        """
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time

        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.SUCCESS

        if format == "json":
            return json.dumps(self._to_dict(total_duration), indent=2, ensure_ascii=False)
        elif format == "markdown":
            return self._generate_markdown_report(total_duration)
        else:
            return self._generate_text_report(total_duration)

    def _to_dict(self, total_duration: float) -> Dict:
        """转换为字典"""
        return {
            "task_name": self.task_name,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "total_duration": total_duration,
            "status": self.status.value,
            "steps": [step.to_dict() for step in self.steps],
            "summary": self._generate_summary()
        }

    def _generate_summary(self) -> Dict:
        """生成摘要统计"""
        total_duration = sum(s.duration or 0 for s in self.steps)
        failed_steps = [s for s in self.steps if s.status == TaskStatus.FAILED]
        slow_steps = [s for s in self.steps if (s.duration or 0) > 5.0]

        return {
            "total_steps": len(self.steps),
            "successful_steps": len(self.steps) - len(failed_steps),
            "failed_steps": len(failed_steps),
            "total_duration": total_duration,
            "avg_duration": total_duration / len(self.steps) if self.steps else 0,
            "slow_steps": [s.name for s in slow_steps],
            "errors": [s.error for s in failed_steps if s.error]
        }

    def _generate_text_report(self, total_duration: float) -> str:
        """生成文本报告"""
        lines = []
        lines.append("="*70)
        lines.append(f"📋 任务报告：{self.task_name}")
        lines.append("="*70)
        lines.append(f"开始时间：{datetime.fromtimestamp(self.start_time).strftime('%H:%M:%S')}")
        lines.append(f"结束时间：{datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else 'N/A'}")
        lines.append(f"总耗时：{total_duration:.3f}秒")
        lines.append(f"状态：{self.status.value}")
        lines.append("")
        lines.append("步骤详情:")
        lines.append("-"*70)

        for i, step in enumerate(self.steps, 1):
            indent = "  " * (len(step.name) - len(step.name.lstrip()))
            status_icon = {
                TaskStatus.SUCCESS: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.TIMEOUT: "⏰",
                TaskStatus.RUNNING: "▶️",
                TaskStatus.PENDING: "⏳"
            }.get(step.status, "❓")

            duration_str = f"{step.duration:.3f}s" if step.duration else "N/A"
            lines.append(f"{indent}{i}. {status_icon} {step.name}")
            lines.append(f"{indent}   耗时：{duration_str}")

            if step.error:
                lines.append(f"{indent}   错误：{step.error}")

            if step.metadata:
                lines.append(f"{indent}   元数据：{step.metadata}")

            lines.append("")

        # 摘要
        summary = self._generate_summary()
        lines.append("-"*70)
        lines.append("摘要:")
        lines.append(f"  总步骤数：{summary['total_steps']}")
        lines.append(f"  成功：{summary['successful_steps']}")
        lines.append(f"  失败：{summary['failed_steps']}")
        lines.append(f"  平均耗时：{summary['avg_duration']:.3f}秒")

        if summary['slow_steps']:
            lines.append(f"  慢步骤 (>5 秒): {', '.join(summary['slow_steps'])}")

        if summary['errors']:
            lines.append(f"  错误列表:")
            for err in summary['errors']:
                lines.append(f"    - {err}")

        lines.append("="*70)

        return "\n".join(lines)

    def _generate_markdown_report(self, total_duration: float) -> str:
        """生成 Markdown 报告"""
        lines = []
        lines.append(f"# 📋 任务报告：{self.task_name}\n")
        lines.append(f"**开始时间:** {datetime.fromtimestamp(self.start_time).strftime('%H:%M:%S')}")
        lines.append(f"**结束时间:** {datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else 'N/A'}")
        lines.append(f"**总耗时:** {total_duration:.3f}秒\n")
        lines.append(f"**状态:** {self.status.value}\n")
        lines.append("## 步骤详情\n")
        lines.append("| # | 步骤 | 状态 | 耗时 | 错误 |")
        lines.append("|---|------|------|------|------|")

        for i, step in enumerate(self.steps, 1):
            status_icon = {
                TaskStatus.SUCCESS: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.TIMEOUT: "⏰",
            }.get(step.status, "❓")
            duration_str = f"{step.duration:.3f}s" if step.duration else "N/A"
            error_str = step.error[:50] + "..." if step.error and len(step.error) > 50 else (step.error or "-")

            lines.append(f"| {i} | {step.name} | {status_icon} {step.status.value} | {duration_str} | {error_str} |")

        lines.append("\n## 摘要\n")
        summary = self._generate_summary()
        lines.append(f"- **总步骤数:** {summary['total_steps']}")
        lines.append(f"- **成功:** {summary['successful_steps']}")
        lines.append(f"- **失败:** {summary['failed_steps']}")
        lines.append(f"- **平均耗时:** {summary['avg_duration']:.3f}秒")

        if summary['slow_steps']:
            lines.append(f"- **慢步骤 (>5 秒):** {', '.join(summary['slow_steps'])}")

        return "\n".join(lines)


class TaskStepContext:
    """任务步骤上下文管理器"""

    def __init__(self, task_logger: TaskLogger, name: str, metadata: Optional[Dict] = None):
        self.task_logger = task_logger
        self.name = name
        self.metadata = metadata
        self.step: Optional[TaskStep] = None

    def __enter__(self) -> 'TaskStepContext':
        self.step = self.task_logger._start_step(self.name, self.metadata)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.task_logger._end_step(self.step, success=True)
        else:
            error_msg = f"{exc_type.__name__}: {exc_val}"
            self.task_logger._end_step(self.step, success=False, error=error_msg)
        return False  # 不抑制异常

    async def __aenter__(self) -> 'TaskStepContext':
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.__exit__(exc_type, exc_val, exc_tb)


# ==================== 便捷函数 ====================

def log_task(task_name: str, log_level: int = logging.INFO):
    """装饰器：自动记录函数执行"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            task_logger = TaskLogger(f"{task_name}:{func.__name__}", log_level)

            async with task_logger.step("函数执行"):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    raise
                finally:
                    report = task_logger.generate_report(format="text")
                    logger.info(f"\n{report}")

        return wrapper
    return decorator


# ==================== 测试代码 ====================

async def test_task_logger():
    """测试 TaskLogger"""
    print("="*70)
    print("📋 TaskLogger 测试")
    print("="*70)

    # 创建日志器
    task_logger = TaskLogger("测试任务：OpenClaw 命令执行")

    async with task_logger.step("初始化"):
        await asyncio.sleep(0.5)
        print("  初始化完成")

    async with task_logger.step("准备命令", metadata={"command": "echo Hello"}):
        await asyncio.sleep(0.3)
        print("  命令准备完成")

    async with task_logger.step("执行命令"):
        await asyncio.sleep(1.2)
        print("  命令执行完成")

    async with task_logger.step("处理结果"):
        await asyncio.sleep(0.4)
        print("  结果处理完成")

    # 模拟一个错误
    try:
        async with task_logger.step("错误测试"):
            await asyncio.sleep(0.2)
            raise ValueError("这是一个测试错误")
    except ValueError:
        pass

    # 生成报告
    print("\n" + "="*70)
    print("生成报告:")
    print("="*70)

    # 文本报告
    report_text = task_logger.generate_report(format="text")
    print(report_text)

    # JSON 报告
    print("\nJSON 报告:")
    report_json = task_logger.generate_report(format="json")
    print(report_json[:500] + "...")

    # Markdown 报告
    print("\nMarkdown 报告:")
    report_md = task_logger.generate_report(format="markdown")
    print(report_md)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_task_logger())
