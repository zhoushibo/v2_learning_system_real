"""
AgentManager - 多 Agent 协调器（带全链路日志）

职责：
1. 智能路由用户输入到合适的 Agent
2. 协调多个 Agent 执行任务
3. 管理 Agent 生命周期
4. 全链路日志追踪（诊断慢/卡/错误问题）

Agent 列表：
- ChatAgent: 对话 Agent（Gateway 流式）
- TaskAgent: 任务 Agent（Worker Pool 调度）
- KnowledgeAgent: 知识 Agent（记忆搜索）
"""

import asyncio
import re
from typing import Optional, Dict
from enum import Enum
import logging
from datetime import datetime
import sys
import os

# 添加项目和根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.dirname(project_root))

# 使用绝对导入
from mvp_jarvais.agents.knowledge_agent import KnowledgeAgent
from task_logger import TaskLogger

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent 类型枚举"""
    CHAT = "chat"
    KNOWLEDGE = "knowledge"
    TASK = "task"


class IntentType(Enum):
    """意图类型枚举"""
    KNOWLEDGE_QUERY = "knowledge_query"      # 知识查询
    TASK_EXECUTION = "task_execution"        # 任务执行
    CONVERSATION = "conversation"           # 日常对话
    LEARNING = "learning"                   # 持续学习


class AgentManager:
    """
    多 Agent 协调器（带全链路日志）

    核心能力：
    1. 意图识别（分析用户输入）
    2. Agent 路由（选择最适合的 Agent）
    3. 任务协调（多 Agent 协作）
    4. 结果整合（统一输出格式）
    5. 全链路日志（诊断慢/卡/错误）
    """

    def __init__(self, memory_manager):
        """
        初始化 AgentManager

        Args:
            memory_manager: 记忆管理器实例
        """
        self.memory = memory_manager

        # 初始化 Agent
        self.knowledge_agent = KnowledgeAgent(memory_manager)
        self.chat_agent = BasicChatAgent()
        self.task_agent = BasicTaskAgent()

        # 意图识别关键词
        self.intent_keywords = {
            IntentType.KNOWLEDGE_QUERY: [
                "记住", "回忆", "搜索", "查询", "找", "知识",
                "项目", "进展", "目标", "资产", "规则", "历史"
            ],
            IntentType.TASK_EXECUTION: [
                "执行", "运行", "命令", "安装", "部署", "测试",
                "build", "run", "npm", "python", "shell"
            ],
            IntentType.LEARNING: [
                "学习", "研究", "了解", "分析", "调查"
            ],
            IntentType.CONVERSATION: [
                "你好", "谢谢", "早上好", "晚上好", "再见",
                "哈哈", "😊", "开心", "难过"
            ]
        }

        logger.info("✅ AgentManager 初始化完成（带全链路日志）")

    async def route(self, user_input: str, enable_logging: bool = True) -> Dict:
        """
        智能路由用户输入到合适的 Agent（带全链路日志）

        流程：
        1. 意图识别
        2. Agent 选择
        3. 执行
        4. 结果整合

        Args:
            user_input: 用户输入
            enable_logging: 是否启用全链路日志（默认 True）

        Returns:
            Dict: 统一格式结果
        """
        # 创建任务日志器
        task_logger = TaskLogger(f"Agent 路由：{user_input[:50]}")
        
        try:
            async with task_logger.step("1. 意图识别", metadata={"input": user_input[:100]}):
                intent = await self._analyze_intent(user_input)
                logger.info(f"  意图类型：{intent.value}")

            # 步骤 2: Agent 选择和执行
            async with task_logger.step("2. Agent 路由", metadata={"intent": intent.value}):
                if intent == IntentType.KNOWLEDGE_QUERY:
                    result = await self._route_to_knowledge(user_input, task_logger)
                elif intent == IntentType.TASK_EXECUTION:
                    result = await self._route_to_task(user_input, task_logger)
                elif intent == IntentType.LEARNING:
                    result = await self._route_to_learning(user_input, task_logger)
                else:  # CONVERSATION
                    result = await self._route_to_chat(user_input, task_logger)

            # 步骤 3: 结果整合
            async with task_logger.step("3. 结果整合"):
                response_data = {
                    "type": intent.value,
                    "agent": result.get("agent", "unknown"),
                    "response": result.get("response", ""),
                    "metadata": result.get("metadata", {}),
                    "timestamp": datetime.now().isoformat()
                }
                logger.info(f"✅ 路由完成：{response_data['agent']}")

            return response_data

        except Exception as e:
            logger.error(f"❌ Agent 路由失败：{e}")
            raise
        finally:
            # 生成诊断报告
            if enable_logging:
                report = task_logger.generate_report(format="text")
                logger.info(f"\n📋 路由诊断报告:\n{report}")

    async def _analyze_intent(self, user_input: str) -> IntentType:
        """意图识别"""
        input_lower = user_input.lower()

        # 特殊处理：记住命令
        if input_lower.startswith("记住") or "记住：" in input_lower:
            return IntentType.KNOWLEDGE_QUERY

        # 关键词匹配
        scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for kw in keywords if kw in input_lower)
            scores[intent] = score

        # 选择分数最高的意图
        max_intent = max(scores.items(), key=lambda x: x[1])
        if max_intent[1] > 0:
            return max_intent[0]

        # 默认：对话意图
        return IntentType.CONVERSATION

    async def _route_to_knowledge(self, user_input: str, task_logger: TaskLogger) -> Dict:
        """路由到知识 Agent"""
        logger.info("  → 路由到 KnowledgeAgent")

        async with task_logger.step("2.1 KnowledgeAgent 查询"):
            result = await self.knowledge_agent.query(user_input)

        return {
            "agent": "KnowledgeAgent",
            "response": result.get("answer", ""),
            "metadata": {
                "confidence": result.get("confidence"),
                "sources": result.get("sources")
            }
        }

    async def _route_to_task(self, user_input: str, task_logger: TaskLogger) -> Dict:
        """路由到任务 Agent"""
        logger.info("  → 路由到 TaskAgent")

        async with task_logger.step("2.1 TaskAgent 执行"):
            result = await self.task_agent.execute(user_input)

        return {
            "agent": "TaskAgent",
            "response": result,
            "metadata": {
                "status": "completed"
            }
        }

    async def _route_to_learning(self, user_input: str, task_logger: TaskLogger) -> Dict:
        """路由到学习功能"""
        logger.info("  → 路由到 Learning")

        async with task_logger.step("2.1 提取学习主题"):
            topic = user_input.replace("学习", "").replace("研究", "").strip()

        if not topic:
            return {
                "agent": "Learning",
                "response": "请指定学习主题。例如：帮我学习 ChromaDB 向量搜索",
                "metadata": {}
            }

        async with task_logger.step("2.2 KnowledgeAgent 学习"):
            result = await self.knowledge_agent.learn(topic)

        return {
            "agent": "Learning",
            "response": result.get("message", ""),
            "metadata": {
                "status": result.get("status"),
                "topic": topic
            }
        }

    async def _route_to_chat(self, user_input: str, task_logger: TaskLogger) -> Dict:
        """路由到对话 Agent"""
        logger.info("  → 路由到 ChatAgent")

        async with task_logger.step("2.1 ChatAgent 对话"):
            response = await self.chat_agent.chat(user_input)

        return {
            "agent": "ChatAgent",
            "response": response,
            "metadata": {
                "mood": "friendly"
            }
        }

    async def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "type": "AgentManager",
            "agents": {
                "knowledge": "KnowledgeAgent",
                "task": "TaskAgent",
                "chat": "ChatAgent"
            },
            "intents": [it.value for it in IntentType],
            "timestamp": datetime.now().isoformat()
        }


# ==================== 基础 Agent 实现 ====================

class BasicChatAgent:
    """基础对话 Agent"""

    async def chat(self, message: str) -> str:
        """处理对话"""
        greetings = {
            "你好": "你好！很高兴见到你！",
            "谢谢": "不客气！随时为您服务",
            "早上好": "早上好！祝你今天过得愉快",
            "晚上好": "晚上好！今天过得怎么样？",
            "再见": "再见！期待下次聊天"
        }

        for key, value in greetings.items():
            if key in message:
                return value

        return f"你说的是：{message}。我正在学习中，越来越聪明！"


class BasicTaskAgent:
    """基础任务 Agent"""

    async def execute(self, task: str) -> str:
        """执行任务"""
        return f"任务执行：{task}（任务 Agent 开发中，暂未完成）"


# ==================== 测试代码 ====================

async def main():
    """测试 AgentManager（带全链路日志）"""
    print("="*70)
    print("🎯 AgentManager 测试（带全链路日志）")
    print("="*70)

    from mvp_jarvais.core.memory_manager import MemoryManager

    # 创建记忆管理器
    memory = MemoryManager(enable_v1=False)

    # 创建 AgentManager
    manager = AgentManager(memory)
    print("\n✅ AgentManager 初始化完成")

    # 记住一些测试数据
    print("\n📝 记住测试数据")
    await memory.remember(
        key="project_status",
        content="V2 CLI 系统开发进度：90%（MemoryManager + KnowledgeAgent + AgentManager + ToolEngine 已完成）",
        metadata={"type": "status", "progress": "90%"}
    )

    # 测试路由（带全链路日志）
    print("\n🧪 智能路由测试（带全链路日志）")

    test_inputs = [
        ("我们的项目进展如何？", "知识查询"),
        ("帮我学习向量搜索", "学习"),
        ("执行 npm install", "任务"),
        ("你好", "对话"),
    ]

    for user_input, expected_intent in test_inputs:
        print(f"\n{'='*60}")
        print(f"👤 用户：{user_input}")
        print(f"🎯 预期意图：{expected_intent}")
        print("="*60)

        result = await manager.route(user_input, enable_logging=True)

        print(f"\n🎯 实际意图：{result['type']}")
        print(f"🤖 路由 Agent: {result['agent']}")
        print(f"💬 响应：{result['response'][:100]}...")

    # 统计
    print("\n" + "="*70)
    print("📈 统计信息")
    print("="*70)
    stats = await manager.get_stats()
    print(f"  Manager 类型：{stats['type']}")
    print(f"  可用 Agent: {list(stats['agents'].keys())}")
    print(f"  支持意图：{stats['intents']}")

    print("\n✅ 测试完成！")


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
