"""
WebSocket连接管理器
管理所有活跃的WebSocket连接
"""
from typing import Dict, Set
from asyncio import Queue
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self, max_connections: int = 1000, max_per_ip: int = 10):
        """
        初始化连接管理器

        Args:
            max_connections: 最大连接数
            max_per_ip: 单个IP最大连接数
        """
        self.max_connections = max_connections
        self.max_per_ip = max_per_ip

        # 活跃连接：{connection_id: websocket}
        self.active_connections: Dict[str, object] = {}

        # IP连接映射：{ip: set(connection_id)}
        self.ip_connections: Dict[str, Set[str]] = {}

    async def connect(self, connection_id: str, websocket: object, client_ip: str = "unknown"):
        """
        添加新连接

        Args:
            connection_id: 连接唯一ID
            websocket: WebSocket对象
            client_ip: 客户端IP

        Raises:
            ConnectionError: 连接限制
        """
        # 检查总连接数限制
        if len(self.active_connections) >= self.max_connections:
            logger.warning(f"达到最大连接数限制: {self.max_connections}")
            raise ConnectionError("Too many connections")

        # 检查单IP连接数限制
        if len(self.ip_connections.get(client_ip, set())) >= self.max_per_ip:
            logger.warning(f"IP {client_ip} 达到连接数限制: {self.max_per_ip}")
            raise ConnectionError(f"Too many connections from this IP")

        # 添加连接
        self.active_connections[connection_id] = websocket
        if client_ip not in self.ip_connections:
            self.ip_connections[client_ip] = set()
        self.ip_connections[client_ip].add(connection_id)

        logger.info(f"连接已添加: {connection_id} (IP: {client_ip})")

    def disconnect(self, connection_id: str, client_ip: str = "unknown"):
        """
        移除连接

        Args:
            connection_id: 连接ID
            client_ip: 客户端IP
        """
        # 从活跃连接中移除
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # 从IP连接映射中移除
        if client_ip in self.ip_connections:
            self.ip_connections[client_ip].discard(connection_id)
            if not self.ip_connections[client_ip]:
                del self.ip_connections[client_ip]

        logger.info(f"连接已移除: {connection_id}")

    def is_connected(self, connection_id: str) -> bool:
        """
        检查连接是否活跃

        Args:
            connection_id: 连接ID

        Returns:
            是否连接
        """
        return connection_id in self.active_connections

    def get_connection(self, connection_id: str):
        """
        获取连接对象

        Args:
            connection_id: 连接ID

        Returns:
            WebSocket对象或None
        """
        return self.active_connections.get(connection_id)

    def get_active_count(self) -> int:
        """
        获取活跃连接数

        Returns:
            活跃连接数
        """
        return len(self.active_connections)
