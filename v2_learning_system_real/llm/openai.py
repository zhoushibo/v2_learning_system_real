"""
OpenAIProvider - OpenAI API提供者

使用OpenAI GPT模型进行学习
支持自定义base_url（如NVIDIA API）

特别注意：
- GLM4.7等模型使用reasoning_content而非content字段
- GLM4.7需要max_tokens=4000以上才能输出完整JSON
"""
import logging
import json
import re
from typing import Dict, List, Optional
from openai import AsyncOpenAI, Timeout
import asyncio


from .base import LLMProvider, APIError, RateLimitError, AuthenticationError, InvalidResponseError

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):

    # ⭐ API Key 池（负载均衡 + 自动切换）
    API_KEY_POOL = [
        "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",  # 主 Key
        "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",  # 备用 Key
    ]
    """
    OpenAI API提供者

    支持的模型：
    - gpt-3.5-turbo: 快速，便宜
    - gpt-4: 高质量
    - gpt-4-turbo: GPT-4的更快版本

    也支持OpenAI兼容的API：
    - NVIDIA API: https://integrate.api.nvidia.com/v1
    - 其他兼容OpenAI格式的API

    注意：
    - GLM4.7等模型使用reasoning_content而非content字段
    - GLM4.7需要max_tokens=4000以上（max_tokens=8000更安全）
    - ⭐ 新增：超时机制，防止卡住
    """

    # ⭐ 多模型池（自动 fallback）
    MODEL_POOL = [
        "qwen/qwen3.5-397b-a17b",              # 主模型，397B
        "z-ai/glm5",                           # 最新 GLM-5
        "moonshotai/kimi-k2.5",                # Kimi K2.5
        "qwen/qwen3-next-80b-a3b-instruct",    # Qwen3-Next 80B
        "z-ai/glm4.7",                         # 备用 GLM-4.7
    ]
    DEFAULT_MODEL = MODEL_POOL[0]
    FALLBACK_MODEL = MODEL_POOL[1] if len(MODEL_POOL) > 1 else MODEL_POOL[0]

    # ⭐ 新增：超时配置
    DEFAULT_TIMEOUT = 180.0  # 3分钟（GLM4.7可能需要2-3分钟）
    CONNECT_TIMEOUT = 10.0  # 连接超时10秒

    def __init__(self, api_key: str = None, model: str = None, base_url: str = None, max_tokens: int = None, timeout: float = None):
        """
        初始化OpenAI提供者

        Args:
            api_key: OpenAI API密钥
            model: 模型名称（默认：gpt-4）
            base_url: 自定义base_url（如NVIDIA API）
            max_tokens: 最大输出tokens（GLM4.7建议4000-8000）
            timeout: 超时时间（秒，默认180秒）
        """
        # ⭐ 默认使用 NVIDIA API
        if base_url is None:
            base_url = "https://integrate.api.nvidia.com/v1"
        
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        self.base_url = base_url
        
        # ⭐ 修复：确保 api_key 始终有值（在 super() 之后）
        if api_key is None:
            api_key = self.API_KEY_POOL[0]
        
        self.api_key_index = self.API_KEY_POOL.index(api_key) if api_key in self.API_KEY_POOL else 0
        self.timeout = timeout or self.DEFAULT_TIMEOUT

        # 针对GLM4.7自动调整max_tokens
        # 针对不同模型调整 max_tokens
        model_lower = (model or "").lower()
        if "glm" in model_lower:
            self.max_tokens = 8000 if max_tokens is None else max(max_tokens, 4000)
        elif "qwen" in model_lower:
            # Qwen3.5 支持 262K 上下文，推荐 max_tokens=16384
            self.max_tokens = 16384 if max_tokens is None else max(max_tokens, 8000)
        else:
            self.max_tokens = max_tokens or 2000

        # 创建客户端（带超时）
        # 确保 api_key 不为 None
        if api_key is None:
            api_key = self.API_KEY_POOL[0]
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=Timeout(
                connect=self.CONNECT_TIMEOUT,
                read=self.timeout,
                write=self.timeout,
                pool=self.DEFAULT_TIMEOUT
            )
        )

        if base_url:
            logger.info(f"OpenAIProvider使用自定义base_url: {base_url}, max_tokens={self.max_tokens}, timeout={self.timeout}s")

    async def learning(
        self,
        topic: str,
        perspective: str,
        style: str = "deep_analysis"
    ) -> Dict[str, List[str]]:
        """
        使用OpenAI GPT学习主题

        Args:
            topic: 学习主题
            perspective: 学习视角
            style: 学习风格

        Returns:
            学习结果字典

        Raises:
            APIError: API调用失败
            RateLimitError: 速率限制
            AuthenticationError: 认证失败
        """
        try:
            # 构建Prompt
            prompt = self._build_prompt(topic, perspective, style)

            # 调用OpenAI API
            api_name = self.base_url if self.base_url else "OpenAI"
            logger.info(f"请求API学习: {topic} ({perspective}) [{api_name}]")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位经验丰富的技术专家，擅长深度学习和知识总结。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=self.max_tokens
                # ⭐ 超时已在初始化时设置
            )

            # 解析响应
            # 注意：GLM4.7等模型使用reasoning_content而非content
            content = self._extract_content(response)

            if not content:
                logger.error(f"响应无content字段: {response}")
                raise InvalidResponseError("响应格式错误：无content或reasoning_content字段")

            logger.debug(f"API响应内容: {content[:200]}...")

            result = self._parse_response(content)

            # 记录使用情况
            logger.info(f"API学习完成: {topic} ({perspective})")
            logger.debug(f"使用的tokens: {response.usage.total_tokens}")

            return result

        except asyncio.TimeoutError as e:
            logger.error(f"API调用超时（{self.timeout}s）: {e}")
            raise APIError(f"API调用超时: {e}")

        except AuthenticationError as e:
            logger.error(f"API认证失败: {e}")
            raise AuthenticationError(f"API密钥无效: {e}")

        except RateLimitError as e:
            logger.warning(f"API速率限制: {e}")
            raise RateLimitError(f"API速率限制: {e}")

        except Exception as e:
            logger.error(f"API调用失败: {e}")
            raise APIError(f"API调用失败: {e}")

    def _extract_content(self, response) -> Optional[str]:
        """
        从响应中提取内容

        支持两种格式：
        1. 标准OpenAI: response.choices[0].message.content
        2. GLM4.7: response.choices[0].message.reasoning_content

        Args:
            response: OpenAI响应对象

        Returns:
            内容字符串
        """
        if not response.choices or len(response.choices) == 0:
            return None

        message = response.choices[0].message

        # 优先使用content（标准OpenAI格式）
        if hasattr(message, 'content') and message.content:
            return message.content

        # 如果content为空，尝试reasoning_content（GLM4.7格式）
        if hasattr(message, 'reasoning_content') and message.reasoning_content:
            return message.reasoning_content

        # 都没有，返回None
        return None


    async def learning_with_fallback(
        self,
        topic: str,
        perspective: str,
        style: str = "deep_analysis",
        max_retries: int = 3
    ) -> dict:
        """
        带自动 fallback 的学习方法
        
        策略：
        1. 尝试主模型
        2. 失败则切换到备用模型
        3. 最多重试 max_retries 次
        
        Args:
            topic: 学习主题
            perspective: 学习视角
            style: 学习风格
            max_retries: 最大重试次数
            
        Returns:
            学习结果字典
            
        Raises:
            APIError: 所有模型都失败
        """
        last_error = None
        
        # 遍历模型池和 API Key 池
        for i, model in enumerate(self.MODEL_POOL):
            current_model = self.model
            current_key_index = self.api_key_index
            
            try:
                # 切换到当前模型
                self.model = model
                logger.info(f"尝试模型 [{i+1}/{len(self.MODEL_POOL)}]: {model} [Key #{current_key_index + 1}]")
                
                # 调用学习（带重试）
                for attempt in range(max_retries):
                    try:
                        result = await self.learning(topic, perspective, style)
                        logger.info(f"✅ 模型 {model} 学习成功")
                        return result
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"模型 {model} 第{attempt+1}次失败，重试...: {e}")
                            import asyncio
                            await asyncio.sleep(1 * (attempt + 1))  # 指数退避
                        else:
                            raise
                
            except Exception as e:
                last_error = e
                logger.warning(f"❌ 模型 {model} [Key #{current_key_index + 1}] 失败：{e}")
                
                # 尝试切换 API Key
                if self.switch_api_key():
                    logger.info(f"🔄 已切换到新 API Key，继续尝试当前模型 {model}")
                    # 用新 Key 重试当前模型
                    try:
                        self.model = model
                        for attempt in range(max_retries):
                            try:
                                result = await self.learning(topic, perspective, style)
                                logger.info(f"✅ 模型 {model} [Key #{self.api_key_index + 1}] 学习成功")
                                return result
                            except Exception as retry_error:
                                if attempt < max_retries - 1:
                                    logger.warning(f"模型 {model} 第{attempt+1}次重试失败：{retry_error}")
                                    import asyncio
                                    await asyncio.sleep(1 * (attempt + 1))
                                else:
                                    raise
                    except Exception as retry_error:
                        logger.warning(f"模型 {model} 用新 Key 重试失败：{retry_error}")
                
                # 继续尝试下一个模型
                continue
            finally:
                # 恢复原模型
                self.model = current_model
        
        # 所有模型都失败
        error_msg = f"所有模型都失败（尝试了 {len(self.MODEL_POOL)} 个模型）"
        logger.error(error_msg)
        if last_error:
            error_msg += f" 最后错误：{last_error}"
        raise APIError(error_msg)


    def switch_api_key(self):
        """
        切换到下一个 API Key（用于 fallback）
        
        Returns:
            bool: 是否成功切换
        """
        if len(self.API_KEY_POOL) <= 1:
            return False
        
        # 切换到下一个 Key
        self.api_key_index = (self.api_key_index + 1) % len(self.API_KEY_POOL)
        new_key = self.API_KEY_POOL[self.api_key_index]
        
        # 更新客户端
        self.client = AsyncOpenAI(
            api_key=new_key,
            base_url=self.base_url,
            timeout=Timeout(
                connect=self.CONNECT_TIMEOUT,
                read=self.timeout,
                write=self.timeout,
                pool=self.DEFAULT_TIMEOUT
            )
        )
        
        logger.info(f"🔄 切换到 API Key #{self.api_key_index + 1}")
        return True

    async def validate_key(self) -> bool:
        """
        验证API密钥是否有效

        Returns:
            密钥是否有效
        """
        try:
            # 尝试列出模型
            await self.client.models.list()
            api_name = self.base_url if self.base_url else "OpenAI"
            logger.info(f"{api_name} API密钥验证成功")
            return True
        except AuthenticationError:
            logger.error("API密钥无效")
            return False
        except Exception as e:
            logger.warning(f"API密钥验证失败: {e}")
            return False

    def _build_prompt(self, topic: str, perspective: str, style: str) -> str:
        """
        构建学习Prompt

        Args:
            topic: 学习主题
            perspective: 学习视角
            style: 学习风格

        Returns:
            Prompt字符串
        """
        if style == "deep_analysis":
            prompt = f"""
你是一位经验丰富的{perspective}。

请深度学习以下主题：{topic}

要求：
1. 深度理解：不是表面介绍，而是底层原理
2. 实践导向：结合实际项目经验
3. 可操作建议：提供立即可用的建议
4. 最新信息：关注最新发展

请以JSON格式返回：
{{
  "lessons": [
    "课程标题1 - 10-15字",
    "课程标题2 - 10-15字",
    "..."
  ],
  "key_points": [
    "要点1 - 一句话总结",
    "要点2 - 一句话总结",
    "..."
  ],
  "recommendations": [
    "具体可操作的建议1 - 20-30字",
    "具体可操作的建议2 - 20-30字",
    "..."
  ]
}}

确保JSON格式正确，不要有语法错误。
"""
        else:  # quick_overview
            prompt = f"""
请快速了解{topic}（从{perspective}视角）。

请以JSON格式返回：
{{
  "lessons": ["课程1", "课程2", "课程3"],
  "key_points": ["要点1", "要点2", "要点3"],
  "recommendations": ["建议1", "建议2", "建议3"]
}}
"""

        return prompt

    def _parse_response(self, content: str) -> Dict[str, List[str]]:
        """
        解析LLM响应

        Args:
            content: LLM响应内容

        Returns:
            学习结果字典

        Raises:
            InvalidResponseError: 响应格式错误
        """
        try:
            # 尝试提取JSON（可能包含```json ```）
            json_str = self._extract_json(content)

            # 解析JSON
            result = json.loads(json_str)

            # 验证格式
            required_keys = ["lessons", "key_points", "recommendations"]
            for key in required_keys:
                if key not in result:
                    raise InvalidResponseError(f"响应缺少必需字段: {key}")

                if not isinstance(result[key], list):
                    raise InvalidResponseError(f"字段{key}不是列表类型")

            # 验证每个字段都有内容
            for key in required_keys:
                if len(result[key]) == 0:
                    logger.warning(f"字段{key}为空，使用默认值")
                    result[key] = self._get_default_content(key)

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.debug(f"原始内容: {content}")

            # 尝试使用正则表达式提取
            return self._extract_with_regex(content)

        except Exception as e:
            logger.error(f"响应解析失败: {e}")
            # 返回默认结果
            return self._get_default_result()

    def _extract_json(self, content: str) -> str:
        """
        从内容中提取JSON字符串

        Args:
            content: 内容字符串

        Returns:
            JSON字符串
        """
        # 尝试移除```json ```标记
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}'
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()

        # 如果没有找到，直接返回原内容
        return content.strip()

    def _extract_with_regex(self, content: str) -> Dict[str, List[str]]:
        """
        使用正则表达式提取内容

        Args:
            content: 内容字符串

        Returns:
            学习结果字典
        """
        result = {
            "lessons": [],
            "key_points": [],
            "recommendations": []
        }

        # 提取lessons（类似"lessons": [...])
        lessons_match = re.search(r'"lessons"\s*:\s*\[(.*?)\]', content, re.DOTALL)
        if lessons_match:
            lessons = re.findall(r'"([^"]*)"', lessons_match.group(1))
            result["lessons"] = lessons[:5] if len(lessons) > 5 else lessons

        # 提取key_points
        key_points_match = re.search(r'"key_points"\s*:\s*\[(.*?)\]', content, re.DOTALL)
        if key_points_match:
            key_points = re.findall(r'"([^"]*)"', key_points_match.group(1))
            result["key_points"] = key_points[:5] if len(key_points) > 5 else key_points

        # 提取recommendations
        recommendations_match = re.search(r'"recommendations"\s*:\s*\[(.*?)\]', content, re.DOTALL)
        if recommendations_match:
            recommendations = re.findall(r'"([^"]*)"', recommendations_match.group(1))
            result["recommendations"] = recommendations[:3] if len(recommendations) > 3 else recommendations

        # 如果提取失败，使用默认值
        if not any(result.values()):
            logger.warning("正则表达式提取失败，使用默认值")
            return self._get_default_result()

        return result

    def _get_default_result(self) -> Dict[str, List[str]]:
        """
        获取默认结果

        Returns:
            默认学习结果
        """
        return {
            "lessons": [
                "基础概念学习",
                "核心原理理解",
                "实际应用掌握"
            ],
            "key_points": [
                "关键知识点1",
                "关键知识点2",
                "关键知识点3"
            ],
            "recommendations": [
                "建议1：深入学习",
                "建议2：实践操作",
                "建议3：持续关注"
            ]
        }

    def _get_default_content(self, key: str) -> List[str]:
        """
        获取默认内容

        Args:
            key: 字段名称

        Returns:
            默认内容列表
        """
        defaults = {
            "lessons": ["课程1", "课程2", "课程3"],
            "key_points": ["要点1", "要点2", "要点3"],
            "recommendations": ["建议1", "建议2", "建议3"]
        }
        return defaults.get(key, [])
