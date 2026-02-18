"""负载均衡器 - 结合RateLimiter和TaskClassifier"""
from typing import Optional, Dict, Any
from .multi_model_limiter import MultiModelRateLimiter, get_rate_limiter
from .task_classifier import TaskClassifier, get_task_classifier
import json
import requests


class LoadBalancer:
    """
    多模型负载均衡器

    整合：
    - TaskClassifier: 根据任务特征选择最优模型
    - MultiModelRateLimiter: 检查并发和RPM限制
    """

    def __init__(self):
        # 初始化组件
        self.limiter = get_rate_limiter()
        self.classifier = get_task_classifier()

        # API配置
        self.api_configs = self._load_api_configs()

        # 统计信息
        self.request_stats = {
            "total": 0,
            "by_model": {
                "zhipu": 0,
                "hunyuan": 0,
                "nvidia1": 0,
                "nvidia2": 0,
                "siliconflow": 0
            },
            "failures": 0
        }

        print("="*60)
        print("负载均衡器初始化 [OK]")
        print("="*60)

    def _load_api_configs(self) -> Dict:
        """加载API配置"""
        config_path = r'C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\API_CONFIG_FINAL.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)['api_configs']

    def call_api(self, prompt: str, preferred_models: Optional[list] = None) -> Dict[str, Any]:
        """
        智能调用API（自动选择最优模型）

        Args:
            prompt: 用户提示词
            preferred_models: 用户优先级（可选）

        Returns:
            {
                "success": bool,
                "content": str,
                "model": str,
                "latency": float,
                "usage": dict
            }
        """
        # 1. 任务分类
        models_to_try = self.classifier.recommend_model(prompt, preferred_models)

        # 2. 依次尝试模型
        for model_name in models_to_try:
            print(f"\n[LoadBalancer] 尝试模型: {model_name}")

            # 检查并发和RPM限制
            if not self.limiter.acquire_concurrency(model_name):
                print(f"  ➜ 并发限制，跳过 {model_name}")
                continue

            if not self.limiter.check_rpm_limit(model_name):
                self.limiter.release_concurrency(model_name)
                print(f"  ➜ RPM限制，跳过 {model_name}")
                continue

            # 3. 调用API
            result = self._call_single_model(model_name, prompt)

            if result['success']:
                # 统计
                self.request_stats["total"] += 1
                self.request_stats["by_model"][model_name] += 1

                print(f"  ✅ {model_name} 调用成功！")
                return result
            else:
                self.limiter.release_concurrency(model_name)
                self.request_stats["failures"] += 1
                print(f"  ❌ {model_name} 调用失败: {result.get('error')}")

        # 所有模型都失败
        self.limiter.release_concurrency(models_to_try[0])  # 清理
        self.request_stats["failures"] += 1

        return {
            "success": False,
            "content": None,
            "model": None,
            "latency": 0,
            "error": "所有模型都不可用"
        }

    def _call_single_model(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """调用单个模型API"""
        import time

        config = self.api_configs[model_name]

        # Embeddings API（特殊处理）
        if model_name == "siliconflow":
            return self._call_embedding_api(config, prompt)

        # Chat API
        return self._call_chat_api(config, prompt)

    def _call_chat_api(self, config: Dict, prompt: str) -> Dict[str, Any]:
        """调用聊天API"""
        import time

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": config['model'],
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 1024
        }

        # 模型特定参数
        if config['provider'] == 'nvidia' and config.get('enable_thinking'):
            payload['extra_body'] = {
                "chat_template_kwargs": {
                    "enable_thinking": True,
                    "clear_thinking": False
                }
            }
        elif config['provider'] == 'zhipu' and config.get('enable_thinking'):
            payload['thinking'] = {"type": "enabled"}

        try:
            start_time = time.time()

            response = requests.post(
                config['url'],
                headers=headers,
                json=payload,
                timeout=30
            )

            latency = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                usage = data.get('usage', {})

                return {
                    "success": True,
                    "content": content,
                    "model": config['model'],
                    "latency": latency,
                    "usage": usage
                }
            else:
                return {
                    "success": False,
                    "content": None,
                    "model": None,
                    "latency": latency,
                    "error": f"HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "content": None,
                "model": None,
                "latency": 0,
                "error": str(e)
            }

    def _call_embedding_api(self, config: Dict, text: str) -> Dict[str, Any]:
        """调用Embedding API"""
        import time

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": config['model'],
            "input": text,
            "encoding_format": "float"
        }

        try:
            start_time = time.time()

            response = requests.post(
                config['url'],
                headers=headers,
                json=payload,
                timeout=30
            )

            latency = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                embedding = data['data'][0]['embedding']

                return {
                    "success": True,
                    "content": embedding,
                    "model": config['model'],
                    "latency": latency,
                    "usage": {
                        "dimensions": len(embedding)
                    }
                }
            else:
                return {
                    "success": False,
                    "content": None,
                    "model": None,
                    "latency": latency,
                    "error": f"HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "content": None,
                "model": None,
                "latency": 0,
                "error": str(e)
            }

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "requests": self.request_stats,
            "limiter_status": self.limiter.get_status()
        }


# 全局实例
load_balancer_instance = None

def get_load_balancer():
    """获取负载均衡器实例"""
    global load_balancer_instance
    if load_balancer_instance is None:
        load_balancer_instance = LoadBalancer()
    return load_balancer_instance


if __name__ == "__main__":
    # 测试
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    balancer = LoadBalancer()

    test_prompts = [
        "你好",
        "分析人工智能发展趋势",
        "翻译这100篇文章",
    ]

    for prompt in test_prompts:
        print(f"\n{'='*60}")
        print(f"测试: {prompt}")
        print(f"{'='*60}")
        result = balancer.call_api(prompt)
        print(f"\n结果:")
        print(f"  成功: {result['success']}")
        print(f"  模型: {result['model']}")
        print(f"  耗时: {result.get('latency', 0):.2f}秒")
        if result['success']:
            print(f"  内容: {result['content'][:100]}...")

    # 统计
    print(f"\n{'='*60}")
    print("统计信息:")
    print(json.dumps(balancer.get_stats(), indent=2, ensure_ascii=False))
