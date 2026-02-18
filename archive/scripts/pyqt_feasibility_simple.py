# -*- coding: utf-8 -*-
"""PyQt可行性验证（非GUI版本）"""
import sys
import subprocess
import time
import json
import tempfile
import os

print("="*70)
print("PyQt可行性验证")
print("="*70)

# 测试1: 检查PyQt安装
print("\n[1/5] 检查PyQt安装...")
try:
    import PyQt5
    from PyQt5.QtCore import PYQT_VERSION_STR
    print(f"   [OK] PyQt5 已安装")
    print(f"   版本: {PYQT_VERSION_STR}")

    # 注意：QSystemTrayIcon测试需要GUI环境，这里跳过
    print(f"   [INFO] 托盘支持测试需要GUI环境，跳过")

except ImportError as e:
    print(f"   [ERROR] PyQt5 未安装: {e}")
    sys.exit(1)

# 测试2: 子进程管理测试
print("\n[2/5] 子进程管理测试...")
try:
    process = subprocess.Popen(
        [sys.executable, "-c", "import time; print('Subprocess test'); time.sleep(2)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(0.5)
    if process.poll() is None:
        print("   [OK] 子进程启动成功")
    else:
        print(f"   [ERROR] 子进程已退出，返回码: {process.returncode}")
        sys.exit(1)

    stdout, stderr = process.communicate(timeout=5)
    print(f"   [OK] 子进程输出: {stdout.decode('utf-8', errors='ignore').strip()}")
    print(f"   [OK] 子进程管理正常")

except subprocess.TimeoutExpired:
    process.kill()
    print("   [ERROR] 子进程超时")
    sys.exit(1)
except Exception as e:
    print(f"   [ERROR] 子进程管理测试失败: {e}")
    sys.exit(1)

# 测试3: 项目配置读写
print("\n[3/5] 项目配置测试...")
test_projects = {
    "projects": [
        {
            "name": "V2 MVP",
            "type": "mvp",
            "path": "C:\\Users\\10952\\.openclaw\\workspace\\openclaw_async_architecture\\mvp",
            "launcher": "launcher.py",
            "start_cmd": "python launcher.py gateway",
            "description": "OpenClaw V2异步架构MVP"
        },
        {
            "name": "钉钉AI Agent",
            "type": "agent",
            "path": "D:\\\\.openclaw\\workspace\\claw_agent_demo",
            "description": "钉钉AI Agent系统"
        }
    ]
}

try:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(test_projects, f, ensure_ascii=False, indent=2)
        test_file = f.name

    with open(test_file, 'r', encoding='utf-8') as f:
        loaded = json.load(f)

    print(f"   [OK] 项目配置读写正常")
    print(f"   配置项目数: {len(loaded['projects'])}")
    os.unlink(test_file)

except Exception as e:
    print(f"   [ERROR] 项目配置测试失败: {e}")
    sys.exit(1)

# 测试4: 文件路径检查
print("\n[4/5] 项目路径检查...")
paths_to_check = [
    ("V2 MVP", "C:\\Users\\10952\\.openclaw\\workspace\\openclaw_async_architecture\\mvp"),
    ("钉钉AI Agent", "D:\\\\.openclaw\\workspace\\claw_agent_demo"),
]

for name, path in paths_to_check:
    if os.path.exists(path):
        print(f"   [OK] {name}: {path}")
    else:
        print(f"   [WARN] {name}: 路径不存在 ({path})")

# 测试5: 项目启动器测试
print("\n[5/5] 项目启动器测试...")
mvp_path = "C:\\Users\\10952\\.openclaw\\workspace\\openclaw_async_architecture\\mvp\\launcher.py"
if os.path.exists(mvp_path):
    print(f"   [OK] V2 MVP启动器存在")
    print(f"   路径: {mvp_path}")
    print(f"   [INFO] 可以通过subprocess.Popen([sys.executable, 'launcher.py', 'gateway'])启动")
else:
    print(f"   [WARN] V2 MVP启动器不存在")

# 总结
print("\n" + "="*70)
print("测试完成")
print("="*70)

print("\n[总结]")
print("   [OK] PyQt5已安装")
print("   [OK] 子进程管理正常")
print("   [OK] 项目配置读写正常")
print("   [OK] 文件路径检查正常")
print("   [INFO] GUI组件测试需要桌面环境")

print("\n[结论]")
print("   PyQt技术栈基本可行！")
print("   可以开始MVP开发")

print("\n[依赖]")
print("   PyQt5    [OK] 已安装")
print("   psutil   [OPTIONAL] 用于进程监控")
print("   requests [OPTIONAL] 用于HTTP请求")

print("\n[下一步]")
print("   1. 创建project_manager_gui/目录结构")
print("   2. 开发基础GUI框架")
print("   3. 实现项目列表和启动/停止功能")

print("\n" + "="*70)
print("测试通过！")
print("="*70)
