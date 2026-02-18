"""任务分类器 - 根据任务特征自动选择最优模型"""
import re
from typing import Literal, Optional
from enum import Enum


class TaskType(Enum):
    """任务类型枚举"""
    REALTIME = "realtime"      # 实时交互
    BULK = "bulk"              # 大批量任务
    COMPLEX = "complex"        # 复杂推理
    SIMPLE = "simple"          # 简单任务
    EMBEDDING = "embedding"    # 向量嵌入


class TaskClassifier:
    """
    任务分类器

    根据任务特征自动选择最优模型：
    - 实时交互 → 智谱（最快1.03秒）
    - 大批量任务 → 混元（无RPM限制）
    - 复杂推理 → NVIDIA（思考模式）
    - 简单任务 → 负载均衡
    - Embeddings → SiliconFlow
    """

    def __init__(self):
        # 模型优先级配置
        self.model_preferences = {
            TaskType.REALTIME: ["zhipu", "hunyuan", "nvidia2", "nvidia1"],
            TaskType.BULK: ["hunyuan", "nvidia2", "nvidia1"],
            TaskType.COMPLEX: ["nvidia1", "nvidia2", "hunyuan"],
            TaskType.SIMPLE: ["hunyuan", "nvidia1", "nvidia2", "zhipu"],
            TaskType.EMBEDDING: ["siliconflow"],
        }

        # 任务类型关键字检测
        self.task_keywords = {
            TaskType.REALTIME: [
                "现在", "立即", "快速", "快点", "马上", "等一下",
                "实时", "即时", "秒回", "立刻"
            ],
            TaskType.BULK: [
                "批量", "多个", "很多", "大量", "列表", "所有",
                "全部", "每个", "逐一", "依次"
            ],
            TaskType.COMPLEX: [
                "分析", "推理", "推导", "总结", "评估", "对比",
                "深刻", "详细", "深度", "思考", "逻辑"
            ],
            TaskType.SIMPLE: [
                "你好", "再见", "感谢", "OK", "好的", "知道",
                "简单", "快速", "简短"
            ],
        }

        # 上下文大小需求检测
        self.context_keywords_large = [
            "长文本", "长篇", "文章", "报告", "论文", "书籍",
            "整个", "全部", "完整", "所有内容"
        ]

        print("="*60)
        print("任务分类器初始化 [OK]")
        print("="*60)

    def count_tokens_heuristic(self, text: str) -> int:
        """
        简单Token估算（中文: 1字符≈1token，英文: 4字符≈1token）
        """
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        other_chars = len(text) - chinese_chars
        tokens = chinese_chars + int(other_chars / 4)
        return tokens

    def analyze_task(self, prompt: str) -> dict:
        """
        分析任务特征

        Returns:
            {
                "task_type": TaskType,
                "context_size": "small" | "medium" | "large",
                "urgency": "high" | "medium" | "low",
                "needs_thinking": bool,
                "estimated_tokens": int
            }
        """
        result = {}

        # 1. 估算Token数量
        tokens = self.count_tokens_heuristic(prompt)
        result['estimated_tokens'] = tokens

        # 2. 判断上下文大小
        if tokens < 1000:
            result['context_size'] = "small"
        elif tokens < 50000:
            result['context_size'] = "medium"
        else:
            result['context_size'] = "large"

        # 3. 判断是否需要思考模式
        result['needs_thinking'] = any(
            keyword in prompt for keyword in self.task_keywords[TaskType.COMPLEX]
        )

        # 4. 判断紧急程度
        if any(keyword in prompt for keyword in self.task_keywords[TaskType.REALTIME]):
            result['urgency'] = "high"
        elif any(keyword in prompt for keyword in self.task_keywords[TaskType.SIMPLE]):
            result['urgency'] = "medium"
        else:
            result['urgency'] = "low"

        # 5. 判别任务类型
        task_type = self._classify_task_type(prompt, result)
        result['task_type'] = task_type

        return result

    def _classify_task_type(self, prompt: str, analysis: dict) -> TaskType:
        """分类任务类型"""
        # 检查是否是Embeddings请求
        if "嵌入" in prompt or "向量" in prompt or "embedding" in prompt.lower():
            return TaskType.EMBEDDING

        # 优先检查实时交互
        if any(k in prompt for k in self.task_keywords[TaskType.REALTIME]):
            return TaskType.REALTIME

        # 检查大批量任务
        if any(k in prompt for k in self.task_keywords[TaskType.BULK]):
            return TaskType.BULK

        # 检查复杂推理
        if any(k in prompt for k in self.task_keywords[TaskType.COMPLEX]):
            return TaskType.COMPLEX

        # 默认为简单任务
        return TaskType.SIMPLE

    def recommend_model(self, prompt: str, preferred_models: Optional[list] = None) -> list:
        """
        推荐模型列表（按优先级）

        Args:
            prompt: 用户提示词
            preferred_models: 用户优先级（可选）

        Returns:
            推荐的模型列表
        """
        # 分析任务
        analysis = self.analyze_task(prompt)
        task_type = analysis['task_type']
        context_size = analysis['context_size']
        needs_thinking = analysis['needs_thinking']
        urgency = analysis['urgency']

        print(f"\n[TaskClassifier] 任务分析:")
        print(f"  类型: {task_type.value}")
        print(f"  上下文: {context_size} ({analysis['estimated_tokens']} tokens)")
        print(f"  紧急度: {urgency}")
        print(f"  需要思考: {needs_thinking}")

        # 基础优先级
        base_models = self.model_preferences[task_type].copy()

        # 特殊规则：思考模式必须选NVIDIA
        if needs_thinking and task_type == TaskType.COMPLEX:
            base_models = ["nvidia1", "nvidia2", "hunyuan"]

        # 特殊规则：超大上下文（>200K）必须选混元
        if context_size == "large" and analysis['estimated_tokens'] > 200000:
            base_models = ["hunyuan"]

        # 特殊规则：实时任务必须选智谱（最快）
        if urgency == "high" and task_type == TaskType.REALTIME:
            base_models = ["zhipu", "hunyuan", "nvidia2", "nvidia1"]

        # 用户优先级覆盖
        if preferred_models:
            # 将用户指定的模型移到列表前面
            user_models = [m for m in preferred_models if m in base_models]
            other_models = [m for m in base_models if m not in preferred_models]
            base_models = user_models + other_models

        print(f"  推荐模型: {' → '.join(base_models)}")

        return base_models


# 全局实例
classifier_instance = None

def get_task_classifier():
    """获取任务分类器实例"""
    global classifier_instance
    if classifier_instance is None:
        classifier_instance = TaskClassifier()
    return classifier_instance


if __name__ == "__main__":
    # 测试
    classifier = TaskClassifier()

    test_cases = [
        "你好",
        "现在马上翻译这100篇文章",
        "深入分析人工智能对社会的影响",
        "生成这句话的向量嵌入",
        "快速告诉我今天天气",
    ]

    for prompt in test_cases:
        print(f"\n{'='*60}")
        print(f"测试: {prompt}")
        print(f"{'='*60}")
        models = classifier.recommend_model(prompt)
