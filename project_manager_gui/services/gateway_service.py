# -*- coding: utf-8 -*-
"""
Gateway Service Manager
Start/stop Gateway service from GUI
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict
import json


class GatewayService:
    """Gateway Service Manager"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent.parent
        self.gateway_script = self.workspace / "openclaw_async_architecture" / "streaming-service" / "src" / "gateway.py"
        self.config_file = self.workspace / "openclaw_async_architecture" / "API_CONFIG_FINAL.json"
        self.process: Optional[subprocess.Popen] = None
        self.port = 8001
    
    def is_running(self) -> bool:
        """Check if Gateway is running"""
        if self.process and self.process.poll() is None:
            return True
        
        # Also check by port
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', self.port))
        sock.close()
        return result == 0
    
    def start(self) -> Dict[str, any]:
        """Start Gateway service"""
        if self.is_running():
            return {
                "success": False,
                "message": "Gateway 已在运行中",
                "port": self.port
            }
        
        if not self.gateway_script.exists():
            return {
                "success": False,
                "message": f"找不到 Gateway 脚本：{self.gateway_script}"
            }
        
        try:
            # Start Gateway
            cmd = [sys.executable, str(self.gateway_script)]
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.gateway_script.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            
            return {
                "success": True,
                "message": f"Gateway 已启动 (端口 {self.port})",
                "port": self.port,
                "pid": self.process.pid
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"启动失败：{str(e)}"
            }
    
    def stop(self) -> Dict[str, any]:
        """Stop Gateway service"""
        if not self.is_running():
            return {
                "success": False,
                "message": "Gateway 未运行"
            }
        
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.process = None
            
            return {
                "success": True,
                "message": "Gateway 已停止"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"停止失败：{str(e)}"
            }
    
    def get_status(self) -> Dict[str, any]:
        """Get Gateway status"""
        running = self.is_running()
        
        status = {
            "name": "Gateway 服务",
            "type": "websocket",
            "port": self.port,
            "url": f"ws://127.0.0.1:{self.port}",
            "running": running,
            "description": "统一 AI Provider Gateway (6 个 Provider)"
        }
        
        if running:
            # Try to get config info
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        providers = config.get("providers", {})
                        status["provider_count"] = len(providers)
                        status["providers"] = list(providers.keys())
                except:
                    pass
        
        return status


class KnowledgeBaseService:
    """Knowledge Base Web UI Service Manager"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent.parent
        self.app_script = self.workspace / "knowledge_base" / "app.py"
        self.process: Optional[subprocess.Popen] = None
        self.port = 8501
    
    def is_running(self) -> bool:
        """Check if KB Web UI is running"""
        if self.process and self.process.poll() is None:
            return True
        
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', self.port))
        sock.close()
        return result == 0
    
    def start(self) -> Dict[str, any]:
        """Start Knowledge Base Web UI"""
        if self.is_running():
            return {
                "success": False,
                "message": "知识库 Web UI 已在运行中",
                "port": self.port
            }
        
        if not self.app_script.exists():
            return {
                "success": False,
                "message": f"找不到知识库脚本：{self.app_script}"
            }
        
        try:
            # Start Streamlit
            cmd = [sys.executable, "-m", "streamlit", "run", str(self.app_script), "--server.port", str(self.port)]
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.app_script.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            
            return {
                "success": True,
                "message": f"知识库 Web UI 已启动 (http://localhost:{self.port})",
                "port": self.port,
                "url": f"http://localhost:{self.port}",
                "pid": self.process.pid
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"启动失败：{str(e)}"
            }
    
    def stop(self) -> Dict[str, any]:
        """Stop Knowledge Base Web UI"""
        if not self.is_running():
            return {
                "success": False,
                "message": "知识库 Web UI 未运行"
            }
        
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.process = None
            
            return {
                "success": True,
                "message": "知识库 Web UI 已停止"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"停止失败：{str(e)}"
            }
    
    def get_status(self) -> Dict[str, any]:
        """Get Knowledge Base status"""
        running = self.is_running()
        
        return {
            "name": "知识库 Web UI",
            "type": "web",
            "port": self.port,
            "url": f"http://localhost:{self.port}",
            "running": running,
            "description": "知识库管理系统 (ChromaDB + FTS5 双索引)"
        }
