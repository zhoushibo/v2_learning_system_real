"""配置管理"""
import os
from typing import Optional


class Settings:
    """OpenClaw V2 MVP 配置"""

    def __init__(self):
        # Gateway配置
        self.gateway_host = os.getenv("GATEWAY_HOST", "127.0.0.1")
        self.gateway_port = int(os.getenv("GATEWAY_PORT", "8000"))

        # Redis配置
        self.redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_password = os.getenv("REDIS_PASSWORD")

        # OpenClaw V1
        self.v1_gateway_url = os.getenv("V1_GATEWAY_URL", "http://127.0.0.1:18790")
        self.v1_gateway_token = os.getenv("V1_GATEWAY_TOKEN", "lbprg74nqGxsvopWqkgLAAefoIWKobzH")
        self.v1_agent_id = os.getenv("V1_AGENT_ID", "main")

        # Worker配置
        self.worker_timeout = int(os.getenv("WORKER_TIMEOUT", "60"))


# 全局配置实例
settings = Settings()
