"""
自主实现的web_fetch工具
使用httpx + BeautifulSoup，完全自主可控
"""
import httpx
import logging
from typing import Optional, Dict
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


class WebFetchTool:
    """自主实现的web_fetch，完全独立于OpenClaw"""

    def __init__(
        self,
        timeout: float = 10.0,
        max_chars: int = 10000,
        extract_mode: str = "markdown"
    ):
        """
        初始化

        Args:
            timeout: 超时时间（秒）
            max_chars: 最大字符数
            extract_mode: 提取模式（"markdown"或"text"）
        """
        self.timeout = timeout
        self.max_chars = max_chars
        self.extract_mode = extract_mode

        # 支持的MIME类型
        self.text_mime_types = [
            "text/html",
            "text/plain",
            "text/xml",
            "text/markdown",
            "application/json",
            "application/xml",
            "application/xhtml+xml"
        ]

    async def fetch(
        self,
        url: str,
        extract_mode: Optional[str] = None,
        max_chars: Optional[int] = None
    ) -> Optional[str]:
        """
        抓取网页内容

        Args:
            url: 目标URL
            extract_mode: 提取模式（"markdown"或"text"）
            max_chars: 最大字符数

        Returns:
            网页内容（文本）
        """
        if not url:
            return None

        # 验证URL
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                logger.error(f"[WebFetch] 无效的URL: {url}")
                return None
        except Exception as e:
            logger.error(f"[WebFetch] URL解析失败: {e}")
            return None

        mode = extract_mode or self.extract_mode
        chars_limit = max_chars or self.max_chars

        try:
            # 发送HTTP请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }

                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()

                # 检查Content-Type
                content_type = response.headers.get("content-type", "").lower()
                if not any(mime in content_type for mime in self.text_mime_types):
                    logger.warning(f"[WebFetch] 不支持的Content-Type: {content_type}")
                    return f"URL返回非文本内容: {content_type}"

                # 提取内容
                content = await response.aread()
                text = content.decode('utf-8', errors='ignore')

                # 根据模式提取
                if mode == "text":
                    result = self._extract_text(text)
                else:
                    result = self._extract_html(text)

                # 限制长度
                if len(result) > chars_limit:
                    result = result[:chars_limit] + "\n...[截断]"

                logger.info(f"[WebFetch] 抓取成功: url={url}, 长度={len(result)}")
                return result

        except httpx.TimeoutException:
            logger.error(f"[WebFetch] 请求超时: {url}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"[WebFetch] HTTP错误: {e}")
            return None
        except Exception as e:
            logger.error(f"[WebFetch] 抓取失败: {e}")
            return None

    def _extract_text(self, html: str) -> str:
        """
        提取纯文本

        Args:
            html: HTML内容

        Returns:
            纯文本
        """
        # 移除脚本和样式
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.IGNORECASE | re.DOTALL)

        # 移除HTML标签
        html = re.sub(r'<[^>]+>', '', html)

        # 清理空白
        html = re.sub(r'\s+', ' ', html)
        html = html.strip()

        return html

    def _extract_html(self, html: str) -> str:
        """
        提取HTML内容（简化markdown）

        Args:
            html: HTML内容

        Returns:
            简化的markdown文本
        """
        # 移除脚本和样式
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.IGNORECASE | re.DOTALL)

        # 提取主要文本（简化处理）
        lines = [
            self._extract_text(line)
            for line in html.split('\n')
        ]

        # 过滤空行
        lines = [line for line in lines if line.strip()]

        return '\n'.join(lines)

    def sync_fetch(
        self,
        url: str,
        extract_mode: Optional[str] = None,
        max_chars: Optional[int] = None
    ) -> Optional[str]:
        """
        同步版本

        用于不支持async的场景
        """
        import asyncio

        return asyncio.run(self.fetch(url, extract_mode, max_chars))


# 便捷函数
async def web_fetch(
    url: str,
    extract_mode: str = "markdown",
    max_chars: int = 10000
) -> Optional[str]:
    """
    web_fetch便捷函数

    Args:
        url: 目标URL
        extract_mode: 提取模式
        max_chars: 最大字符数

    Returns:
        网页内容
    """
    tool = WebFetchTool(extract_mode=extract_mode, max_chars=max_chars)
    return await tool.fetch(url)


# 测试
if __name__ == "__main__":
    import sys
    import asyncio

    # 设置Unicode输出（Windows）
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    async def test():
        # 测试抓取
        url = "https://example.com"
        content = await web_fetch(url, max_chars=500)

        print("\n" + "="*70)
        print("自主WebFetch测试")
        print("="*70 + "\n")

        print(f"URL: {url}\n")
        print("内容:")
        print("-"*70)
        print(content)
        print("-"*70)

        print("\n" + "="*70)
        print("测试完成")
        print("="*70 + "\n")

    asyncio.run(test())
