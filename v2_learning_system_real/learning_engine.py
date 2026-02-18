"""
V2 Learning System - Learning Engine
Real LLM integration with fallback mechanisms
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid

from .llm import LLMProvider, OpenAIProvider, APIError


@dataclass
class LearningTask:
    """Represents a single learning task"""
    id: str
    topic: str
    worker_id: str
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    result: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed
    error: Optional[str] = None
    api_calls: int = 0
    duration: float = 0.0


class LearningEngine:
    """
    Core learning engine that manages parallel learning workers
    """
    
    def __init__(self, num_workers: int = 3, model: str = None):
        self.num_workers = num_workers
        self.model = model
        self.llm_provider: Optional[LLMProvider] = None
        self.tasks: Dict[str, LearningTask] = {}
        self.running = False
    
    async def submit_learning_task(self, topic: str, worker_id: str) -> LearningTask:
        """Submit a learning task"""
        task = LearningTask(str(uuid.uuid4()), topic, worker_id)
        self.tasks[task.id] = task
        return task
    
    async def execute_task(self, task: LearningTask, perspective: str = "technical", style: str = "detailed") -> str:
        """Execute a learning task with real LLM"""
        task.status = "running"
        start_time = time.time()
        
        try:
            if not self.llm_provider:
                self.llm_provider = OpenAIProvider(model=self.model)
            
            result = await self.llm_provider.learning_with_fallback(
                topic=task.topic,
                perspective=perspective,
                style=style
            )
            
            task.result = result
            task.status = "completed"
            task.api_calls = 1
            
        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            result = f"[Failed] {str(e)}"
        
        task.completed_at = time.time()
        task.duration = task.completed_at - start_time
        return result
    
    async def parallel_learning(self, topic: str, num_perspectives: int = 3, save_to_kb: bool = True) -> List[Dict[str, Any]]:
        """
        Execute parallel learning with multiple perspectives
        
        Args:
            topic: Learning topic
            num_perspectives: Number of perspectives to explore
            save_to_kb: Whether to save results to Knowledge Base (default: True)
        
        Returns:
            List of learning results
        """
        perspectives = [
            "technical",
            "practical",
            "theoretical",
            "historical",
            "comparative"
        ][:num_perspectives]
        
        tasks = []
        for i, perspective in enumerate(perspectives):
            task = await self.submit_learning_task(topic, f"worker_{i}")
            tasks.append(self.execute_task(task, perspective=perspective))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        learning_data = []
        for i, (perspective, result) in enumerate(zip(perspectives, results)):
            learning_data.append({
                "perspective": perspective,
                "result": result if isinstance(result, str) else str(result),
                "worker_id": f"worker_{i}",
                "timestamp": datetime.now().isoformat()
            })
        
        # Auto-save to Knowledge Base if enabled
        if save_to_kb:
            try:
                from .knowledge_base_integration import KnowledgeBaseIntegration
                kb = KnowledgeBaseIntegration()
                save_result = await kb.save_learning_result(topic, learning_data)
                
                if save_result["success"]:
                    print(f"\n💾 {save_result['message']}")
                else:
                    print(f"\n⚠️ 保存到知识库失败：{save_result.get('error', '未知错误')}")
            except Exception as e:
                print(f"\n⚠️ 知识库集成未启用或出错：{e}")
        
        return learning_data
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        task = self.tasks.get(task_id)
        if task:
            return asdict(task)
        return None
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks"""
        return [asdict(task) for task in self.tasks.values()]


async def main():
    """Test the learning engine"""
    print("=" * 80)
    print("🧪 V2 Learning Engine Test")
    print("=" * 80)
    
    engine = LearningEngine(num_workers=3)
    
    print("\n📚 Testing parallel learning...")
    topic = "What is Python programming language?"
    
    results = await engine.parallel_learning(topic, num_perspectives=2)
    
    print(f"\n✅ Learning completed!")
    print(f"📊 Results: {len(results)} perspectives")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Perspective: {result['perspective']}")
        content = result['result'][:150] + "..." if len(result['result']) > 150 else result['result']
        print(f"   {content}")
    
    print("\n" + "=" * 80)
    print("✅ Test completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
