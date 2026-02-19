# -*- coding: utf-8 -*-
"""
Main Window v3 - With Service Manager
OpenClaw Control Center
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QStatusBar, QLabel, QMessageBox, QMenuBar, QMenu
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from .dashboard import Dashboard
from .project_list import ProjectList
from .service_manager import ServiceManagerPanel
from .quick_start import QuickStartPanel
from .diagnostic_panel import DiagnosticPanel
from .knowledge_base_panel import KnowledgeBasePanel
from .v2_learning_panel import V2LearningPanel
from .system_tray import SystemTrayManager
from .config_editor import ConfigEditorPanel
from .themes import ThemeManager
from core.health_checker import HealthChecker
from core.project_manager import ProjectManager
from core.state_reader import get_projects_with_completion


class MainWindow(QMainWindow):
    """Main window with dashboard, projects, and service manager"""
    
    def __init__(self, project_manager: ProjectManager):
        super().__init__()
        self.project_manager = project_manager
        self.health_checker = HealthChecker()
        
        self.init_ui()
        self.configure_services()
    
    def create_menu_bar(self):
        """Create menu bar with theme switcher"""
        menubar = self.menuBar()
        
        # View menu
        view_menu = menubar.addMenu("视图 (&V)")
        
        # Theme submenu
        theme_menu = view_menu.addMenu("切换主题 (&T)")
        
        # Theme actions
        current_theme = 'dark'
        
        for theme_name in ThemeManager.get_theme_names():
            display_name = ThemeManager.get_theme_display_name(theme_name)
            action = theme_menu.addAction(display_name)
            action.triggered.connect(lambda checked, name=theme_name: self.on_theme_changed(name))
        
        # Help menu
        help_menu = menubar.addMenu("帮助 (&H)")
        about_action = help_menu.addAction("关于 (&A)")
        about_action.triggered.connect(self.show_about)
    
    def on_theme_changed(self, theme_name: str):
        """Handle theme change"""
        self.switch_theme(theme_name)
        display_name = ThemeManager.get_theme_display_name(theme_name)
        self.statusBar.showMessage(f"就绪 | Gateway:8001 | 知识库:8501 | 主题：{display_name}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "关于 OpenClaw Control Center",
            "OpenClaw Control Center v3.1\n\n"
            "一站式 AI 开发环境管理工具\n\n"
            "功能特性：\n"
            "• 一键启动开发环境\n"
            "• 服务状态实时监控\n"
            "• 智能诊断与一键修复\n"
            "• 项目进度管理\n"
            "• 三套主题可选\n\n"
            "© 2026 OpenClaw Project"
        )
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("OpenClaw Control Center")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply default theme (Dark)
        self.apply_theme('dark')
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 0;
            }
            QTabBar::tab {
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #f5f5f5;
            }
        """)
        
        # Quick Start tab (NEW - P0 feature)
        self.quick_start = QuickStartPanel()
        self.tabs.addTab(self.quick_start, "🚀 快速启动")
        
        # Knowledge Base tab (NEW - P1 feature)
        self.knowledge_base = KnowledgeBasePanel()
        self.tabs.addTab(self.knowledge_base, "📚 知识库")
        
        # V2 Learning tab (NEW - P1 feature)
        self.v2_learning = V2LearningPanel()
        self.tabs.addTab(self.v2_learning, "🧠 V2 学习")
        
        # Config Editor tab (NEW - P1 feature)
        self.config_editor = ConfigEditorPanel()
        self.tabs.addTab(self.config_editor, "⚙️ 配置")
        
        # Diagnostic tab (NEW - P0 feature)
        self.diagnostic = DiagnosticPanel()
        self.tabs.addTab(self.diagnostic, "🔍 智能诊断")
        
        # Dashboard tab
        self.dashboard = Dashboard(self.health_checker)
        # Configure default services for dashboard
        default_services = {
            "Gateway": {
                "type": "websocket",
                "port": 8001,
                "url": "ws://127.0.0.1:8001",
                "description": "统一 AI Provider Gateway (6 个 Provider)"
            },
            "Knowledge Base": {
                "type": "web",
                "port": 8501,
                "url": "http://localhost:8501",
                "description": "知识库管理系统 (ChromaDB + FTS5)"
            },
            "V2 Learning": {
                "type": "module",
                "port": None,
                "url": None,
                "description": "V2 学习系统 (3 Worker 并发)"
            }
        }
        self.dashboard.configure_services(default_services)
        self.tabs.addTab(self.dashboard, "📊 仪表盘")
        
        # Service Manager tab
        self.service_manager = ServiceManagerPanel()
        self.tabs.addTab(self.service_manager, "🔧 服务管理")
        
        # Project Management tab
        self.project_list = ProjectList()
        self.project_list.project_manager = self.project_manager
        
        # Load projects from STATE.json with completion data
        projects = get_projects_with_completion()
        self.project_list.update_projects(projects)
        self.tabs.addTab(self.project_list, "📁 项目管理")
        
        main_layout.addWidget(self.tabs)
        
        # Menu bar
        self.create_menu_bar()
        
        # System tray
        self.tray_manager = SystemTrayManager(self)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪 | Gateway:8001 | 知识库:8501 | 主题：深色 | 托盘：已启用")
    
    def configure_services(self):
        """Configure services"""
        self.statusBar.showMessage("正在初始化服务...")
        
        # Check if services are running
        QTimer.singleShot(1000, self.check_initial_status)
    
    def check_initial_status(self):
        """Check initial service status"""
        from services.gateway_service import GatewayService, KnowledgeBaseService
        
        gateway = GatewayService()
        kb = KnowledgeBaseService()
        
        running_services = []
        if gateway.is_running():
            running_services.append("Gateway")
        if kb.is_running():
            running_services.append("知识库 Web UI")
        
        if running_services:
            msg = f"已运行：{', '.join(running_services)}"
        else:
            msg = "就绪 | 所有服务已停止"
        
        self.statusBar.showMessage(msg)
        
        # Show welcome message if no services running
        if not running_services:
            QMessageBox.information(
                self,
                "欢迎",
                "欢迎使用 OpenClaw Control Center！\n\n"
                "切换到「服务管理」标签页启动服务：\n"
                "• Gateway 服务 (端口 8001)\n"
                "• 知识库 Web UI (端口 8501)\n\n"
                "或者在「仪表盘」查看系统状态。"
            )
    
    def closeEvent(self, event):
        """Handle window close"""
        # Check if we should minimize to tray instead
        if hasattr(self, 'tray_manager') and self.tray_manager.tray_icon.isVisible():
            # Ask user
            reply = QMessageBox.question(
                self,
                '最小化到托盘',
                "确定要退出程序吗？\n\n点击「是」退出程序\n点击「否」最小化到托盘",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                # Minimize to tray instead
                self.tray_manager.minimize_to_tray()
                event.ignore()
                return
        
        # Proceed with exit
        reply = QMessageBox.question(
            self,
            '确认退出',
            "确定要关闭 OpenClaw Control Center 吗？\n\n"
            "注意：正在运行的服务不会自动停止。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Stop services if running
            from services.gateway_service import GatewayService, KnowledgeBaseService
            
            gateway = GatewayService()
            kb = KnowledgeBaseService()
            
            if gateway.is_running() or kb.is_running():
                stop_reply = QMessageBox.question(
                    self,
                    '停止服务',
                    '检测到有服务正在运行，要在退出前停止所有服务吗？',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if stop_reply == QMessageBox.Yes:
                    if gateway.is_running():
                        gateway.stop()
                    if kb.is_running():
                        kb.stop()
            
            event.accept()
        else:
            event.ignore()
    
    def changeEvent(self, event):
        """Handle window state change"""
        if event.type() == event.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                # Minimize to tray when minimized
                if hasattr(self, 'tray_manager'):
                    self.tray_manager.minimize_to_tray()
        super().changeEvent(event)
    
    def apply_theme(self, theme_name: str):
        """Apply a theme to the application"""
        from PyQt5.QtWidgets import QApplication
        stylesheet = ThemeManager.get_theme_stylesheet(theme_name)
        QApplication.instance().setStyleSheet(stylesheet)
    
    def switch_theme(self, theme_name: str):
        """Switch to a different theme"""
        self.apply_theme(theme_name)
        # Refresh all widgets
        self.update()
