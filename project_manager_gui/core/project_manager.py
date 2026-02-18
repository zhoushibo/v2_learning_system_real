# -*- coding: utf-8 -*-
"""项目管理器 - 管理项目配置和组件控制"""
import json
import os
import requests
from typing import Dict, List, Optional
from .process_manager import ProcessManager


class ProjectManager:
    """项目管理器"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._get_default_config_path()
        self.projects: Dict = {}
        self.process_manager = ProcessManager()

        # 加载配置
        self.load_config()

    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        return os.path.join(os.path.dirname(__file__), "..", "config", "projects.json")

    def load_config(self) -> bool:
        """
        加载项目配置

        Returns:
            是否加载成功
        """
        try:
            if not os.path.exists(self.config_path):
                print(f"[ProjectManager] 配置文件不存在: {self.config_path}")
                return False

            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.projects = {p['id']: p for p in data.get('projects', [])}

            print(f"[ProjectManager] 加载了 {len(self.projects)} 个项目")
            return True

        except Exception as e:
            print(f"[ProjectManager] 加载配置失败: {e}")
            return False

    def get_all_projects(self) -> List[Dict]:
        """
        获取所有项目

        Returns:
            项目列表
        """
        return list(self.projects.values())

    def get_project(self, project_id: str) -> Optional[Dict]:
        """
        获取指定项目

        Args:
            project_id: 项目ID

        Returns:
            项目信息
        """
        return self.projects.get(project_id)

    def start_component(self, project_id: str, component_id: str) -> bool:
        """
        启动项目组件

        Args:
            project_id: 项目ID
            component_id: 组件ID

        Returns:
            是否启动成功
        """
        project = self.get_project(project_id)
        if not project:
            print(f"[ProjectManager] 项目不存在: {project_id}")
            return False

        # 查找组件
        component = None
        for comp in project.get('components', []):
            if comp.get('id') == component_id:
                component = comp
                break

        if not component:
            print(f"[ProjectManager] 组件不存在: {project_id}/{component_id}")
            return False

        # 检查工作目录
        working_dir = component.get('working_dir')
        if not os.path.exists(working_dir):
            print(f"[ProjectManager] 工作目录不存在: {working_dir}")
            return False

        # 检查端口占用
        port = component.get('port')
        if port:
            if self._is_port_in_use(port):
                print(f"[ProjectManager] 端口 {port} 已被占用")
                return False

        # 启动进程
        command = component.get('command', '').split()
        full_component_id = f"{project_id}_{component_id}"

        success = self.process_manager.start_process(
            component_id=full_component_id,
            command=command,
            working_dir=working_dir
        )

        return success

    def stop_component(self, project_id: str, component_id: str) -> bool:
        """
        停止项目组件

        Args:
            project_id: 项目ID
            component_id: 组件ID

        Returns:
            是否停止成功
        """
        full_component_id = f"{project_id}_{component_id}"
        return self.process_manager.stop_process(full_component_id)

    def get_component_status(self, project_id: str, component_id: str) -> Optional[Dict]:
        """
        获取组件状态

        Args:
            project_id: 项目ID
            component_id: 组件ID

        Returns:
            组件状态
        """
        full_component_id = f"{project_id}_{component_id}"
        return self.process_manager.get_process_status(full_component_id)

    def check_component_health(self, project_id: str, component_id: str) -> Optional[Dict]:
        """
        健康检查

        Args:
            project_id: 项目ID
            component_id: 组件ID

        Returns:
            健康状态
        """
        project = self.get_project(project_id)
        if not project:
            return None

        # 查找组件
        component = None
        for comp in project.get('components', []):
            if comp.get('id') == component_id:
                component = comp
                break

        if not component:
            return None

        health_check_url = component.get('health_check')
        if not health_check_url:
            return None

        try:
            response = requests.get(health_check_url, timeout=3)
            return {
                "healthy": True,
                "status_code": response.status_code,
                "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except requests.exceptions.ConnectionError:
            return {"healthy": False, "error": "连接失败"}
        except requests.exceptions.Timeout:
            return {"healthy": False, "error": "超时"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    def _is_port_in_use(self, port: int) -> bool:
        """
        检查端口是否被占用

        Args:
            port: 端口号

        Returns:
            是否被占用
        """
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    def cleanup(self):
        """清理资源"""
        print("[ProjectManager] 清理所有进程...")
        all_processes = self.process_manager.get_all_processes()
        for proc in all_processes:
            self.process_manager.stop_process(proc['id'])
