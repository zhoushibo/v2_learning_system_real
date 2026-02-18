"""
运行流式响应系统测试
"""
import sys
import os
import subprocess

# 添加src到PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 设置环境变量
os.environ['PYTHONPATH'] = os.path.join(os.path.dirname(__file__), 'src')

# 运行pytest
result = subprocess.run([
    sys.executable, '-m', 'pytest',
    'test_streaming_basic.py', '-v'
], env=os.environ)

sys.exit(result.returncode)
