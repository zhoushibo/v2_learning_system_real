"""
Fusion Workflow Engine
融合工作流引擎 - 协调学习/决策/执行三大引擎
"""

from .engine import WorkflowEngine, Step, StepStatus, Workflow
from .workflow import create_sequential_workflow, create_parallel_workflow

__all__ = [
    'WorkflowEngine',
    'Step',
    'StepStatus',
    'Workflow',
    'create_sequential_workflow',
    'create_parallel_workflow',
]

__version__ = '0.1.0-MVP'
