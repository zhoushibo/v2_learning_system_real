"""
自主实现的web_search工具
使用Brave Search API，完全自主可控
"""
import httpx
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class WebSearchTool:
    """自主实现的web_search，完全独立于OpenClaw"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化

        Args:
            api_key: Brave Search API Key (如果为None，使用环境变量或免费模式)
        """
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    async def search(
        self,
        query: str,
        count: int = 5,
        country: str = "CN",
        search_lang: str = "zh-CN"
    ) -> List[Dict]:
        """
        执行搜索

        Args:
            query: 搜索查询
            count: 返回结果数量（1-10）
            country: 国家代码
            search_lang: 搜索语言

        Returns:
            搜索结果列表
        """
        if not query or not query.strip():
            return []

        params = {
            "q": query.strip(),
            "count": min(count, 10)
        }

        headers = {}

        # 如果有API key，添加认证
        if self.api_key:
            headers["X-Subscription-Token"] = self.api_key

        # 如果有country参数
        if country and country != "ALL":
            params["country"] = country

        # 如果有search_lang参数
        if search_lang:
            params["search_lang"] = search_lang

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()

                # 解析结果
                results = []
                if "web" in data and "results" in data["web"]:
                    for item in data["web"]["results"]:
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "snippet": item.get("snippet", ""),
                        })

                logger.info(f"[WebSearch] 搜索成功: query='{query}', 结果数={len(results)}")
                return results

        except httpx.HTTPStatusError as e:
            logger.error(f"[WebSearch] HTTP错误: {e}")
            return []
        except Exception as e:
            logger.error(f"[WebSearch] 搜索失败: {e}")
            return []

    def sync_search(
        self,
        query: str,
        count: int = 5,
        country: str = "CN",
        search_lang: str = "zh-CN"
    ) -> List[Dict]:
        """
        同步版本

        用于不支持async的场景
        """
        import asyncio

        return asyncio.run(self.search(query, count, country, search_lang))


# 便捷函数
async def web_search(
    query: str,
    count: int = 5,
    country: str = "CN",
    search_lang: str = "zh-CN",
    api_key: Optional[str] = None
) -> List[Dict]:
    """
    web_search便捷函数

    Args:
        query: 搜索查询
        count: 返回结果数量
        country: 国家代码
        search_lang: 搜索语言
        api_key: Brave Search API Key

    Returns:
        搜索结果列表
    """
    tool = WebSearchTool(api_key=api_key)
    return await tool.search(query, count, country, search_lang)


# 测试
if __name__ == "__main__":
    import sys
    import os
    from dotenv import load_dotenv

    # 加载.env
    load_dotenv()

    # 设置Unicode输出（Windows）
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    async def test():
        # 测试搜索
        results = await web_search("OpenClaw 替代方案")

        print("\n" + "="*70)
        print("自主WebSearch测试")
        print("="*70 + "\n")

        for i, result in enumerate(results, 1):
            print(f"\n[{i}] {result['title']}")
            print(f"    URL: {result['url']}")
            print(f"    摘要: {result['snippet']}")

        print("\n" + "="*70)
        print(f"测试完成，共{len(results)}条结果")
        print("="*70 + "\n")

    asyncio.run(test())
