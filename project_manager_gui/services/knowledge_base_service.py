# -*- coding: utf-8 -*-
"""
Knowledge Base Service Manager
Start, stop, and monitor Knowledge Base Streamlit service
"""

import subprocess
import psutil
import socket
from pathlib import Path
from typing import Dict, Optional


class KnowledgeBaseService:
    """Manage Knowledge Base Streamlit service"""
    
    def __init__(self):
        self.port = 8501
        self.process: Optional[subprocess.Popen] = None
        self.workspace_dir = Path(__file__).parent.parent.parent
        self.kb_dir = self.workspace_dir / 'knowledge_base'
    
    def is_port_in_use(self) -> bool:
        """Check if port 8501 is in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', self.port)) == 0
    
    def find_process(self) -> Optional[psutil.Process]:
        """Find the Streamlit process running on port 8501"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info.get('cmdline', []))
                if 'streamlit' in cmdline.lower() and 'knowledge_base' in cmdline.lower():
                    # Check if this process is using port 8501
                    for conn in proc.connections():
                        if conn.laddr.port == self.port:
                            return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def is_running(self) -> bool:
        """Check if Knowledge Base service is running"""
        # Check port
        if self.is_port_in_use():
            return True
        
        # Check process
        proc = self.find_process()
        return proc is not None
    
    def start(self) -> Dict:
        """Start Knowledge Base service"""
        try:
            if self.is_running():
                return {
                    'success': False,
                    'message': 'Knowledge Base is already running',
                    'port': self.port
                }
            
            if not self.kb_dir.exists():
                return {
                    'success': False,
                    'message': f'Knowledge base directory not found: {self.kb_dir}'
                }
            
            # Start Streamlit
            app_path = self.kb_dir / 'app.py'
            if not app_path.exists():
                return {
                    'success': False,
                    'message': f'app.py not found in {self.kb_dir}'
                }
            
            self.process = subprocess.Popen(
                ['streamlit', 'run', str(app_path), '--server.port', str(self.port)],
                cwd=str(self.kb_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            return {
                'success': True,
                'message': f'Knowledge Base started on port {self.port}',
                'port': self.port,
                'pid': self.process.pid
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to start Knowledge Base: {str(e)}'
            }
    
    def stop(self) -> Dict:
        """Stop Knowledge Base service"""
        try:
            # Try to find and kill the process
            proc = self.find_process()
            
            if proc is None:
                # Try to kill by port
                if self.is_port_in_use():
                    for conn in psutil.net_connections(kind='tcp'):
                        if conn.laddr.port == self.port and conn.pid:
                            try:
                                p = psutil.Process(conn.pid)
                                p.terminate()
                                p.wait(timeout=5)
                                return {
                                    'success': True,
                                    'message': 'Knowledge Base stopped'
                                }
                            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                                pass
                
                return {
                    'success': True,
                    'message': 'Knowledge Base was not running'
                }
            
            # Terminate process
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                proc.kill()
            
            return {
                'success': True,
                'message': 'Knowledge Base stopped'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to stop Knowledge Base: {str(e)}'
            }
    
    def get_status(self) -> Dict:
        """Get Knowledge Base service status"""
        running = self.is_running()
        
        status = {
            'name': 'Knowledge Base',
            'type': 'Streamlit Web UI',
            'port': self.port,
            'running': running,
            'url': f'http://localhost:{self.port}' if running else None
        }
        
        if running:
            proc = self.find_process()
            if proc:
                status['pid'] = proc.pid
                try:
                    status['cpu_percent'] = proc.cpu_percent()
                    status['memory_percent'] = proc.memory_percent()
                except:
                    pass
        
        return status
