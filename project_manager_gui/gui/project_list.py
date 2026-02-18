# -*- coding: utf-8 -*-
"""项目列表组件"""
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Dict, List


class ProjectCard(QWidget):
    """项目卡片"""

    # 信号
    start_component = pyqtSignal(str, str)  # project_id, component_id
    stop_component = pyqtSignal(str, str)    # project_id, component_id
    check_health = pyqtSignal(str, str)      # project_id, component_id

    def __init__(self, project: Dict, parent=None):
        super().__init__(parent)

        self.project = project
        self.project_id = project.get('id')
        self.project_name = project.get('name')
        self.components = project.get('components', [])

        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()

        # 项目名称
        name_label = QLabel(f"<b>{self.project_name}</b>")
        layout.addWidget(name_label)

        # 描述
        description = self.project.get('description', '')
        if description:
            desc_label = QLabel(f"<small>{description}</small>")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # 组件列表
        for component in self.components:
            comp_widget = self._create_component_widget(component)
            layout.addWidget(comp_widget)

        self.setLayout(layout)

    def _create_component_widget(self, component: Dict) -> QWidget:
        """创建组件小部件"""
        widget = QWidget()
        layout = QHBoxLayout()

        # 组件名称
        comp_id = component.get('id')
        comp_name = component.get('name', comp_id)
        comp_label = QLabel(f"  {comp_name}")
        comp_label.setStyleSheet("color: #666;")
        layout.addWidget(comp_label)

        layout.addStretch()

        # 启动按钮
        start_btn = QPushButton("启动")
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        start_btn.clicked.connect(lambda: self.start_component.emit(self.project_id, comp_id))
        layout.addWidget(start_btn)

        # 停止按钮
        stop_btn = QPushButton("停止")
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        stop_btn.clicked.connect(lambda: self.stop_component.emit(self.project_id, comp_id))
        layout.addWidget(stop_btn)

        widget.setLayout(layout)
        return widget


class ProjectList(QWidget):
    """项目列表"""

    # 信号
    start_component = pyqtSignal(str, str)
    stop_component = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.cards = {}

        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()

        # 标题
        title_label = QLabel("<h2>项目管理器</h2>")
        layout.addWidget(title_label)

        # 项目卡片容器
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_container.setLayout(self.cards_layout)
        layout.addWidget(self.cards_container)

        layout.addStretch()

        self.setLayout(layout)

    def update_projects(self, projects: List[Dict]):
        """
        更新项目列表

        Args:
            projects: 项目列表
        """
        # 清空现有卡片
        for i in reversed(range(self.cards_layout.count())):
            child = self.cards_layout.itemAt(i).widget()
            if child:
                child.deleteLater()

        self.cards.clear()

        # 创建新卡片
        for project in projects:
            card = ProjectCard(project)

            # 连接信号
            card.start_component.connect(self.start_component.emit)
            card.stop_component.connect(self.stop_component.emit)

            self.cards_layout.addWidget(card)
            self.cards[project.get('id')] = card
