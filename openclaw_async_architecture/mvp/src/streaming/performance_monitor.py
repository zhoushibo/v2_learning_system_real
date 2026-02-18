"""
性能监控模块
用于监控流式响应的各个阶段耗时
"""
import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标"""

    # 时间戳
    t_start: float = 0.0              # 开始时间
    t_dns: float = 0.0                # DNS解析时间
    t_connect: float = 0.0            # TCP连接时间
    t_tls: float = 0.0                # TLS握手时间
    t_first_byte: float = 0.0         # API第一字节时间
    t_complete: float = 0.0           # 完成时间

    # 内容统计
    chunk_count: int = 0              # chunk数量
    total_chars: int = 0              # 总字符数

    # 计算属性
    def get_dns_time(self) -> float:
        """DNS解析耗时"""
        return self.t_dns - self.t_start

    def get_connect_time(self) -> float:
        """TCP连接耗时"""
        return self.t_connect - self.t_dns

    def get_tls_time(self) -> float:
        """TLS握手耗时"""
        return self.t_tls - self.t_connect

    def get_first_byte_time(self) -> float:
        """首字节耗时（从开始到第一字节）"""
        return self.t_first_byte - self.t_start

    def get_stream_time(self) -> float:
        """流式传输耗时（第一字节到完成）"""
        if self.t_first_byte == 0:
            return 0.0
        return self.t_complete - self.t_first_byte

    def get_total_time(self) -> float:
        """总耗时"""
        return self.t_complete - self.t_start

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

    def to_log_string(self, provider: str) -> str:
        """生成日志字符串"""
        return (
            f"[PERF] {provider} | "
            f"首字:{self.get_first_byte_time()*1000:.0f}ms | "
            f"完整:{self.get_total_time()*1000:.0f}ms | "
            f"字符:{self.total_chars} | "
            f"chunks:{self.chunk_count} | "
            f"DNS:{self.get_dns_time()*1000:.0f}ms | "
            f"T-TLS:{self.get_tls_time()*1000:.0f}ms"
        )


class PerformanceMonitor:
    """性能监控器"""

    @staticmethod
    def start() -> PerformanceMetrics:
        """开始监控"""
        return PerformanceMetrics(t_start=time.time())

    @staticmethod
    def mark_dns(metrics: PerformanceMetrics):
        """标记DNS解析完成"""
        metrics.t_dns = time.time()
        logger.debug(f"[PERF] DNS解析完成: {metrics.get_dns_time()*1000:.0f}ms")

    @staticmethod
    def mark_connect(metrics: PerformanceMetrics):
        """标记TCP连接完成"""
        metrics.t_connect = time.time()
        logger.debug(f"[PERF] TCP连接完成: {metrics.get_connect_time()*1000:.0f}ms")

    @staticmethod
    def mark_tls(metrics: PerformanceMetrics):
        """标记TLS握手完成"""
        metrics.t_tls = time.time()
        logger.debug(f"[PERF] TLS握手完成: {metrics.get_tls_time()*1000:.0f}ms")

    @staticmethod
    def mark_first_byte(metrics: PerformanceMetrics):
        """标记第一字节到达"""
        metrics.t_first_byte = time.time()
        logger.debug(f"[PERF] 第一字节到达: {metrics.get_first_byte_time()*1000:.0f}ms")

    @staticmethod
    def mark_complete(metrics: PerformanceMetrics, chunk_count: int, total_chars: int):
        """标记完成"""
        metrics.t_complete = time.time()
        metrics.chunk_count = chunk_count
        metrics.total_chars = total_chars
        logger.debug(f"[PERF] 流式传输完成: {metrics.get_stream_time()*1000:.0f}ms")

    @staticmethod
    def check_target(metrics: PerformanceMetrics, provider: str, is_first_call: bool = True) -> bool:
        """
        检查是否达到性能目标

        Args:
            metrics: 性能指标
            provider: API提供商
            is_first_call: 是否首次调用（冷启动）

        Returns:
            是否达标
        """
        first_byte_time = metrics.get_first_byte_time()

        # 根据目标判断
        if provider in ["zhipu", "hunyuan"]:
            # 国内API：<1秒
            target = 1.0
        elif not is_first_call:
            # 国外API热连接：<3秒
            target = 3.0
        else:
            # 国外API首次：<8秒
            target = 8.0

        is_target_met = first_byte_time <= target

        if is_target_met:
            logger.info(metrics.to_log_string(provider) + " | [OK] 目标达标")
        else:
            logger.warning(metrics.to_log_string(provider) + f" | [WARN] 未达标（目标<{target}s）")

        return is_target_met


# 上下文管理器（方便使用）
class PerformanceMonitorContext:
    """性能监控上下文管理器"""

    def __init__(self, provider: str, is_first_call: bool = True):
        self.provider = provider
        self.is_first_call = is_first_call
        self.metrics: Optional[PerformanceMetrics] = None
        self.chunk_count = 0
        self.total_chars = 0

    def __enter__(self):
        self.metrics = PerformanceMonitor.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.metrics and self.metrics.t_first_byte > 0:
            PerformanceMonitor.mark_complete(
                self.metrics,
                self.chunk_count,
                self.total_chars
            )
            PerformanceMonitor.check_target(
                self.metrics,
                self.provider,
                self.is_first_call
            )
        return False

    def record_chunk(self, chunk: str):
        """记录一个chunk"""
        if self.metrics and self.metrics.t_first_byte == 0:
            # 第一个chunk
            PerformanceMonitor.mark_first_byte(self.metrics)

        self.chunk_count += 1
        self.total_chars += len(chunk)
