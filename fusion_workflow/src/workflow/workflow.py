"""
工作流工厂函数
"""

from .engine import create_sequential_workflow, create_parallel_workflow

__all__ = [
    'create_sequential_workflow',
    'create_parallel_workflow',
]
