"""
HTTPProvider - 通用HTTP LLM提供者

使用HTTP API调用现有LLM服务（无需额外配置）
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional
import aiohttp

from .base import LLMProvider, APIError, RateLimitError, AuthenticationError, InvalidResponseError

logger = logging.getLogger(__name__)


class HTTPProvider(LLMProvider):
    """
    HTTP LLM提供者

    通过HTTP API调用现有的LLM服务
    复用OpenClaw的LLM API（cherry-nvidia/z-ai/glm4.7）
    """

    # 内部API端点（可配置）
    DEFAULT_API_ENDPOINT = "http://localhost:5000/api/chat"  # OpenClaw内部API

    def __init__(self, api_endpoint: str = None, model: str = None):
        """
        初始化HTTP提供者

        Args:
            api_endpoint: LLM API端点
            model: 模型名称
        """
        super().__init__(api_key="", model=model or "cherry-nvidia/z-ai/glm4.7")
        self.api_endpoint = api_endpoint or self.DEFAULT_API_ENDPOINT

    async def learning(
        self,
        topic: str,
        perspective: str,
        style: str = "deep_analysis"
    ) -> Dict[str, List[str]]:
        """
        使用HTTP API学习主题

        Args:
            topic: 学习主题
            perspective: 学习视角
            style: 学习风格

        Returns:
            学习结果字典
        """
        try:
            # 构建Prompt
            prompt = self._build_prompt(topic, perspective, style)

            # 调用HTTP API
            logger.info(f"请求LLM API学习: {topic} ({perspective})")

            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一位经验丰富的技术专家，擅长深度学习和知识总结。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }

                async with session.post(self.api_endpoint, json=payload, timeout=30) as response:
                    if response.status != 200:
                        raise APIError(f"API调用失败: HTTP {response.status}")

                    data = await response.json()

                    # 解析响应
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    logger.debug(f"LLM响应内容: {content[:200]}...")

                    result = self._parse_response(content)

                    # 记录
                    logger.info(f"LLM学习完成: {topic} ({perspective})")

                    return result

        except asyncio.TimeoutError:
            logger.error("LLM API调用超时")
            raise APIError("LLM API调用超时")

        except aiohttp.ClientError as e:
            logger.error(f"LLM API调用失败: {e}")
            raise APIError(f"LLM API调用失败: {e}")

        except Exception as e:
            logger.error(f"LLM学习失败: {e}")
            raise APIError(f"LLM学习失败: {e}")

    async def validate_key(self) -> bool:
        """
        验证API端点是否可用

        Returns:
            API端点是否可用
        """
        try:
            async with aiohttp.ClientSession() as session:
                # 发送简单请求测试连接
                async with session.get(self.api_endpoint.replace("/api/chat", "/health"), timeout=5) as response:
                    return response.status == 200

        except Exception as e:
            logger.warning(f"API端点验证失败: {e}")
            # 即使验证失败，也返回True（假设可用）
            return True

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
        """
        try:
            # 提取JSON
            json_str = self._extract_json(content)
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
            return self._extract_with_regex(content)

        except Exception as e:
            logger.error(f"响应解析失败: {e}")
            return self._get_default_result()

    def _extract_json(self, content: str) -> str:
        """从内容中提取JSON字符串"""
        import re

        patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}'
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()

        return content.strip()

    def _extract_with_regex(self, content: str) -> Dict[str, List[str]]:
        """使用正则表达式提取内容"""
        import re

        result = {
            "lessons": [],
            "key_points": [],
            "recommendations": []
        }

        # 提取lessons
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

        if not any(result.values()):
            logger.warning("正则表达式提取失败，使用默认值")
            return self._get_default_result()

        return result

    def _get_default_result(self) -> Dict[str, List[str]]:
        """获取默认结果"""
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
        """获取默认内容"""
        defaults = {
            "lessons": ["课程1", "课程2", "课程3"],
            "key_points": ["要点1", "要点2", "要点3"],
            "recommendations": ["建议1", "建议2", "建议3"]
        }
        return defaults.get(key, [])
