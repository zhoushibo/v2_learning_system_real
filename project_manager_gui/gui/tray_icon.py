# -*- coding: utf-8 -*-
"""系统托盘图标"""
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication, QStyle
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal


class TrayIcon(QSystemTrayIcon):
    """系统托盘图标"""

    # 信号
    show_window = pyqtSignal()
    quit_app = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置图标（使用PyQt5内置图标）
        # SP_DriveCDIcon 是一个通用的光盘图标，可以用作托盘图标
        style = QApplication.style()
        icon = style.standardIcon(QStyle.SP_DriveCDIcon)
        self.setIcon(icon)
        self.setToolTip("OpenClaw项目管理器")

        # 创建右键菜单
        self._create_menu()

    def _create_menu(self):
        """创建右键菜单"""
        menu = QMenu()

        # 显示窗口
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show_window.emit)
        menu.addAction(show_action)

        menu.addSeparator()

        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_app.emit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def show_message(self, title: str, message: str):
        """
        显示托盘通知

        Args:
            title: 标题
            message: 消息
        """
        self.showMessage(title, message)
