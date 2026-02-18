"""
Learning Integration - V2学习系统集成
"""

import sys
import asyncio
import logging
from typing import Dict, Any
from pathlib import Path

# 添加V2学习系统路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'v2_learning_system_real'))

# 提前导入Step类（避免相对导入问题）
from workflow.engine import Step

try:
    from learning_engine import LearningEngine
    from llm import LLMProvider, OpenAIProvider
    V2_LEARNING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"V2 Learning System not available: {e}")
    V2_LEARNING_AVAILABLE = False

logger = logging.getLogger(__name__)


class LearningIntegration:
    """
    V2学习系统集成
    将V2学习系统封装为工作流步骤
    """

    def __init__(self, use_mock: bool = False):
        """
        初始化V2学习系统集成

        Args:
            use_mock: 是否使用模拟结果（当V2学习系统不可用时）
        """
        self.use_mock = use_mock
        self.learning_engine = None

        if not use_mock and V2_LEARNING_AVAILABLE:
            try:
                # 配置NVIDIA GLM4.7 API
                from dotenv import load_dotenv
                load_dotenv(Path(__file__).parent.parent.parent.parent / 'v2_learning_system_real' / '.env')

                api_key = None
                base_url = None

                # 尝试从环境变量读取
                import os
                api_key = os.getenv('NVIDIA_API_KEY') or os.getenv('NVAPI_KEY')
                base_url = "https://integrate.api.nvidia.com/v1/chat/completions"

                if api_key:
                    self.llm_provider = OpenAIProvider(
                        model="nvidia/llama-3.1-nemotron-70b-instruct",
                        api_key=api_key,
                        base_url=base_url
                    )
                    self.learning_engine = LearningEngine(llm_provider=self.llm_provider)
                    logger.info("V2 Learning System initialized successfully")
                else:
                    logger.warning("NVIDIA API key not found, using mock")
                    self.learning_engine = None
                    self.use_mock = True
            except Exception as e:
                logger.warning(f"Failed to initialize V2 Learning System: {e}")
                self.learning_engine = None
                self.use_mock = True
        else:
            logger.info("Using mock learning integration")
            self.use_mock = True

    async def learn(self, topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行学习

        Args:
            topic: 学习主题
            context: 执行上下文

        Returns:
            学习结果
        """
        if self.use_mock or self.learning_engine is None:
            return await self._learn_mock(topic, context)

        logger.info(f"Learning topic: {topic}")

        try:
            # 创建学习任务（使用worker-1进行学习）
            task = await self.learning_engine.submit_learning_task(topic, "worker-1")

            # 执行学习
            result_task = await self.learning_engine.execute_learning(task)

            # 返回学习结果
            return {
                'status': 'success',
                'topic': topic,
                'lessons': result_task.lessons,
                'key_points': result_task.key_points,
                'recommendations': result_task.recommendations,
                'duration': result_task.end_time - result_task.start_time if result_task.end_time else 0,
                'worker_id': result_task.worker_id
            }
        except Exception as e:
            logger.error(f"Learning failed: {e}")
            # 失败时回退到模拟
            return await self._learn_mock(topic, context)

    async def _learn_mock(self, topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟学习（当V2学习系统不可用时）

        Args:
            topic: 学习主题
            context: 执行上下文

        Returns:
            模拟学习结果
        """
        logger.warning(f"Using mock learning for: {topic}")

        # 模拟学习延迟
        await asyncio.sleep(1.0)

        # 返回模拟结果
        return {
            'status': 'success',
            'topic': topic,
            'mock': True,
            'lessons': [
                f"Mock lesson 1 for {topic}",
                f"Mock lesson 2 for {topic}"
            ],
            'key_points': [
                f"Mock key point 1 for {topic}",
                f"Mock key point 2 for {topic}"
            ],
            'recommendations': [
                "Mock recommendation 1",
                "Mock recommendation 2"
            ],
            'duration': 1.0,
            'worker_id': 'worker-1-mock'
        }

    def create_learning_step(self, topic: str, timeout: int = 300):
        """
        创建学习步骤

        Args:
            topic: 学习主题
            timeout: 超时时间（秒）

        Returns:
            Step: 工作流步骤
        """
        def learning_function(context: Dict[str, Any]):
            return self.learn(topic, context)

        return Step(
            name=f"learning_{topic.replace(' ', '_')}",
            function=learning_function,
            enabled=True,
            timeout=timeout,
            metadata={
                'type': 'learning',
                'topic': topic
            }
        )
