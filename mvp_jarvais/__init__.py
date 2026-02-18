"""
MVP JARVIS - 超越钢铁侠JARVIS的全能AI

核心系统：
- MemoryManager: 三层记忆系统（Redis + ChromaDB + SQLite）
- KnowledgeAgent: 知识问答智能体
- AgentManager: 多Agent协调器
- ToolIntegration: 工具整合

战略目标：成为超越JARVIS的个人AI
"""

__version__ = "0.1.0"
__author__ = "博 + Claw"
__description__ = "MVP全能AI系统 - 对齐终极目标（超越JARVIS）"

# 导出核心组件
from .core.memory_manager import MemoryManager, get_memory_manager
from .agents.knowledge_agent import KnowledgeAgent

__all__ = [
    "MemoryManager",
    "get_memory_manager",
    "KnowledgeAgent"
]
