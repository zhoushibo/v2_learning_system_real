# -*- coding: utf-8 -*-
"""
Diagnostic Panel GUI
Display issues and provide one-click fixes
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from services.diagnostic import SmartDiagnostic


class IssueCard(QFrame):
    """Card displaying a single issue"""
    
    def __init__(self, issue: dict, parent=None):
        super().__init__(parent)
        self.issue = issue
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
        # Color based on severity
        if self.issue['severity'] == 'error':
            color = '#f44336'  # Red
        elif self.issue['severity'] == 'warning':
            color = '#FF9800'  # Orange
        else:
            color = '#2196F3'  # Blue
        
        self.setStyleSheet(f"""
            IssueCard {{
                background-color: white;
                border-left: 5px solid {color};
                border-radius: 8px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title with icon
        icon = "❌" if self.issue['severity'] == 'error' else "⚠️"
        title = QLabel(f"{icon} {self.issue['message']}")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet(f"color: {color};")
        layout.addWidget(title)
        
        # Details
        if self.issue.get('process'):
            proc = self.issue['process']
            details = QLabel(f"占用进程：{proc.get('name', 'Unknown')} (PID: {proc.get('pid', '?')})")
            details.setStyleSheet("color: #666; margin-left: 10px;")
            layout.addWidget(details)
        
        # Fix button
        if self.issue.get('fix_available'):
            fix_layout = QHBoxLayout()
            fix_layout.addStretch()
            
            self.fix_btn = QPushButton("🔧 一键修复")
            self.fix_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.fix_btn.clicked.connect(self.attempt_fix)
            fix_layout.addWidget(self.fix_btn)
            layout.addLayout(fix_layout)
        
        self.setLayout(layout)
    
    def attempt_fix(self):
        """Attempt to fix the issue"""
        diag = SmartDiagnostic()
        
        if self.issue['type'] == 'port_occupied':
            if self.issue.get('process') and self.issue['process'].get('pid'):
                reply = QMessageBox.question(
                    None,
                    '确认结束进程',
                    f"确定要结束进程 {self.issue['process'].get('name', 'Unknown')} (PID: {self.issue['process']['pid']}) 吗？\n\n"
                    "这可能会关闭其他程序。",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    result = diag.fix_issue('kill_process', pid=self.issue['process']['pid'])
                    if result['success']:
                        QMessageBox.information(None, "修复成功", result['message'])
                        # Hide this card
                        self.parent().layout().removeWidget(self)
                        self.hide()
                    else:
                        QMessageBox.critical(None, "修复失败", result['message'])
        
        elif self.issue['type'] == 'missing_dependency':
            if self.issue.get('dependency') == 'streamlit':
                reply = QMessageBox.question(
                    None,
                    '确认安装',
                    "确定要安装 Streamlit 吗？\n\n这可能需要几分钟时间。",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    result = diag.fix_issue('install_dependency', dependency='streamlit')
                    if result['success']:
                        QMessageBox.information(None, "安装成功", result['message'])
                        # Hide this card
                        self.parent().layout().removeWidget(self)
                        self.hide()
                    else:
                        QMessageBox.critical(None, "安装失败", result['message'])


class DiagnosticPanel(QWidget):
    """Main diagnostic panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.diag = SmartDiagnostic()
        self.init_ui()
        self.refresh_diagnostics()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🔍 智能诊断")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2196F3;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("自动检测系统问题并提供一键修复方案")
        desc.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(desc)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 重新检测")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b82d6;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_diagnostics)
        layout.addWidget(self.refresh_btn)
        
        # Issues container
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background-color: #f5f5f5; border-radius: 5px; }")
        
        self.issues_container = QWidget()
        self.issues_layout = QVBoxLayout()
        self.issues_layout.setSpacing(10)
        self.issues_container.setLayout(self.issues_layout)
        
        self.scroll.setWidget(self.issues_container)
        layout.addWidget(self.scroll)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def refresh_diagnostics(self):
        """Refresh diagnostic check"""
        # Clear existing cards
        while self.issues_layout.count():
            item = self.issues_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.status_label.setText("正在检测...")
        
        # Run diagnostics
        results = self.diag.run_full_diagnostic()
        
        # Clear status
        self.status_label.clear()
        
        # Display issues
        if results['issues']:
            for issue in results['issues']:
                card = IssueCard(issue, self.issues_container)
                self.issues_layout.addWidget(card)
            
            self.status_label.setText(f"发现 {len(results['issues'])} 个问题")
        else:
            # No issues - show success message
            success_label = QLabel("✅ 所有检查通过！系统运行正常")
            success_label.setFont(QFont("Arial", 14, QFont.Bold))
            success_label.setStyleSheet("color: #4CAF50;")
            success_label.setAlignment(Qt.AlignCenter)
            self.issues_layout.addWidget(success_label)
            
            # Add some spacing
            self.issues_layout.addStretch()
