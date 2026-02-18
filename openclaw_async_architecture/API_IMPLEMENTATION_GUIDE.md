# OpenClaw API配置与实现说明书

**版本：** v1.0
**更新时间：** 2026-02-16
**适用范围：** OpenClaw V2 异步架构，多模型调用

---

## 📚 **目录**

1. [概述](#概述)
2. [API配置汇总](#api配置汇总)
3. [API详细配置](#api详细配置)
4. [调用示例](#调用示例)
5. [最佳实践](#最佳实践)
6. [错误处理](#错误处理)
7. [性能优化](#性能优化)
8. [负载均衡策略](#负载均衡策略)
9. [监控与告警](#监控与告警)

---

## 📋 **概述**

### 项目背景
OpenClaw V2 异步架构项目需要使用多个大模型API，实现智能负载均衡和故障降级。本项目整合了5个免费的API服务，通过统一接口提供稳定的AI能力。

### 核心目标
- ✅ 高可用性：16并发能力，永不崩溃
- ✅ 高性能：最快1.03秒响应，智能路由
- ✅ 零成本：所有API都是免费的
- ✅ 智能路由：根据任务类型自动选择最优模型
- ✅ 容错降级：3层容错机制，自动切换

### 支持的模型
| 模型 | 速度 | 上下文 | 并发 | RPM限制 | 适用场景 |
|------|------|--------|------|---------|---------|
| 智谱 | 🥇 1.03秒 | 200K | 1 | ? | 最快响应 |
| 混元 | 🥈 1.20秒 | 256K | 5 | 无 ⚡ | 大批量任务 |
| 英伟达2 | 🥉 2.68秒 | 128K | 5 | 40/分 | 平衡型 |
| 英伟达1 | 7.17秒 | 128K | 5 | 40/分 | 复杂推理 |
| SiliconFlow | 0.10秒 | - | - | 5 RPM | Embeddings |

---

## 🔧 **API配置汇总**

### 配置文件位置
- JSON配置：`API_CONFIG_FINAL.json`
- 完整报告：`API_SPEED_TEST_COMPLETE_REPORT.md`
- 测试脚本：`api_quick_test.py`、`test_zhipu.py`

### 快速配置加载

```python
import json

# 加载API配置
with open('API_CONFIG_FINAL.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

api_configs = config['api_configs']

# 访问配置
zhipu_config = api_configs['zhipu']
hunyuan_config = api_configs['hunyuan']
nvidia1_config = api_configs['nvidia1']
nvidia2_config = api_configs['nvidia2']
siliconflow_config = api_configs['siliconflow']
```

---

## 📝 **API详细配置**

### 1. 智谱 glm4.7-flash

**基本信息：**
```
Provider: 智谱
URL: https://open.bigmodel.cn/api/paas/v4/chat/completions
API KEY: c744282c23b74fa9bf7a2be68a8656b7.w4rIakRo0j4tWqpO
模型: glm-4-flash
```

**性能指标：**
- 平均延迟：1.03秒（最快）⭐
- 上下文窗口：200,000 tokens
- RPM限制：官方未明确
- 并发限制：1 ⚠️（关键限制）
- 支持思考模式：✅

**适用场景：**
- ✅ 实时交互（最快响应）
- ✅ 中小上下文任务（≤200K）
- ✅ 单任务或低并发场景
- ⚠️ 不适合高并发任务

**调用示例：**
```python
import requests

def call_zhipu_api(prompt):
    headers = {
        "Authorization": "Bearer c744282c23b74fa9bf7a2be68a8656b7.w4rIakRo0j4tWqpO",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "thinking": {"type": "enabled"},  # 启用思考模式
        "max_tokens": 1024,
        "temperature": 0.7
    }

    response = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )

    result = response.json()
    content = result['choices'][0]['message']['content']
    thinking = result['choices'][0]['message'].get('thinking_content', '')

    return content, thinking
```

**注意事项：**
⚠️ **重要：** 并发限制只有1，必须使用队列机制管理请求，避免并发超限。

---

### 2. 混元 hunyuan-lite

**基本信息：**
```
Provider: 腾讯混元
URL: https://api.hunyuan.cloud.tencent.com/v1/chat/completions
API KEY: sk-7xGaNZwkW0CLZNeT8kZrJv2hiHpU47wzS8XVhOagKKjLyb2i
模型: hunyuan-lite
```

**性能指标：**
- 平均延迟：1.20秒
- 上下文窗口：262,144 tokens（最大）⭐
- RPM限制：**无限制** ⚡（杀手级特性）
- 并发限制：5（主子账号共享）
- 支持思考模式：❌

**适用场景：**
- ✅ 大批量任务（无RPM限制）⭐
- ✅ 高并发场景（并发5）
- ✅ 超大上下文（>200K）
- ✅ 主要工作马（推荐50%分配）

**调用示例：**
```python
import requests

def call_hunyuan_api(prompt):
    headers = {
        "Authorization": "Bearer sk-7xGaNZwkW0CLZNeT8kZrJv2hiHpU47wzS8XVhOagKKjLyb2i",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "hunyuan-lite",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.7,
        "extra_body": {
            "enable_enhancement": True
        }
    }

    response = requests.post(
        "https://api.hunyuan.cloud.tencent.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )

    result = response.json()
    content = result['choices'][0]['message']['content']

    return content
```

**注意事项：**
✅ **推荐：** 无RPM限制，适合作为主要模型使用。

---

### 3. 英伟达1 (主账户) - z-ai/glm4.7

**基本信息：**
```
Provider: NVIDIA (cherry-nvidia)
URL: https://integrate.api.nvidia.com/v1/chat/completions
API KEY: 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
模型: z-ai/glm4.7
```

**性能指标：**
- 平均延迟：7.17秒（最慢，但质量高）
- 上下文窗口：128,000 tokens
- RPM限制：40/分钟
- 并发限制：5
- 支持思考模式：✅（深度思考）

**适用场景：**
- ✅ 复杂推理任务
- ✅ 需要深度思考的任务
- ✅ 长文本创作

**调用示例：**
```python
import requests

def call_nvidia1_api(prompt):
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "z-ai/glm4.7",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 1000,
        "extra_body": {
            "chat_template_kwargs": {
                "enable_thinking": True,
                "clear_thinking": False
            }
        }
    }

    response = requests.post(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )

    result = response.json()
    content = result['choices'][0]['message']['content']

    # 提取思考内容
    if hasattr(result['choices'][0]['message'], 'reasoning_content'):
        thinking = result['choices'][0]['message'].reasoning_content
    else:
        thinking = ""

    return content, thinking
```

**注意事项：**
⚠️ **注意：** RPM限制40/分钟，需要Token Bucket算法控制。

---

### 4. 英伟达2 (备用) - z-ai/glm4.7

**基本信息：**
```
Provider: NVIDIA (cherry-nvidia)
URL: https://integrate.api.nvidia.com/v1/chat/completions
API KEY: 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
模型: z-ai/glm4.7
```

**性能指标：**
- 平均延迟：2.68秒（比英伟达1快2.7倍）
- 上下文窗口：128,000 tokens
- RPM限制：40/分钟
- 并发限制：5
- 支持思考模式：✅

**适用场景：**
- ✅ 速度与质量平衡
- ✅ 英伟达1备用
- ✅ 标准任务

**调用示例：**
```python
import requests

def call_nvidia2_api(prompt):
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "z-ai/glm4.7",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 1000,
        "extra_body": {
            "chat_template_kwargs": {
                "enable_thinking": True,
                "clear_thinking": False
            }
        }
    }

    response = requests.post(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )

    result = response.json()
    content = result['choices'][0]['message']['content']

    return content
```

**注意事项：**
✅ **推荐：** 英伟达2比英伟达1稳定，建议优先使用英伟达2。

---

### 5. SiliconFlow (Embeddings)

**基本信息：**
```
Provider: SiliconFlow
URL: https://api.siliconflow.cn/v1/embeddings
API KEY: sk-kvqpfofevcxloxexrrjovsjzpnwsvhpwrbxkwjydwbjyufjf
模型: BAAI/bge-large-zh-v1.5
```

**性能指标：**
- 平均延迟：0.10秒（超快）
- 向量维度：1024
- RPM限制：5
- 每日限制：50万 tokens

**适用场景：**
- ✅ 记忆搜索系统
- ✅ 语义检索
- ✅ 向量存储

**调用示例：**
```python
import requests

def get_embedding(text):
    headers = {
        "Authorization": "Bearer sk-kvqpfofevcxloxexrrjovsjzpnwsvhpwrbxkwjydwbjyufjf",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "BAAI/bge-large-zh-v1.5",
        "input": text,
        "encoding_format": "float"
    }

    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers=headers,
        json=payload,
        timeout=30
    )

    result = response.json()
    embedding = result['data'][0]['embedding']

    return embedding  # [1024维向量]
```

**注意事项：**
⚠️ **注意：** RPM限制5，Embeddings调用应该缓存结果避免重复计算。

---

## 💻 **调用示例**

### 统一接口封装

```python
import requests
import json
import time
from typing import Optional, Tuple

class MultiModelAPI:
    """多模型API统一接口"""

    def __init__(self, config_path='API_CONFIG_FINAL.json'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.api_configs = self.config['api_configs']

    def call_api(self, model_name: str, prompt: str, **kwargs) -> Tuple[str, dict]:
        """
        调用指定API

        Args:
            model_name: 模型名称 (zhipu/hunyuan/nvidia1/nvidia2/siliconflow)
            prompt: 用户提示词
            **kwargs: 其他参数

        Returns:
            (response_content, usage_info)
        """
        config = self.api_configs[model_name]

        if config.get('type') == 'embeddings':
            return self._call_embedding_api(config, prompt, **kwargs)
        else:
            return self._call_chat_api(config, prompt, **kwargs)

    def _call_chat_api(self, config: dict, prompt: str, **kwargs) -> Tuple[str, dict]:
        """调用聊天API"""
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": config['model'],
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 1024)
        }

        # 特殊参数处理
        if config['provider'] == 'nvidia' and config.get('enable_thinking'):
            payload['extra_body'] = {
                "chat_template_kwargs": {
                    "enable_thinking": True,
                    "clear_thinking": False
                }
            }
        elif config['provider'] == 'zhipu' and config.get('enable_thinking'):
            payload['thinking'] = {"type": "enabled"}
        elif config['provider'] == 'tencent':
            payload['extra_body'] = {
                "enable_enhancement": True
            }

        start_time = time.time()

        response = requests.post(
            config['url'],
            headers=headers,
            json=payload,
            timeout=kwargs.get('timeout', 60)
        )

        end_time = time.time()
        latency = end_time - start_time

        result = response.json()
        content = result['choices'][0]['message']['content']

        usage = {
            "latency": latency,
            "total_tokens": result.get('usage', {}).get('total_tokens', 0),
            "prompt_tokens": result.get('usage', {}).get('prompt_tokens', 0),
            "completion_tokens": result.get('usage', {}).get('completion_tokens', 0)
        }

        return content, usage

    def _call_embedding_api(self, config: dict, text: str, **kwargs) -> Tuple[list, dict]:
        """调用Embedding API"""
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": config['model'],
            "input": text,
            "encoding_format": "float"
        }

        start_time = time.time()

        response = requests.post(
            config['url'],
            headers=headers,
            json=payload,
            timeout=kwargs.get('timeout', 30)
        )

        end_time = time.time()
        latency = end_time - start_time

        result = response.json()
        embedding = result['data'][0]['embedding']

        usage = {
            "latency": latency,
            "dimensions": len(embedding)
        }

        return embedding, usage


# 使用示例
if __name__ == "__main__":
    api = MultiModelAPI()

    # 调用智谱
    content, usage = api.call_api("zhipu", "你好")
    print(f"智谱响应: {content}")
    print(f"耗时: {usage['latency']:.2f}秒")

    # 调用混元
    content, usage = api.call_api("hunyuan", "你好")
    print(f"混元响应: {content}")
    print(f"耗时: {usage['latency']:.2f}秒")
```

---

## 🎯 **最佳实践**

### 1. 智能路由策略

```python
def route_task(task_type: str, prompt_length: int, need_thinking: bool) -> str:
    """
    智能路由：根据任务类型选择最优模型

    Args:
        task_type: 任务类型 (simple/complex/bulk/realtime)
        prompt_length: 提示词长度
        need_thinking: 是否需要思考模式

    Returns:
        模型名称
    """
    # 实时交互 → 智谱（最快）
    if task_type == "realtime":
        return "zhipu"

    # 大批量任务 → 混元（无RPM限制）
    elif task_type == "bulk":
        return "hunyuan"

    # 复杂推理 → 英伟达1（思考模式最深）
    elif need_thinking:
        return "nvidia1"

    # 超大上下文（>200k）→ 混元（256k）
    elif prompt_length > 200000:
        return "hunyuan"

    # 大上下文（128k-200k）→ 智谱（200k）
    elif prompt_length > 128000:
        return "zhipu"

    # 默认 → 负载均衡
    else:
        import random
        return weighted_random({
            "hunyuan": 0.50,    # 50%
            "nvidia1": 0.20,   # 20%
            "nvidia2": 0.20,   # 20%
            "zhipu": 0.10      # 10%
        })
```

### 2. 并发控制

```python
import asyncio
from asyncio import Semaphore

class ConcurrencyController:
    """并发控制器"""

    def __init__(self):
        # 并发限制
        self.semaphores = {
            "zhipu": Semaphore(1),      # 智谱：只有1并发
            "hunyuan": Semaphore(5),    # 混元：5并发
            "nvidia1": Semaphore(5),    # 英伟达1：5并发
            "nvidia2": Semaphore(5)     # 英伟达2：5并发
        }

    async def call_with_limit(self, model_name: str, api: MultiModelAPI, prompt: str):
        """带并发限制的调用"""
        semaphore = self.semaphores[model_name]

        async with semaphore:
            # 调用API
            content, usage = await asyncio.to_thread(api.call_api, model_name, prompt)
            return content, usage


# 使用示例
async def concurrent_tasks():
    api = MultiModelAPI()
    controller = ConcurrencyController()

    tasks = [
        controller.call_with_limit("zhipu", api, prompt)
        for prompt in ["你好"] * 10
    ]

    results = await asyncio.gather(*tasks)
    return results
```

### 3. 缓存策略

```python
import hashlib
import json
from typing import Optional

class ResponseCache:
    """响应缓存"""

    def __init__(self, redis_client=None):
        self.cache = {} if redis_client is None else redis_client
        self.ttl = 3600  # 1小时

    def _get_cache_key(self, model: str, prompt: str):
        """生成缓存键"""
        key = f"{model}:{hashlib.md5(prompt.encode()).hexdigest()}"
        return key

    def get(self, model: str, prompt: str) -> Optional[str]:
        """获取缓存"""
        key = self._get_cache_key(model, prompt)

        if isinstance(self.cache, dict):
            return self.cache.get(key)
        else:
            # Redis
            value = self.cache.get(key)
            return json.loads(value) if value else None

    def set(self, model: str, prompt: str, response: str):
        """设置缓存"""
        key = self._get_cache_key(model, prompt)

        if isinstance(self.cache, dict):
            self.cache[key] = response
        else:
            # Redis
            self.cache.setex(key, self.ttl, json.dumps(response))


# 使用示例
def call_with_cache(api: MultiModelAPI, cache: ResponseCache, model: str, prompt: str):
    """带缓存的调用"""
    # 先查缓存
    cached = cache.get(model, prompt)
    if cached:
        return cached

    # 调用API
    content, _ = api.call_api(model, prompt)

    # 写入缓存
    cache.set(model, prompt, content)

    return content
```

---

## ⚠️ **错误处理**

### 1. 统一错误处理

```python
import requests
from typing import Tuple

class APIError(Exception):
    """API错误基类"""
    pass

class RateLimitError(APIError):
    """速率限制错误"""
    pass

class TimeoutError(APIError):
    """超时错误"""
    pass

class AuthenticationError(APIError):
    """认证错误"""
    pass


def call_with_retry(
    api: MultiModelAPI,
    model: str,
    prompt: str,
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> Tuple[str, dict]:
    """
    带重试的API调用

    Args:
        api: API实例
        model: 模型名称
        prompt: 提示词
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）

    Returns:
        (response_content, usage_info)

    Raises:
        APIError: 所有重试失败后抛出
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            content, usage = api.call_api(model, prompt)
            return content, usage

        except requests.exceptions.Timeout as e:
            last_error = TimeoutError(f"API调用超时: {e}")

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code

            if status_code == 429:
                # 速率限制
                wait_time = retry_delay * (2 ** attempt)
                last_error = RateLimitError(f"触发速率限制，等待{wait_time}秒后重试")
                time.sleep(wait_time)
                continue

            elif status_code == 401:
                # 认证失败
                raise AuthenticationError(f"API认证失败: {e.response.text}")

            else:
                # 其他HTTP错误
                last_error = APIError(f"HTTP错误 {status_code}: {e.response.text}")

        except Exception as e:
            last_error = APIError(f"未知错误: {e}")

        # 等待重试
        if attempt < max_retries - 1:
            wait_time = retry_delay * (2 ** attempt)
            time.sleep(wait_time)

    # 所有重试失败
    raise last_error
```

### 2. 故障降级

```python
def call_with_fallback(
    api: MultiModelAPI,
    models: list,
    prompt: str
) -> Tuple[str, str, dict]:
    """
    故障降级：依次尝试多个模型

    Args:
        api: API实例
        models: 模型列表（按优先级排序）
        prompt: 提示词

    Returns:
        (response_content, model_used, usage_info)
    """
    last_error = None

    for model in models:
        try:
            content, usage = call_with_retry(api, model, prompt)
            return content, model, usage

        except APIError as e:
            last_error = e
            print(f"[WARN] {model} 失败: {e}")
            continue

    # 所有模型都失败
    raise APIError(f"所有模型都失败: {last_error}")


# 使用示例
def smart_call(api: MultiModelAPI, prompt: str):
    """智能调用：自动降级"""

    # 场景1：实时任务
    models = ["zhipu", "hunyuan", "nvidia2", "nvidia1"]
    content, model_used, usage = call_with_fallback(api, models, prompt)

    print(f"使用模型: {model_used}")
    print(f"耗时: {usage['latency']:.2f}秒")

    return content
```

---

## ⚡ **性能优化**

### 1. 批量请求优化

```python
from typing import List
import asyncio

async def batch_call_api(
    api: MultiModelAPI,
    model: str,
    prompts: List[str],
    max_concurrent: int = 5
) -> List[Tuple[str, dict]]:
    """
    批量调用API

    Args:
        api: API实例
        model: 模型名称
        prompts: 提示词列表
        max_concurrent: 最大并发数

    Returns:
        结果列表
    """
    semaphore = Semaphore(max_concurrent)

    async def single_call(prompt: str):
        async with semaphore:
            content, usage = await asyncio.to_thread(api.call_api, model, prompt)
            return (content, usage)

    tasks = [single_call(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)

    return results


# 使用示例
async def run_batch():
    api = MultiModelAPI()

    prompts = ["你好"] * 10
    results = await batch_call_api(api, "zhipu", prompts, max_concurrent=1)

    for content, usage in results:
        print(f"响应: {content}, 耗时: {usage['latency']:.2f}秒")
```

### 2. 响应缓存

见上文 `ResponseCache` 类。

### 3. 流式响应（如果API支持）

```python
def stream_response(api: MultiModelAPI, model: str, prompt: str):
    """流式响应"""
    config = api.api_configs[model]

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": config['model'],
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "max_tokens": 1024
    }

    response = requests.post(
        config['url'],
        headers=headers,
        json=payload,
        stream=True,
        timeout=60
    )

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = json.loads(line[6:])
                if data['choices'][0]['finish_reason'] is None:
                    content = data['choices'][0]['delta']['content']
                    yield content
```

---

## 🎮 **负载均衡策略**

```python
import random

def weighted_random(weights: dict) -> str:
    """
    加权随机选择

    Args:
        weights: {model_name: weight}

    Returns:
        选中的模型名称
    """
    models = list(weights.keys())
    probabilities = list(weights.values())

    return random.choices(models, weights=probabilities)[0]


# 负载均衡配置
LOAD_BALANCING_CONFIG = {
    "default": {
        "hunyuan": 0.50,
        "nvidia1": 0.20,
        "nvidia2": 0.20,
        "zhipu": 0.10
    },
    "bulk": {
        "hunyuan": 1.0
    },
    "realtime": {
        "zhipu": 1.0
    },
    "complex": {
        "nvidia1": 0.6,
        "nvidia2": 0.4
    }
}


def load_balance(task_type: str = "default") -> str:
    """负载均衡"""
    config = LOAD_BALANCING_CONFIG.get(task_type, LOAD_BALANCING_CONFIG["default"])
    return weighted_random(config)
```

---

## 📊 **监控与告警**

### 1. 性能监控

```python
import time
from collections import defaultdict

class PerformanceMonitor:
    """性能监控"""

    def __init__(self):
        self.stats = defaultdict(lambda: {
            "total_calls": 0,
            "total_latency": 0,
            "success_count": 0,
            "failure_count": 0
        })

    def record_call(self, model: str, latency: float, success: bool):
        """记录调用"""
        stats = self.stats[model]
        stats["total_calls"] += 1
        stats["total_latency"] += latency

        if success:
            stats["success_count"] += 1
        else:
            stats["failure_count"] += 1

    def get_stats(self, model: str) -> dict:
        """获取统计"""
        stats = self.stats[model]

        if stats["total_calls"] == 0:
            return stats.copy()

        return {
            "total_calls": stats["total_calls"],
            "avg_latency": stats["total_latency"] / stats["total_calls"],
            "success_rate": stats["success_count"] / stats["total_calls"],
            "failure_count": stats["failure_count"]
        }


# 使用示例
monitor = PerformanceMonitor()

# 记录调用
monitor.record_call("zhipu", 1.03, True)
monitor.record_call("hunyuan", 1.20, True)

# 获取统计
print(monitor.get_stats("zhipu"))
```

### 2. 健康检查

```python
def health_check(api: MultiModelAPI) -> dict:
    """健康检查"""
    results = {}

    for model_name in api.api_configs.keys():
        if model_name == "siliconflow":
            continue

        try:
            # 简单测试调用
            content, usage = api.call_api(model_name, "测试")

            results[model_name] = {
                "status": "healthy",
                "latency": usage["latency"],
                "last_check": time.time()
            }

        except Exception as e:
            results[model_name] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": time.time()
            }

    return results
```

---

## 📝 **总结**

### 关键要点

1. **智谱**：速度最快（1.03秒），但并发只有1，适合单任务
2. **混元**：无RPM限制，并发5，高并发场景最优
3. **英伟达**：思考模式最深，适合复杂推理
4. **SiliconFlow**：Embeddings专用，0.10秒超快

### 最佳实践

- ✅ 使用智能路由，根据任务类型选择模型
- ✅ 实现重试和降级机制，保证高可用
- ✅ 使用缓存减少重复调用
- ✅ 控制并发，避免触发限制
- ✅ 监控性能，及时发现问题

### 下一步

- 实施OpenClaw V2 MVP集成
- 开发MultiModelRateLimiter
- 开发TaskClassifier
- 实现负载均衡和智能路由

---

**文档版本：** v1.0
**最后更新：** 2026-02-16
**维护者：** Claw
