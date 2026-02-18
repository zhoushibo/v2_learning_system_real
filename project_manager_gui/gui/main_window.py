# -*- coding: utf-8 -*-
"""主窗口"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QTextEdit,
                             QStatusBar, QTabWidget)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from .tray_icon import TrayIcon
from .project_list import ProjectList
from .task_submit_widget import TaskSubmitWidget
from core import ProjectManager


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__(parent)

        self.project_manager = project_manager

        self._setup_ui()
        self._setup_tray_icon()
        self._connect_signals()

        # 定时器用于更新状态
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_status)
        self.timer.start(1000)  # 每秒更新

    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("OpenClaw项目管理器")
        self.resize(900, 700)

        # 中心部件
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Tab窗口
        self.tab_widget = QTabWidget()

        # Tab 1: 项目管理
        self.project_list = ProjectList()
        projects = self.project_manager.get_all_projects()
        self.project_list.update_projects(projects)

        project_tab = QWidget()
        project_layout = QVBoxLayout()
        project_layout.addWidget(self.project_list)
        project_layout.addWidget(QLabel("<b>日志输出：</b>"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        font = QFont("Consolas", 9)
        self.log_text.setFont(font)
        project_layout.addWidget(self.log_text)
        project_tab.setLayout(project_layout)

        self.tab_widget.addTab(project_tab, "项目管理")

        # Tab 2: 任务提交
        self.task_submit_widget = TaskSubmitWidget()
        self.tab_widget.addTab(self.task_submit_widget, "任务提交")

        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()

    def _setup_tray_icon(self):
        """设置托盘图标"""
        self.tray_icon = TrayIcon()
        self.tray_icon.show()

        # 信号连接
        self.tray_icon.show_window.connect(self.show)
        self.tray_icon.quit_app.connect(self.close)

    def _connect_signals(self):
        """连接信号"""
        # 项目列表信号
        self.project_list.start_component.connect(self._on_start_component)
        self.project_list.stop_component.connect(self._on_stop_component)

        # 任务提交信号
        self.task_submit_widget.task_submitted.connect(self._on_task_submitted)

    def _on_start_component(self, project_id: str, component_id: str):
        """启动组件"""
        self._log(f"启动 {project_id}/{component_id}...")

        success = self.project_manager.start_component(project_id, component_id)

        if success:
            self._log(f"启动成功")
            self.tray_icon.show_message("启动成功", f"{project_id}/{component_id}已启动")
        else:
            self._log(f"启动失败")

    def _on_stop_component(self, project_id: str, component_id: str):
        """停止组件"""
        self._log(f"停止 {project_id}/{component_id}...")

        success = self.project_manager.stop_component(project_id, component_id)

        if success:
            self._log(f"停止成功")
            self.tray_icon.show_message("停止成功", f"{project_id}/{component_id}已停止")
        else:
            self._log(f"停止失败")

    def _on_task_submitted(self, task_id: str):
        """任务已提交"""
        self._log(f"任务已提交: {task_id}")
        if self.tab_widget.currentIndex() == 0:
            # 在项目管理Tab，可以提示用户切换到任务提交Tab查看结果
            pass

    def _update_status(self):
        """更新状态"""
        # 更新状态栏
        self._update_status_bar()

        # 可以在这里添加更多状态更新逻辑
        # 例如：检查组件健康状态、更新按钮状态等

    def _update_status_bar(self):
        """更新状态栏"""
        all_processes = self.project_manager.process_manager.get_all_processes()
        running_count = sum(1 for p in all_processes if p['is_running'])

        self.status_bar.showMessage(f"运行中: {running_count} 个进程")

    def _log(self, message: str):
        """
        记录日志

        Args:
            message: 日志消息
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def closeEvent(self, event):
        """关闭事件"""
        # 先停止所有进程
        self.project_manager.cleanup()

        # 停止任务轮询
        self.task_submit_widget.stop_polling()

        # 接受关闭事件
        event.accept()

    def show(self):
        """显示窗口"""
        super().show()
        self._log("欢迎使用OpenClaw项目管理器")
