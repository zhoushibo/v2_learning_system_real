# -*- coding: utf-8 -*-
"""
System Tray Integration
Background running, tray notifications, and quick access menu
"""

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QMessageBox, QWidget
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer


class SystemTrayManager:
    """Manage system tray icon and menu"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.tray_icon = None
        self.tray_menu = None
        self.setup_tray()
    
    def create_icon(self, color='#FF9800'):
        """Create a custom tray icon programmatically"""
        # Create a 64x64 pixmap
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        # Create painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw circle
        painter.setBrush(QColor(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        
        # Draw letter "O" (for OpenClaw)
        painter.setPen(QColor('white'))
        font = QFont('Arial', 28, QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, 'O')
        
        painter.end()
        return QIcon(pixmap)
    
    def setup_tray(self):
        """Setup system tray icon and menu"""
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self.main_window)
        self.tray_icon.setIcon(self.create_icon())
        self.tray_icon.setToolTip("OpenClaw Control Center")
        
        # Create tray menu
        self.tray_menu = QMenu()
        
        # Show action
        show_action = QAction("🖥️ 显示主窗口", self.main_window)
        show_action.triggered.connect(self.show_window)
        self.tray_menu.addAction(show_action)
        
        self.tray_menu.addSeparator()
        
        # Quick actions
        quick_start_action = QAction("🚀 快速启动服务", self.main_window)
        quick_start_action.triggered.connect(self.quick_start_services)
        self.tray_menu.addAction(quick_start_action)
        
        stop_all_action = QAction("⏹️ 停止所有服务", self.main_window)
        stop_all_action.triggered.connect(self.stop_all_services)
        self.tray_menu.addAction(stop_all_action)
        
        self.tray_menu.addSeparator()
        
        # Open Knowledge Base
        kb_action = QAction("📚 打开知识库", self.main_window)
        kb_action.triggered.connect(self.open_knowledge_base)
        self.tray_menu.addAction(kb_action)
        
        # Open V2 Learning
        v2_action = QAction("🧠 打开 V2 学习", self.main_window)
        v2_action.triggered.connect(self.open_v2_learning)
        self.tray_menu.addAction(v2_action)
        
        self.tray_menu.addSeparator()
        
        # Minimize to tray action
        minimize_action = QAction("📥 最小化到托盘", self.main_window)
        minimize_action.triggered.connect(self.minimize_to_tray)
        self.tray_menu.addAction(minimize_action)
        
        # Restore action
        restore_action = QAction("📤 从托盘恢复", self.main_window)
        restore_action.triggered.connect(self.show_window)
        self.tray_menu.addAction(restore_action)
        
        self.tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("❌ 退出", self.main_window)
        exit_action.triggered.connect(self.exit_application)
        self.tray_menu.addAction(exit_action)
        
        # Set menu
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # Connect double-click
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Show tray icon
        self.tray_icon.show()
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """Show main window"""
        self.main_window.show()
        self.main_window.activateWindow()
        self.main_window.raise_()
    
    def minimize_to_tray(self):
        """Minimize window to system tray"""
        self.main_window.hide()
        
        # Show notification
        self.tray_icon.showMessage(
            "OpenClaw Control Center",
            "已最小化到系统托盘\n双击托盘图标恢复窗口",
            QSystemTrayIcon.Information,
            2000
        )
    
    def quick_start_services(self):
        """Quick start all services"""
        # Switch to Quick Start tab
        self.main_window.tabs.setCurrentIndex(0)
        self.show_window()
        
        # Trigger quick start
        from gui.quick_start import QuickStartPanel
        quick_start = self.main_window.quick_start
        quick_start.start_services()
    
    def stop_all_services(self):
        """Stop all services"""
        reply = QMessageBox.question(
            self.main_window,
            '确认停止',
            '确定要停止所有服务吗？\n\n• Gateway (端口 8001)\n• 知识库 Web UI (端口 8501)',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from services.gateway_service import GatewayService, KnowledgeBaseService
            
            gateway = GatewayService()
            kb = KnowledgeBaseService()
            
            stopped = []
            
            if gateway.is_running():
                result = gateway.stop()
                if result['success']:
                    stopped.append('Gateway')
            
            if kb.is_running():
                result = kb.stop()
                if result['success']:
                    stopped.append('知识库')
            
            if stopped:
                self.tray_icon.showMessage(
                    "服务已停止",
                    f"已停止：{', '.join(stopped)}",
                    QSystemTrayIcon.Information,
                    2000
                )
            else:
                self.tray_icon.showMessage(
                    "提示",
                    "所有服务已经处于停止状态",
                    QSystemTrayIcon.Information,
                    2000
                )
    
    def open_knowledge_base(self):
        """Open Knowledge Base Web UI"""
        import webbrowser
        webbrowser.open("http://localhost:8501")
        
        # Switch to KB tab
        self.main_window.tabs.setCurrentIndex(1)
        self.show_window()
        
        self.tray_icon.showMessage(
            "知识库",
            "知识库 Web UI 已在浏览器中打开",
            QSystemTrayIcon.Information,
            2000
        )
    
    def open_v2_learning(self):
        """Open V2 Learning panel"""
        # Switch to V2 Learning tab
        self.main_window.tabs.setCurrentIndex(2)
        self.show_window()
        
        self.tray_icon.showMessage(
            "V2 学习",
            "已切换到 V2 学习面板",
            QSystemTrayIcon.Information,
            2000
        )
    
    def exit_application(self):
        """Exit application"""
        reply = QMessageBox.question(
            self.main_window,
            '确认退出',
            '确定要退出 OpenClaw Control Center 吗？\n\n注意：正在运行的服务不会自动停止。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Stop all services first (optional)
            from services.gateway_service import GatewayService, KnowledgeBaseService
            
            gateway = GatewayService()
            kb = KnowledgeBaseService()
            
            if gateway.is_running() or kb.is_running():
                stop_reply = QMessageBox.question(
                    self.main_window,
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
            
            self.tray_icon.hide()
            self.main_window.close()
    
    def show_notification(self, title, message, icon_type=QSystemTrayIcon.Information, duration=2000):
        """Show a tray notification"""
        self.tray_icon.showMessage(title, message, icon_type, duration)
