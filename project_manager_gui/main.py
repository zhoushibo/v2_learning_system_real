# -*- coding: utf-8 -*-
"""OpenClaw项目管理器 - 主入口"""
import sys
import os

# Windows编码修复
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from core import ProjectManager


def main():
    """主函数"""
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("OpenClaw项目管理器")

    # 创建项目管理器
    config_path = os.path.join(os.path.dirname(__file__), "config", "projects.json")
    project_manager = ProjectManager(config_path)

    # 创建主窗口
    window = MainWindow(project_manager)
    window.show()

    # 运行应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
