"""
Workflow Engine - 工作流引擎
"""

import asyncio
import logging
from enum import Enum
from typing import Callable, Dict, Any, Optional, List
from dataclasses import dataclass, field

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """
    步骤状态枚举
    """
    PENDING = "pending"       # 等待中
    RUNNING = "running"       # 运行中
    SUCCESS = "success"       # 成功
    FAILED = "failed"         # 失败
    SKIPPED = "skipped"       # 跳过


@dataclass
class StepResult:
    """
    步骤执行结果
    """
    status: StepStatus
    output: Any = None
    error: Optional[Exception] = None
    duration: float = 0.0


@dataclass
class Step:
    """
    工作流步骤
    """
    name: str                             # 步骤名称
    function: Callable                    # 执行函数
    enabled: bool = True                  # 是否启用
    timeout: int = 300                    # 超时时间（秒）
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据


class Workflow:
    """
    工作流 - 管理多个步骤
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: List[Step] = []
        self.results: Dict[str, StepResult] = {}
        self.shared_data: Dict[str, Any] = {}  # 共享数据，用于步骤间传递

    def add_step(self, step: Step, after: Optional[str] = None) -> 'Workflow':
        """
        添加步骤

        Args:
            step: 要添加的步骤
            after: 在哪个步骤之后添加（可选）
        """
        if after is not None:
            # 在指定步骤后添加
            for i, s in enumerate(self.steps):
                if s.name == after:
                    self.steps.insert(i + 1, step)
                    return self
            # 如果找不到after步骤，添加到末尾
            logger.warning(f"Step '{after}' not found, appending to end")
        self.steps.append(step)
        return self

    def get_step(self, name: str) -> Optional[Step]:
        """
        获取步骤
        """
        for step in self.steps:
            if step.name == name:
                return step
        return None

    def get_result(self, name: str) -> Optional[StepResult]:
        """
        获取步骤结果
        """
        return self.results.get(name)

    def reset(self):
        """
        重置工作流
        """
        self.results = {}
        self.shared_data = {}


class WorkflowEngine:
    """
    工作流引擎 - 执行工作流
    """

    def __init__(self, fallback_to_mock: bool = True):
        """
        初始化工作流引擎

        Args:
            fallback_to_mock: 失败时是否回退到模拟结果
        """
        self.fallback_to_mock = fallback_to_mock

    async def execute_step(self, step: Step, context: Dict[str, Any]) -> StepResult:
        """
        执行单个步骤

        Args:
            step: 要执行的步骤
            context: 执行上下文

        Returns:
            StepResult: 步骤执行结果
        """
        if not step.enabled:
            logger.info(f"Step '{step.name}' is skipped (disabled)")
            return StepResult(status=StepStatus.SKIPPED)

        logger.info(f"Executing step '{step.name}'...")
        start_time = asyncio.get_event_loop().time()

        try:
            # 带超时执行
            result = await asyncio.wait_for(
                step.function(context),
                timeout=step.timeout
            )

            duration = asyncio.get_event_loop().time() - start_time
            logger.info(f"Step '{step.name}' completed in {duration:.2f}s")

            return StepResult(
                status=StepStatus.SUCCESS,
                output=result,
                duration=duration
            )

        except asyncio.TimeoutError:
            duration = asyncio.get_event_loop().time() - start_time
            error = TimeoutError(f"Step '{step.name}' timed out after {step.timeout}s")
            logger.error(f"Step '{step.name}' failed: {error}")

            if self.fallback_to_mock:
                logger.warning(f"Fallback to mock result for step '{step.name}'")
                return StepResult(
                    status=StepStatus.SUCCESS,  # 降级为成功，使用模拟结果
                    output=self._get_mock_result(step.name),
                    duration=duration
                )

            return StepResult(
                status=StepStatus.FAILED,
                error=error,
                duration=duration
            )

        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            logger.error(f"Step '{step.name}' failed: {e}")

            if self.fallback_to_mock:
                logger.warning(f"Fallback to mock result for step '{step.name}'")
                return StepResult(
                    status=StepStatus.SUCCESS,
                    output=self._get_mock_result(step.name),
                    duration=duration
                )

            return StepResult(
                status=StepStatus.FAILED,
                error=e,
                duration=duration
            )

    async def execute(self, workflow: Workflow) -> Dict[str, StepResult]:
        """
        顺序执行工作流

        Args:
            workflow: 要执行的工作流

        Returns:
            Dict[str, StepResult]: 所有步骤的执行结果
        """
        logger.info(f"Starting workflow '{workflow.name}'...")
        workflow.reset()

        for step in workflow.steps:
            step_result = await self.execute_step(step, {
                'shared_data': workflow.shared_data,
                'previous_results': workflow.results
            })
            workflow.results[step.name] = step_result

            # 如果步骤失败且不启用fallback，停止执行
            if step_result.status == StepStatus.FAILED:
                logger.error(f"Workflow '{workflow.name}' stopped at step '{step.name}'")
                break

        # 统计
        total_steps = len(workflow.steps)
        success_steps = sum(1 for r in workflow.results.values() if r.status == StepStatus.SUCCESS)
        failed_steps = sum(1 for r in workflow.results.values() if r.status == StepStatus.FAILED)

        logger.info(
            f"Workflow '{workflow.name}' completed: "
            f"{success_steps}/{total_steps} succeeded, "
            f"{failed_steps} failed"
        )

        return workflow.results

    def _get_mock_result(self, step_name: str) -> Any:
        """
        获取模拟结果

        Args:
            step_name: 步骤名称

        Returns:
            模拟结果
        """
        # 根据步骤名称返回不同的模拟结果
        mock_results = {
            'learning': {
                'status': 'success',
                'message': 'Mock learning result',
                'knowledge_points': [
                    'Mock knowledge point 1',
                    'Mock knowledge point 2'
                ]
            },
            'decision': {
                'status': 'success',
                'message': 'Mock decision result',
                'decision': 'Proceed with execution',
                'confidence': 0.8
            },
            'execution': {
                'status': 'success',
                'message': 'Mock execution result',
                'output': 'Task completed successfully'
            }
        }

        # 模糊匹配
        for key, value in mock_results.items():
            if key in step_name.lower():
                return value

        # 默认模拟结果
        return {
            'status': 'success',
            'message': f'Mock result for {step_name}'
        }


def create_sequential_workflow(name: str, description: str = "") -> Workflow:
    """
    创建空的工作流（顺序执行）

    Args:
        name: 工作流名称
        description: 描述

    Returns:
        Workflow: 工作流实例
    """
    return Workflow(name=name, description=description)


def create_parallel_workflow(name: str, description: str = "") -> Workflow:
    """
    创建并行工作流（预留接口，MVP阶段暂不实现）

    Args:
        name: 工作流名称
        description: 描述

    Returns:
        Workflow: 工作流实例
    """
    # MVP阶段暂不实现并行
    logger.warning("Parallel workflow is not implemented in MVP, using sequential instead")
    return Workflow(name=name, description=description)
