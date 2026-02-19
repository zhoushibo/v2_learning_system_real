# -*- coding: utf-8 -*-
"""
Service Manager Panel
Quick start/stop for Gateway and Knowledge Base services
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont
import sys
from pathlib import Path

# Add parent path
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.gateway_service import GatewayService, KnowledgeBaseService


class ServiceStatusWorker(QThread):
    """Background worker to check service status"""
    finished = pyqtSignal(dict)
    
    def __init__(self, service):
        super().__init__()
        self.service = service
    
    def run(self):
        status = self.service.get_status()
        self.finished.emit(status)


class ServiceCard(QFrame):
    """Card widget for a service"""
    
    def __init__(self, name: str, description: str, service, parent=None):
        super().__init__(parent)
        self.service = service
        self.name = name
        self.description = description
        self.is_running = False
        self.status_label = None
        self.action_button = None
        self.url_label = None
        
        self.init_ui()
        self.refresh_status()
    
    def init_ui(self):
        """Initialize UI"""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            ServiceCard {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
            ServiceCard:hover {
                background-color: #f0f0f0;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Title
        title = QLabel(self.name)
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel(self.description)
        desc.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(desc)
        
        # Status
        self.status_label = QLabel("● 检查中...")
        self.status_label.setFont(QFont("Arial", 11))
        layout.addWidget(self.status_label)
        
        # URL (if available)
        self.url_label = QLabel("")
        self.url_label.setStyleSheet("color: #0066cc; font-size: 11px;")
        self.url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.url_label)
        
        # Action button
        self.action_button = QPushButton("启动")
        self.action_button.setFixedHeight(35)
        self.action_button.clicked.connect(self.toggle_service)
        layout.addWidget(self.action_button)
        
        self.setLayout(layout)
    
    def refresh_status(self):
        """Refresh service status"""
        self.worker = ServiceStatusWorker(self.service)
        self.worker.finished.connect(self.update_status)
        self.worker.start()
    
    def update_status(self, status: dict):
        """Update UI with status"""
        self.is_running = status.get("running", False)
        
        if self.is_running:
            self.status_label.setText("● 运行中")
            self.status_label.setStyleSheet("color: #28a745;")
            self.action_button.setText("停止")
            self.action_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            
            # Show URL if available
            if "url" in status:
                self.url_label.setText(f"🔗 {status['url']}")
        else:
            self.status_label.setText("● 已停止")
            self.status_label.setStyleSheet("color: #dc3545;")
            self.action_button.setText("启动")
            self.action_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.url_label.setText("")
    
    def toggle_service(self):
        """Start or stop service"""
        self.action_button.setEnabled(False)
        self.action_button.setText("操作中...")
        
        if self.is_running:
            result = self.service.stop()
        else:
            result = self.service.start()
        
        if result.get("success"):
            QMessageBox.information(self, "成功", result["message"])
        else:
            QMessageBox.warning(self, "失败", result["message"])
        
        self.action_button.setEnabled(True)
        self.refresh_status()


class ServiceManagerPanel(QWidget):
    """Service Manager Panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gateway_service = GatewayService()
        self.kb_service = KnowledgeBaseService()
        
        self.init_ui()
        self.refresh_all()
        
        # Auto-refresh every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(5000)
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🔧 服务管理")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        
        # Service cards grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Gateway card
        self.gateway_card = ServiceCard(
            "Gateway 服务",
            "统一 AI Provider Gateway (6 个 Provider)",
            self.gateway_service
        )
        grid.addWidget(self.gateway_card, 0, 0)
        
        # Knowledge Base card
        self.kb_card = ServiceCard(
            "知识库 Web UI",
            "知识库管理系统 (ChromaDB + FTS5)",
            self.kb_service
        )
        grid.addWidget(self.kb_card, 0, 1)
        
        layout.addLayout(grid)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 刷新状态")
        refresh_btn.setFixedHeight(35)
        refresh_btn.clicked.connect(self.refresh_all)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
    
    def refresh_all(self):
        """Refresh all service status"""
        self.gateway_card.refresh_status()
        self.kb_card.refresh_status()
