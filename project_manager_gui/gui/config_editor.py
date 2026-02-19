# -*- coding: utf-8 -*-
"""
Configuration Editor
GUI for managing projects and settings
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QScrollArea, QFrame, QMessageBox,
    QFileDialog, QComboBox, QSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import json
from pathlib import Path
from datetime import datetime


class ProjectEditorCard(QFrame):
    """Card for editing a single project"""
    
    def __init__(self, project: dict, parent=None):
        super().__init__(parent)
        self.project = project
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            ProjectEditorCard {
                background-color: white;
                border: 2px solid #2196F3;
                border-radius: 8px;
                margin: 5px;
            }
            ProjectEditorCard:hover {
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_layout = QHBoxLayout()
        
        title_label = QLabel(f"📁 {self.project.get('name', 'Unnamed Project')}")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2196F3;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Status badge
        status = self.project.get('status', 'Unknown')
        status_color = '#4CAF50' if '完成' in status or 'Complete' in status else '#FF9800'
        status_label = QLabel(f"● {status}")
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        title_layout.addWidget(status_label)
        
        layout.addLayout(title_layout)
        
        # Completion
        completion_layout = QHBoxLayout()
        completion_layout.addWidget(QLabel("完成度:"))
        
        self.completion_spin = QSpinBox()
        self.completion_spin.setRange(0, 100)
        self.completion_spin.setValue(self.project.get('completion', 0))
        self.completion_spin.setSuffix('%')
        self.completion_spin.setFixedWidth(80)
        completion_layout.addWidget(self.completion_spin)
        completion_layout.addStretch()
        layout.addLayout(completion_layout)
        
        # Description
        layout.addWidget(QLabel("描述/备注:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlainText(self.project.get('note', ''))
        self.desc_edit.setFixedHeight(80)
        self.desc_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.desc_edit)
        
        # Missing items
        layout.addWidget(QLabel("缺失项 (用逗号分隔):"))
        self.missing_edit = QLineEdit()
        missing_items = self.project.get('missing', [])
        self.missing_edit.setText(', '.join(missing_items) if isinstance(missing_items, list) else str(missing_items))
        self.missing_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.missing_edit)
        
        # Next steps
        layout.addWidget(QLabel("下一步计划:"))
        self.next_steps_edit = QTextEdit()
        next_steps = self.project.get('next_steps', [])
        if isinstance(next_steps, list):
            self.next_steps_edit.setPlainText('\n'.join(next_steps))
        else:
            self.next_steps_edit.setPlainText(str(next_steps))
        self.next_steps_edit.setFixedHeight(60)
        self.next_steps_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.next_steps_edit)
        
        self.setLayout(layout)
    
    def get_updated_project(self) -> dict:
        """Get updated project data"""
        updated = self.project.copy()
        updated['completion'] = self.completion_spin.value()
        updated['note'] = self.desc_edit.toPlainText()
        
        # Parse missing items
        missing_text = self.missing_edit.text().strip()
        if missing_text:
            updated['missing'] = [item.strip() for item in missing_text.split(',')]
        else:
            updated['missing'] = []
        
        # Parse next steps
        next_steps_text = self.next_steps_edit.toPlainText().strip()
        if next_steps_text:
            updated['next_steps'] = [step.strip() for step in next_steps_text.split('\n') if step.strip()]
        else:
            updated['next_steps'] = []
        
        return updated


class ConfigEditorPanel(QWidget):
    """Main configuration editor panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects = []
        self.state_file = None
        self.init_ui()
        self.load_state()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("⚙️ 配置编辑器")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2196F3;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("编辑项目配置、添加新项目、管理 STATE.json")
        desc.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(desc)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 保存更改")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.save_btn.clicked.connect(self.save_changes)
        actions_layout.addWidget(self.save_btn)
        
        self.add_project_btn = QPushButton("➕ 添加项目")
        self.add_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b82d6;
            }
        """)
        self.add_project_btn.clicked.connect(self.add_project)
        actions_layout.addWidget(self.add_project_btn)
        
        self.reload_btn = QPushButton("🔄 重新加载")
        self.reload_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        self.reload_btn.clicked.connect(self.load_state)
        actions_layout.addWidget(self.reload_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # File info
        self.file_info_label = QLabel("文件：加载中...")
        self.file_info_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.file_info_label)
        
        # Projects scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background-color: #f5f5f5; border-radius: 8px; }")
        
        self.projects_container = QWidget()
        self.projects_layout = QVBoxLayout()
        self.projects_layout.setSpacing(10)
        self.projects_container.setLayout(self.projects_layout)
        
        self.scroll.setWidget(self.projects_container)
        layout.addWidget(self.scroll)
        
        self.setLayout(layout)
    
    def load_state(self):
        """Load STATE.json"""
        # Find STATE.json
        workspace_dir = Path(__file__).parent.parent.parent
        self.state_file = workspace_dir / 'STATE.json'
        
        if not self.state_file.exists():
            QMessageBox.warning(self, "警告", f"未找到 STATE.json 文件：\n{self.state_file}")
            self.file_info_label.setText("文件：未找到")
            return
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state_data = json.load(f)
            
            self.projects = self.state_data.get('projects', {})
            
            # Update file info
            self.file_info_label.setText(
                f"文件：{self.state_file} | 项目数：{len(self.projects)} | "
                f"最后修改：{datetime.fromtimestamp(self.state_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}"
            )
            
            # Display projects
            self.display_projects()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载 STATE.json 失败：\n{str(e)}")
            self.file_info_label.setText("文件：加载失败")
    
    def display_projects(self):
        """Display all projects"""
        # Clear existing
        while self.projects_layout.count():
            item = self.projects_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.projects:
            no_projects = QLabel("💭 暂无项目")
            no_projects.setStyleSheet("color: #666; font-style: italic;")
            no_projects.setAlignment(Qt.AlignCenter)
            self.projects_layout.addWidget(no_projects)
            return
        
        # Display each project
        for project_id, project_data in self.projects.items():
            project_data['id'] = project_id  # Add ID for reference
            card = ProjectEditorCard(project_data, self.projects_container)
            self.projects_layout.addWidget(card)
        
        self.projects_layout.addStretch()
    
    def add_project(self):
        """Add a new project"""
        # Create default project
        new_project = {
            'id': f'project_{len(self.projects) + 1}',
            'name': '新项目',
            'status': '规划中',
            'completion': 0,
            'note': '',
            'missing': [],
            'next_steps': ['定义项目目标']
        }
        
        # Add to state
        self.projects[new_project['id']] = new_project
        
        # Refresh display
        self.display_projects()
        
        # Scroll to bottom
        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )
    
    def save_changes(self):
        """Save all changes to STATE.json"""
        if not self.state_file or not self.state_file.exists():
            QMessageBox.warning(self, "警告", "STATE.json 文件不存在，无法保存")
            return
        
        # Collect updated projects
        updated_projects = {}
        
        for i in range(self.projects_layout.count()):
            item = self.projects_layout.itemAt(i)
            if item and item.widget():
                card = item.widget()
                if isinstance(card, ProjectEditorCard):
                    updated_project = card.get_updated_project()
                    project_id = updated_project.pop('id', None)
                    if project_id:
                        updated_projects[project_id] = updated_project
        
        # Update state data
        self.state_data['projects'] = updated_projects
        self.state_data['last_updated'] = datetime.now().isoformat()
        
        # Save to file
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(
                self,
                "保存成功",
                f"✅ 成功保存 {len(updated_projects)} 个项目配置\n\n"
                f"文件：{self.state_file}"
            )
            
            # Reload to refresh
            self.load_state()
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存 STATE.json 失败：\n{str(e)}")
