# -*- coding: utf-8 -*-
"""进程管理器 - 管理子进程的启动、停止、监控"""
import subprocess
import sys
import psutil
import time
from typing import Optional, Dict, List


class ProcessInfo:
    """进程信息"""
    def __init__(self, pid: int, command: str, working_dir: str, start_time: float = None):
        self.pid = pid
        self.command = command
        self.working_dir = working_dir
        self.start_time = start_time or time.time()
        self.process = psutil.Process(pid) if psutil.pid_exists(pid) else None

    @property
    def is_running(self) -> bool:
        """进程是否运行中"""
        if self.process is None:
            return False
        return self.process.is_running()

    @property
    def runtime(self) -> float:
        """运行时间（秒）"""
        return time.time() - self.start_time

    @property
    def memory_mb(self) -> float:
        """内存占用（MB）"""
        if self.process is None or not self.is_running:
            return 0.0
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except:
            return 0.0


class ProcessManager:
    """进程管理器"""

    def __init__(self):
        self.processes: Dict[str, ProcessInfo] = {}

    def start_process(self, component_id: str, command: List[str], working_dir: str) -> bool:
        """
        启动进程

        Args:
            component_id: 组件ID
            command: 命令列表（例如 ['python', 'launcher.py', 'gateway']）
            working_dir: 工作目录

        Returns:
            是否启动成功
        """
        try:
            # 启动子进程
            process = subprocess.Popen(
                command,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )

            # 保存进程信息
            self.processes[component_id] = ProcessInfo(
                pid=process.pid,
                command=' '.join(command),
                working_dir=working_dir
            )

            print(f"[ProcessManager] {component_id} 启动成功 (PID: {process.pid})")
            return True

        except Exception as e:
            print(f"[ProcessManager] {component_id} 启动失败: {e}")
            return False

    def stop_process(self, component_id: str) -> bool:
        """
        停止进程

        Args:
            component_id: 组件ID

        Returns:
            是否停止成功
        """
        if component_id not in self.processes:
            print(f"[ProcessManager] {component_id} 未找到")
            return False

        process_info = self.processes[component_id]

        if not process_info.is_running:
            print(f"[ProcessManager] {component_id} 已停止")
            del self.processes[component_id]
            return True

        try:
            # 尝试优雅停止
            process_info.process.terminate()

            # 等待3秒
            for _ in range(30):
                if not process_info.is_running:
                    break
                time.sleep(0.1)

            # 如果还在运行，强制停止
            if process_info.is_running:
                process_info.process.kill()
                time.sleep(0.5)

            # 清理
            del self.processes[component_id]
            print(f"[ProcessManager] {component_id} 停止成功")
            return True

        except Exception as e:
            print(f"[ProcessManager] {component_id} 停止失败: {e}")
            return False

    def get_process_status(self, component_id: str) -> Optional[Dict]:
        """
        获取进程状态

        Args:
            component_id: 组件ID

        Returns:
            进程状态信息字典
        """
        if component_id not in self.processes:
            return None

        process_info = self.processes[component_id]

        return {
            "id": component_id,
            "pid": process_info.pid,
            "command": process_info.command,
            "is_running": process_info.is_running,
            "runtime": process_info.runtime,
            "memory_mb": process_info.memory_mb
        }

    def get_all_processes(self) -> List[Dict]:
        """
        获取所有进程状态

        Returns:
            所有进程状态列表
        """
        result = []

        for component_id, process_info in self.processes.items():
            result.append({
                "id": component_id,
                "pid": process_info.pid,
                "command": process_info.command,
                "is_running": process_info.is_running,
                "runtime": process_info.runtime,
                "memory_mb": process_info.memory_mb
            })

        return result

    def cleanup_dead_processes(self):
        """清理已停止的进程"""
        dead_components = []

        for component_id, process_info in list(self.processes.items()):
            if not process_info.is_running:
                dead_components.append(component_id)

        for component_id in dead_components:
            print(f"[ProcessManager] 清理已停止的进程: {component_id}")
            del self.processes[component_id]
