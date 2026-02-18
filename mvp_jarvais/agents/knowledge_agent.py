"""
KnowledgeAgent - 知识问答智能体

职责：
1. 语义搜索记忆（ChromaDB向量匹配）
2. 上下文自动回忆（STATE.json + MEMORY.md）
3. 知识整合（V2学习系统学习的内容）
4. 持续学习（对话中学习）
"""

import sys
import os
import asyncio
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from ..core.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class KnowledgeAgent:
    """
    知识问答智能体
    
    能力：
    1. 语义检索记忆库
    2. 上下文回忆
    3. 知识整合推理
    4. 持续学习能力
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        初始化KnowledgeAgent
        
        Args:
            memory_manager: 记忆管理器实例
        """
        self.memory = memory_manager
        
        # 加载上下文文件
        self.context_files = {
            "STATE": "STATE.json",
            "MEMORY": "MEMORY.md"
        }
        
        logger.info("✅ KnowledgeAgent初始化完成")
    
    # ==================== 核心能力 ====================
    
    async def query(self, question: str, use_memory: bool = True, use_context: bool = True) -> Dict[str, Any]:
        """
        查询知识
        
        流程：
        1. 向量搜索记忆库
        2. 检索上下文文件（STATE.json, MEMORY.md）
        3. 整合答案（调用LLM）
        4. 记住这次对话
        
        Args:
            question: 用户问题
            use_memory: 是否使用记忆库搜索
            use_context: 是否使用上下文文件
            
        Returns:
            Dict: {answer, sources, confidence}
        """
        logger.info(f"🔍 知识查询: {question}")
        
        # 步骤1: 搜索记忆库
        memory_results = []
        if use_memory:
            memory_results = await self.memory.search(question, n_results=5)
            logger.info(f"  记忆搜索: 找到{len(memory_results)}条相关记忆")
        
        # 步骤2: 加载上下文文件
        context_data = {}
        if use_context:
            context_data = await self._load_context_files()
            logger.info(f"  上下文: 加载{len(context_data)}个文件")
        
        # 步骤3: 整合答案（简化版：直接返回记忆结果）
        # TODO: 调用LLM生成完整答案
        answer = self._generate_answer_simple(question, memory_results, context_data)
        
        # 步骤4: 记住这次对话
        await self._remember_conversation(question, answer, memory_results)
        
        return {
            "answer": answer,
            "sources": {
                "memory": len(memory_results),
                "context": list(context_data.keys())
            },
            "confidence": self._calculate_confidence(answer, memory_results, context_data),
            "timestamp": datetime.now().isoformat()
        }
    
    async def learn(self, topic: str, save_to_memory: bool = True) -> Dict[str, Any]:
        """
        学习新知识（调用V2学习系统）
        
        Args:
            topic: 学习主题
            save_to_memory: 是否保存到记忆库
            
        Returns:
            Dict: 学习结果
        """
        logger.info(f"📚 学习主题: {topic}")
        
        try:
            # TODO: 调用V2学习系统
            # learning_system = V2LearningSystem()
            # result = await learning_system.learn(topic)
            
            # 临时返回模拟结果
            result = {
                "status": "success",
                "topic": topic,
                "knowledge_points": ["知识点1", "知识点2", "知识点3"],
                "message": "学习完成（模拟）"
            }
            
            # 保存到记忆库
            if save_to_memory:
                await self.memory.remember(
                    key=f"learning_{uuid.uuid4()}",
                    content=f"学习主题: {topic}",
                    metadata={
                        "type": "learning",
                        "topic": topic,
                        "knowledge_points": result.get("knowledge_points", []),
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            logger.info(f"✅ 学习完成: {topic}")
            return result
            
        except Exception as e:
            logger.error(f"学习失败 [{topic}]: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "学习失败"
            }
    
    async def summarize_context(self) -> Dict[str, Any]:
        """
        总结当前上下文（STATE.json + MEMORY.md）
        
        Returns:
            Dict: 上下文摘要
        """
        logger.info("📋 总结上下文")
        
        context_data = await self._load_context_files()
        
        summary = {
            "state": context_data.get("STATE", {}).get("current_state", {}),
            "rules": list(context_data.get("MEMORY", {}).get("permanent_core_rules", {}).keys()),
            "completed_projects": list(context_data.get("STATE", {}).get("completed_projects", {}).keys()),
            "next_tasks": context_data.get("STATE", {}).get("next_tasks", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ 上下文总结完成: {len(summary['completed_projects'])}个已完成项目")
        return summary
    
    # ==================== 辅助方法 ====================
    
    async def _load_context_files(self) -> Dict[str, Any]:
        """加载上下文文件"""
        context = {}
        
        for name, filename in self.context_files.items():
            try:
                if filename.endswith('.json'):
                    with open(filename, 'r', encoding='utf-8') as f:
                        context[name] = json.load(f)
                else:
                    with open(filename, 'r', encoding='utf-8') as f:
                        context[name] = {"content": f.read()}
            except Exception as e:
                logger.warning(f"加载上下文文件失败 [{filename}]: {e}")
        
        return context
    
    def _generate_answer_simple(self, question: str, memory_results: List[Dict], context_data: Dict) -> str:
        """
        生成答案（简化版）
        
        TODO: 集成LLM调用生成完整答案
        
        Args:
            question: 用户问题
            memory_results: 记忆搜索结果
            context_data: 上下文数据
            
        Returns:
            str: 答案
        """
        # 简化版：直接反馈找到的记忆
        if memory_results:
            answer_parts = []
            answer_parts.append(f"📚 根据你的问题「{question}」，我在记忆中找到以下内容：\n")
            
            for i, result in enumerate(memory_results, 1):
                content = result.get('content', '')
                answer_parts.append(f"{i}. {content}\n")
            
            if context_data.get("STATE"):
                current_phase = context_data["STATE"].get("current_state", {}).get("phase")
                if current_phase:
                    answer_parts.append(f"\n💡 当前阶段: {current_phase}")
            
            return "".join(answer_parts)
        else:
            return f"我没有找到关于「{question}」的相关记忆。不过，通过持续学习，我会越来越聪明！"
    
    def _calculate_confidence(self, answer: str, memory_results: List, context_data: Dict) -> float:
        """
        计算答案置信度
        
        Args:
            answer: 答案
            memory_results: 记忆结果
            context_data: 上下文数据
            
        Returns:
            float: 置信度（0.0 - 1.0）
        """
        confidence = 0.0
        
        # 基于记忆结果数量
        if memory_results:
            confidence += min(len(memory_results) * 0.2, 0.6)
        
        # 基于上下文数据
        if context_data.get("STATE") or context_data.get("MEMORY"):
            confidence += 0.3
        
        # 基于答案长度
        if len(answer) > 100:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def _remember_conversation(self, question: str, answer, memory_results: List):
        """
        记住对话
        
        Args:
            question: 用户问题
            answer: AI答案（可能str或dict）
            memory_results: 使用的记忆
        """
        conversation_key = f"conversation_{uuid.uuid4()}"
        
        # 确保answer是字典格式
        if isinstance(answer, str):
            answer_text = answer
            confidence = 0.0
        else:
            answer_text = answer.get('answer', '')
            confidence = answer.get('confidence', 0.0)
        
        await self.memory.remember(
            key=conversation_key,
            content=f"Q: {question}\nA: {answer_text}",
            metadata={
                "type": "conversation",
                "question": question,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计数据
        """
        return {
            "type": "KnowledgeAgent",
            "context_files": list(self.context_files.values()),
            "timestamp": datetime.now().isoformat()
        }


# ==================== 测试代码 ====================

async def main():
    """测试KnowledgeAgent"""
    print("="*60)
    print("🎓 KnowledgeAgent测试")
    print("="*60)
    
    # 创建记忆管理器
    memory = MemoryManager(enable_v1=False)  # 使用简化模式测试
    
    # 创建KnowledgeAgent
    agent = KnowledgeAgent(memory)
    
    # 记住一些测试数据
    print("\n1️⃣ 记住测试数据")
    await memory.remember(
        key="project_v2",
        content="V2 MVP系统已完成，包括Worker Pool、Gateway流式对话、exec自主工具",
        metadata={"type": "project", "status": "completed"}
    )
    
    await memory.remember(
        key="goal_jarvais",
        content="终极目标是成为超越钢铁侠JARVIS的全能AI",
        metadata={"type": "goal"}
    )
    
    # 查询测试
    print("\n2️⃣ 知识查询测试")
    result = await agent.query("我们的项目进展如何？")
    print(f"\n问题: 我们的项目进展如何？")
    print(f"答案:\n{result['answer']}")
    print(f"\n置信度: {result['confidence']:.2%}")
    print(f"来源: {result['sources']}")
    
    # 学习测试
    print("\n\n3️⃣ 持续学习测试")
    learn_result = await agent.learn("如何优化AI系统的响应速度")
    print(f"学习状态: {learn_result['status']}")
    print(f"学习结果: {learn_result['message']}")
    
    # 上下文总结
    print("\n\n4️⃣ 上下文总结测试")
    summary = await agent.summarize_context()
    print(f"当前阶段: {summary.get('state', {}).get('phase', 'N/A')}")
    print(f"已完成项目: {len(summary.get('completed_projects', []))}个")
    print(f"下一步: {summary.get('next_tasks', {}).get('short_term', {}).get('title', 'N/A')}")
    
    # 统计
    print("\n\n5️⃣ 统计信息")
    stats = await agent.get_stats()
    print(f"Agent类型: {stats['type']}")
    print(f"上下文文件: {stats['context_files']}")
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
