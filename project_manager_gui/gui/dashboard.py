# -*- coding: utf-8 -*-
"""
Dashboard Module
Global status overview with service cards and quick actions
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
import time


class HealthCheckWorker(QThread):
    """Background worker for health checks (non-blocking)"""
    finished = pyqtSignal(dict)
    
    def __init__(self, health_checker, services_config):
        super().__init__()
        self.health_checker = health_checker
        self.services_config = services_config
    
    def run(self):
        """Run health check in background"""
        results = self.health_checker.check_all_services(self.services_config)
        self.finished.emit(results)


class ServiceCard(QFrame):
    """Card widget displaying service status"""
    
    def __init__(self, name: str, service_type: str, description: str = "", parent=None):
        super().__init__(parent)
        self.name = name
        self.service_type = service_type
        self.description = description
        self.is_healthy = False
        self.response_time = None
        self.error_message = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            ServiceCard {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #ddd;
            }
            ServiceCard.healthy {
                border-color: #4CAF50;
            }
            ServiceCard.unhealthy {
                border-color: #f44336;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        self.title_label = QLabel(self.name)
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        
        # Description
        if self.description:
            self.desc_label = QLabel(self.description)
            self.desc_label.setFont(QFont("Arial", 10))
            self.desc_label.setStyleSheet("color: #555; font-style: italic;")
            self.desc_label.setWordWrap(True)
            layout.addWidget(self.desc_label)
        
        # Type and Port/URL
        type_text = f"Type: {self.service_type.upper()}"
        self.type_label = QLabel(type_text)
        self.type_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.type_label.setStyleSheet("color: #2196F3;")
        layout.addWidget(self.type_label)
        
        # Port or URL (will be updated later)
        self.endpoint_label = QLabel("")
        self.endpoint_label.setFont(QFont("Arial", 9))
        self.endpoint_label.setStyleSheet("color: #FF5722; font-weight: bold;")
        layout.addWidget(self.endpoint_label)
        
        # Status (initial state)
        self.status_label = QLabel("Status: Checking...")
        self.status_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.status_label.setStyleSheet("color: #FF9800;")  # Orange for "checking"
        layout.addWidget(self.status_label)
        
        # Response time / Error
        self.detail_label = QLabel("")
        self.detail_label.setFont(QFont("Arial", 10))
        layout.addWidget(self.detail_label)
        
        # Last checked
        self.time_label = QLabel("")
        self.time_label.setFont(QFont("Arial", 9))
        self.time_label.setStyleSheet("color: #999;")
        layout.addWidget(self.time_label)
        
        self.setLayout(layout)
        self.update_style()
    
    def set_endpoint(self, endpoint_text: str):
        """Set the endpoint (port or URL) display"""
        if hasattr(self, 'endpoint_label'):
            self.endpoint_label.setText(endpoint_text)
    
    def update_status(self, health_status):
        """Update card with health status"""
        self.is_healthy = health_status.is_healthy
        self.response_time = health_status.response_time_ms
        self.error_message = health_status.error_message
        
        # Update status label
        if self.is_healthy:
            self.status_label.setText("Status: Running")
            self.status_label.setStyleSheet("color: #4CAF50;")
        else:
            self.status_label.setText("Status: Stopped")
            self.status_label.setStyleSheet("color: #f44336;")
        
        # Update detail
        if self.response_time:
            self.detail_label.setText(f"Response: {self.response_time}ms")
            self.detail_label.setStyleSheet("color: #2196F3;")
        elif self.error_message:
            self.detail_label.setText(f"Error: {self.error_message}")
            self.detail_label.setStyleSheet("color: #f44336;")
        else:
            self.detail_label.setText("")
        
        # Update time
        self.time_label.setText(f"Checked: {health_status.checked_at}")
        
        self.update_style()
    
    def update_style(self):
        """Update card style based on health"""
        if self.is_healthy:
            self.setProperty("class", "healthy")
        else:
            self.setProperty("class", "unhealthy")
        self.style().unpolish(self)
        self.style().polish(self)


class QuickActions(QWidget):
    """Quick action buttons"""
    
    start_all_signal = pyqtSignal()
    stop_all_signal = pyqtSignal()
    refresh_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # Start All button
        self.start_all_btn = QPushButton("Start All Services")
        self.start_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_all_btn.clicked.connect(self.start_all_signal.emit)
        layout.addWidget(self.start_all_btn)
        
        # Stop All button
        self.stop_all_btn = QPushButton("Stop All Services")
        self.stop_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.stop_all_btn.clicked.connect(self.stop_all_signal.emit)
        layout.addWidget(self.stop_all_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b82d6;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_signal.emit)
        layout.addWidget(self.refresh_btn)
        
        layout.addStretch()
        self.setLayout(layout)


class Dashboard(QWidget):
    """Main dashboard widget"""
    
    def __init__(self, health_checker, parent=None):
        super().__init__(parent)
        self.health_checker = health_checker
        self.service_cards = {}
        self.services_config = {}
        self.worker = None
        
        self.init_ui()
        
        # Auto-refresh timer (every 5 seconds)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(5000)  # 5 seconds
    
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("System Overview")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Quick actions
        self.quick_actions = QuickActions()
        self.quick_actions.refresh_signal.connect(self.refresh_all)
        main_layout.addWidget(self.quick_actions)
        
        # Service cards container
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background-color: #f5f5f5; border-radius: 5px; }")
        
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(15)
        self.cards_container.setLayout(self.cards_layout)
        
        self.scroll.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll)
        
        self.setLayout(main_layout)
    
    def configure_services(self, services: dict):
        """
        Configure services to monitor
        
        Args:
            services: Dict of service configurations
        """
        self.services_config = services
        
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.service_cards = {}
        
        # Create cards for each service
        row = 0
        col = 0
        max_cols = 3  # 3 cards per row
        
        for name, config in services.items():
            service_type = config.get("type", "unknown")
            description = config.get("description", "")
            
            # Extract port or URL for display
            endpoint = ""
            if service_type == "port":
                port = config.get("port")
                host = config.get("host", "127.0.0.1")
                if port:
                    endpoint = f"Port: {host}:{port}"
            elif service_type == "http":
                url = config.get("url", "")
                if url:
                    endpoint = f"URL: {url}"
            
            card = ServiceCard(name, service_type, description)
            
            # Set endpoint text
            if endpoint:
                card.set_endpoint(endpoint)
            
            self.service_cards[name] = card
            
            self.cards_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Add stretch to fill remaining space
        if col > 0:
            for i in range(max_cols - col):
                stretch_widget = QWidget()
                self.cards_layout.addWidget(stretch_widget, row, col + i)
    
    def refresh_all(self):
        """Refresh all service statuses (non-blocking)"""
        if not self.services_config:
            return
        
        # Stop previous worker if still running
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        # Start new worker in background
        self.worker = HealthCheckWorker(self.health_checker, self.services_config)
        self.worker.finished.connect(self._update_cards)
        self.worker.start()
    
    def _update_cards(self, results):
        """Update cards with health check results (called from worker thread)"""
        # Update cards
        for name, status in results.items():
            if name in self.service_cards:
                self.service_cards[name].update_status(status)
        
        # Update window title with summary
        healthy_count = sum(1 for s in results.values() if s.is_healthy)
        total_count = len(results)
        parent = self.parentWidget()
        if parent:
            parent.setWindowTitle(
                f"OpenClaw Control Center - {healthy_count}/{total_count} services running"
            )


# Test function
def main():
    """Test dashboard"""
    import sys
    from PyQt5.QtWidgets import QApplication
    from core.health_checker import HealthChecker
    
    app = QApplication(sys.argv)
    
    # Create health checker
    checker = HealthChecker()
    
    # Define services
    services = {
        "Gateway": {"type": "port", "host": "127.0.0.1", "port": 8001},
        "Knowledge Base": {"type": "http", "url": "http://localhost:8501"},
        "V2 Learning": {"type": "process", "pid": 12345}  # Fake PID for testing
    }
    
    # Create dashboard
    dashboard = Dashboard(checker)
    dashboard.configure_services(services)
    dashboard.resize(900, 600)
    dashboard.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
