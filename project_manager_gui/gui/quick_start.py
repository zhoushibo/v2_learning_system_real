# -*- coding: utf-8 -*-
"""
Quick Start Panel - One-click development environment startup
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont
import time

from services.gateway_service import GatewayService, KnowledgeBaseService


class StartupWorker(QThread):
    """Background worker for starting services"""
    progress = pyqtSignal(int, str)  # progress_percent, status_text
    finished = pyqtSignal(bool, str)  # success, message
    log = pyqtSignal(str)  # log_line
    
    def __init__(self):
        super().__init__()
        self.gateway = GatewayService()
        self.kb = KnowledgeBaseService()
    
    def run(self):
        """Start services in sequence"""
        try:
            total_steps = 4
            current_step = 0
            
            # Step 1: Check current status
            current_step += 1
            self.progress.emit(int(100 * current_step / total_steps), "检查当前状态...")
            self.log.emit("[INFO] 开始检查服务状态")
            time.sleep(0.5)
            
            # Step 2: Start Gateway
            current_step += 1
            self.progress.emit(int(100 * current_step / total_steps), "启动 Gateway 服务...")
            self.log.emit("[INFO] 正在启动 Gateway 服务 (端口 8001)")
            
            if not self.gateway.is_running():
                result = self.gateway.start()
                if result['success']:
                    self.log.emit(f"[SUCCESS] Gateway 启动成功：{result['message']}")
                else:
                    self.log.emit(f"[ERROR] Gateway 启动失败：{result['message']}")
                    self.finished.emit(False, f"Gateway 启动失败：{result['message']}")
                    return
            else:
                self.log.emit("[INFO] Gateway 已在运行中")
            
            time.sleep(1)  # Wait for Gateway to fully start
            
            # Step 3: Start Knowledge Base
            current_step += 1
            self.progress.emit(int(100 * current_step / total_steps), "启动知识库 Web UI...")
            self.log.emit("[INFO] 正在启动知识库 Web UI (端口 8501)")
            
            if not self.kb.is_running():
                result = self.kb.start()
                if result['success']:
                    self.log.emit(f"[SUCCESS] 知识库启动成功：{result['message']}")
                else:
                    self.log.emit(f"[ERROR] 知识库启动失败：{result['message']}")
                    self.finished.emit(False, f"知识库启动失败：{result['message']}")
                    return
            else:
                self.log.emit("[INFO] 知识库已在运行中")
            
            time.sleep(2)  # Wait for Streamlit to fully start
            
            # Step 4: Final check
            current_step += 1
            self.progress.emit(100, "完成启动")
            self.log.emit("[INFO] 所有服务启动完成")
            
            # Verify both services are running
            gateway_running = self.gateway.is_running()
            kb_running = self.kb.is_running()
            
            if gateway_running and kb_running:
                self.finished.emit(True, "开发环境启动成功！\n\n• Gateway: ws://127.0.0.1:8001\n• 知识库：http://localhost:8501")
            else:
                errors = []
                if not gateway_running:
                    errors.append("Gateway 未运行")
                if not kb_running:
                    errors.append("知识库未运行")
                self.finished.emit(False, "部分服务启动失败：\n" + "\n".join(errors))
                
        except Exception as e:
            self.log.emit(f"[ERROR] 启动过程异常：{str(e)}")
            self.finished.emit(False, f"启动过程异常：{str(e)}")


class QuickStartPanel(QWidget):
    """Quick start panel with big button"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🚀 一键启动开发环境")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2196F3; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("自动按顺序启动 Gateway 和知识库服务\n无需手动操作，一键搞定！")
        desc.setFont(QFont("Arial", 12))
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(desc)
        
        # Big start button
        self.start_btn = QPushButton("🚀 启动开发环境")
        self.start_btn.setFont(QFont("Arial", 18, QFont.Bold))
        self.start_btn.setFixedHeight(80)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.start_btn.clicked.connect(self.start_services)
        layout.addWidget(self.start_btn)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p% - 准备就绪")
        self.progress.setFixedHeight(30)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        layout.addWidget(self.progress)
        
        # Status label
        self.status_label = QLabel("准备就绪")
        self.status_label.setFont(QFont("Arial", 11))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)
        
        # Log area (collapsible)
        self.log_label = QLabel("查看日志")
        self.log_label.setFont(QFont("Arial", 10))
        self.log_label.setAlignment(Qt.AlignCenter)
        self.log_label.setStyleSheet("color: #2196F3; text-decoration: underline;")
        self.log_label.mousePressEvent = self.toggle_log
        layout.addWidget(self.log_label)
        
        self.log_text = QLabel("")
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.log_text.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                color: #333;
            }
        """)
        self.log_text.setWordWrap(True)
        self.log_text.hide()  # Hidden by default
        layout.addWidget(self.log_text)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def start_services(self):
        """Start all services"""
        # Disable button during startup
        self.start_btn.setEnabled(False)
        self.start_btn.setText("启动中...")
        self.progress.setValue(0)
        self.status_label.setText("正在启动服务...")
        self.log_text.clear()
        
        # Create and start worker
        self.worker = StartupWorker()
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.log.connect(self.on_log)
        self.worker.start()
    
    def on_progress(self, percent, status):
        """Update progress"""
        self.progress.setValue(percent)
        self.status_label.setText(status)
        self.progress.setFormat(f"{percent}% - {status}")
    
    def on_finished(self, success, message):
        """Startup finished"""
        self.start_btn.setEnabled(True)
        self.start_btn.setText("🚀 启动开发环境")
        
        if success:
            self.status_label.setText("✅ 启动成功！")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            QMessageBox.information(self, "启动成功", message)
        else:
            self.status_label.setText("❌ 启动失败")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            QMessageBox.critical(self, "启动失败", message)
    
    def on_log(self, line):
        """Add log line"""
        current = self.log_text.text()
        self.log_text.setText(current + line + "\n")
    
    def toggle_log(self, event):
        """Toggle log visibility"""
        if self.log_text.isVisible():
            self.log_text.hide()
            self.log_label.setText("查看日志")
        else:
            self.log_text.show()
            self.log_label.setText("隐藏日志")
