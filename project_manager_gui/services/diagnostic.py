# -*- coding: utf-8 -*-
"""
Smart Diagnostic System
Auto-detect issues and provide one-click fixes
"""

import subprocess
import socket
import sys
import os
from typing import Dict, List, Optional
from pathlib import Path


class PortDiagnostic:
    """Port occupancy diagnostic"""
    
    @staticmethod
    def is_port_in_use(port: int) -> bool:
        """Check if port is in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return False
            except OSError:
                return True
    
    @staticmethod
    def get_process_using_port(port: int) -> Optional[Dict]:
        """
        Get process information using the specified port
        
        Returns:
            Dict with pid, name, exe or None if not found
        """
        try:
            # Use netstat to find PID
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            # Get process name
                            proc_result = subprocess.run(
                                ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV'],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            
                            proc_lines = proc_result.stdout.strip().split('\n')
                            if len(proc_lines) >= 2:
                                # Parse CSV output
                                proc_info = proc_lines[1].strip('"').split('","')
                                return {
                                    'pid': pid,
                                    'name': proc_info[0] if len(proc_info) > 0 else 'Unknown',
                                    'exe': proc_info[1] if len(proc_info) > 1 else 'Unknown'
                                }
                        except Exception as e:
                            return {'pid': pid, 'name': 'Unknown', 'error': str(e)}
            
            return None
        except Exception as e:
            return None
    
    @staticmethod
    def kill_process(pid: str) -> Dict:
        """
        Kill process by PID
        
        Returns:
            Dict with success and message
        """
        try:
            result = subprocess.run(
                ['taskkill', '/F', '/PID', pid],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'成功结束进程 {pid}',
                    'output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'message': f'结束进程失败：{result.stderr}',
                    'output': result.stderr
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'异常：{str(e)}'
            }


class DependencyDiagnostic:
    """Dependency check diagnostic"""
    
    @staticmethod
    def check_streamlit() -> Dict:
        """Check if Streamlit is installed"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'streamlit', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                return {
                    'installed': True,
                    'version': version,
                    'message': f'Streamlit 已安装：{version}'
                }
            else:
                return {
                    'installed': False,
                    'message': 'Streamlit 未安装'
                }
        except Exception as e:
            return {
                'installed': False,
                'message': f'检测失败：{str(e)}'
            }
    
    @staticmethod
    def install_streamlit() -> Dict:
        """Install Streamlit"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'streamlit', '-q'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Streamlit 安装成功'
                }
            else:
                return {
                    'success': False,
                    'message': f'安装失败：{result.stderr}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'异常：{str(e)}'
            }


class ConfigDiagnostic:
    """Configuration file diagnostic"""
    
    @staticmethod
    def check_gateway_config() -> Dict:
        """Check Gateway configuration file"""
        # Try to find API_CONFIG_FINAL.json
        possible_paths = [
            Path(__file__).parent.parent.parent / 'openclaw_async_architecture' / 'API_CONFIG_FINAL.json',
            Path(__file__).parent.parent.parent.parent / 'openclaw_async_architecture' / 'API_CONFIG_FINAL.json',
        ]
        
        for config_path in possible_paths:
            if config_path.exists():
                return {
                    'exists': True,
                    'path': str(config_path),
                    'message': f'配置文件存在：{config_path}'
                }
        
        return {
            'exists': False,
            'message': '未找到 Gateway 配置文件 (API_CONFIG_FINAL.json)'
        }
    
    @staticmethod
    def check_state_file() -> Dict:
        """Check STATE.json file"""
        state_path = Path(__file__).parent.parent.parent / 'STATE.json'
        
        if state_path.exists():
            try:
                import json
                with open(state_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                return {
                    'exists': True,
                    'valid': True,
                    'path': str(state_path),
                    'projects_count': len(data.get('projects', {})),
                    'message': f'STATE.json 有效，包含 {len(data.get("projects", {}))} 个项目'
                }
            except Exception as e:
                return {
                    'exists': True,
                    'valid': False,
                    'path': str(state_path),
                    'message': f'STATE.json 无效：{str(e)}'
                }
        else:
            return {
                'exists': False,
                'message': '未找到 STATE.json 文件'
            }


class SmartDiagnostic:
    """Main diagnostic system"""
    
    def __init__(self):
        self.port_diag = PortDiagnostic()
        self.dep_diag = DependencyDiagnostic()
        self.config_diag = ConfigDiagnostic()
    
    def run_full_diagnostic(self) -> Dict:
        """
        Run full diagnostic check
        
        Returns:
            Dict with all diagnostic results
        """
        results = {
            'ports': {},
            'dependencies': {},
            'config': {},
            'issues': [],
            'suggestions': []
        }
        
        # Check ports
        for port_name, port_num in [('Gateway', 8001), ('Knowledge Base', 8501)]:
            in_use = self.port_diag.is_port_in_use(port_num)
            proc_info = self.port_diag.get_process_using_port(port_num) if in_use else None
            
            results['ports'][port_name] = {
                'port': port_num,
                'in_use': in_use,
                'process': proc_info
            }
            
            if in_use:
                results['issues'].append({
                    'type': 'port_occupied',
                    'severity': 'warning',
                    'service': port_name,
                    'port': port_num,
                    'process': proc_info,
                    'message': f'{port_name} 端口 {port_num} 被占用',
                    'fix_available': True
                })
        
        # Check dependencies
        streamlit_status = self.dep_diag.check_streamlit()
        results['dependencies']['streamlit'] = streamlit_status
        
        if not streamlit_status['installed']:
            results['issues'].append({
                'type': 'missing_dependency',
                'severity': 'error',
                'dependency': 'streamlit',
                'message': 'Streamlit 未安装，知识库 Web UI 无法启动',
                'fix_available': True
            })
        
        # Check config files
        gateway_config = self.config_diag.check_gateway_config()
        results['config']['gateway'] = gateway_config
        
        if not gateway_config['exists']:
            results['issues'].append({
                'type': 'missing_config',
                'severity': 'warning',
                'config': 'Gateway',
                'message': 'Gateway 配置文件未找到',
                'fix_available': False
            })
        
        state_config = self.config_diag.check_state_file()
        results['config']['state'] = state_config
        
        if not state_config['exists']:
            results['issues'].append({
                'type': 'missing_config',
                'severity': 'warning',
                'config': 'STATE',
                'message': 'STATE.json 未找到',
                'fix_available': False
            })
        
        # Generate suggestions
        for issue in results['issues']:
            if issue['type'] == 'port_occupied':
                results['suggestions'].append({
                    'issue': issue,
                    'actions': [
                        {
                            'name': '结束占用进程',
                            'action': 'kill_process',
                            'pid': issue['process']['pid'] if issue['process'] else None
                        },
                        {
                            'name': '修改服务端口',
                            'action': 'change_port',
                            'current_port': issue['port']
                        }
                    ]
                })
            elif issue['type'] == 'missing_dependency':
                results['suggestions'].append({
                    'issue': issue,
                    'actions': [
                        {
                            'name': '一键安装',
                            'action': 'install_dependency',
                            'dependency': issue['dependency']
                        }
                    ]
                })
        
        return results
    
    def fix_issue(self, issue_type: str, **kwargs) -> Dict:
        """
        Attempt to fix a specific issue
        
        Args:
            issue_type: Type of issue to fix
            **kwargs: Additional parameters
            
        Returns:
            Dict with success and message
        """
        if issue_type == 'kill_process':
            pid = kwargs.get('pid')
            if not pid:
                return {'success': False, 'message': '缺少进程 ID'}
            return self.port_diag.kill_process(pid)
        
        elif issue_type == 'install_dependency':
            dep = kwargs.get('dependency')
            if dep == 'streamlit':
                return self.dep_diag.install_streamlit()
            return {'success': False, 'message': f'不支持的依赖：{dep}'}
        
        elif issue_type == 'change_port':
            # TODO: Implement port change in config
            return {
                'success': False,
                'message': '修改端口功能开发中'
            }
        
        return {
            'success': False,
            'message': f'未知的修复类型：{issue_type}'
        }


# Test function
def main():
    """Test diagnostic system"""
    print("=" * 80)
    print("Smart Diagnostic System Test")
    print("=" * 80)
    
    diag = SmartDiagnostic()
    results = diag.run_full_diagnostic()
    
    print("\n=== Port Status ===")
    for name, info in results['ports'].items():
        status = "In Use" if info['in_use'] else "Available"
        print(f"{name} (Port {info['port']}): {status}")
        if info['process']:
            print(f"  Process: {info['process']['name']} (PID: {info['process']['pid']})")
    
    print("\n=== Dependencies ===")
    for name, info in results['dependencies'].items():
        status = "Installed" if info.get('installed') else "Not Installed"
        print(f"{name}: {status}")
        if 'version' in info:
            print(f"  Version: {info['version']}")
        print(f"  Message: {info['message']}")
    
    print("\n=== Configuration ===")
    for name, info in results['config'].items():
        status = "Found" if info.get('exists') else "Not Found"
        print(f"{name} Config: {status}")
        if 'valid' in info:
            validity = "Valid" if info['valid'] else "Invalid"
            print(f"  Validity: {validity}")
        print(f"  Message: {info['message']}")
    
    print("\n=== Issues Found ===")
    if results['issues']:
        for i, issue in enumerate(results['issues'], 1):
            print(f"{i}. [{issue['severity'].upper()}] {issue['message']}")
            if issue.get('fix_available'):
                print(f"   Fix available: Yes")
    else:
        print("No issues found!")
    
    print("\n=== Suggestions ===")
    if results['suggestions']:
        for sug in results['suggestions']:
            print(f"Issue: {sug['issue']['message']}")
            print("  Actions:")
            for action in sug['actions']:
                print(f"    - {action['name']}")
    else:
        print("No suggestions.")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
