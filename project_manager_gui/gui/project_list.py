# -*- coding: utf-8 -*-
"""项目列表组件 - 带完成度进度条"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt
from typing import Dict, List
from .project_card import ProgressProjectCard


class ProjectList(QWidget):
    """项目列表（带完成度可视化）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("<h2>📁 项目列表 - 完成度监控</h2>")
        title_label.setStyleSheet("color: #2196F3;")
        layout.addWidget(title_label)
        
        # 说明文字
        info_label = QLabel("显示所有项目的完成度进度，自动从 STATE.json 加载数据")
        info_label.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # 项目卡片容器（带滚动）
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background-color: #f5f5f5; border-radius: 5px; }")
        
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(15)
        self.cards_container.setLayout(self.cards_layout)
        
        self.scroll.setWidget(self.cards_container)
        layout.addWidget(self.scroll)
        
        self.setLayout(layout)
    
    def update_projects(self, projects: List[Dict]):
        """
        更新项目列表（带完成度进度条）
        Args:
            projects: 项目列表（从 STATE.json 加载，包含 completion 字段）
        """
        # 清空现有卡片
        for i in reversed(range(self.cards_layout.count())):
            child = self.cards_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        self.cards.clear()
        
        # 创建新卡片（使用增强版 ProgressProjectCard）
        for project in projects:
            # 确保项目有 completion 字段
            if 'completion' not in project:
                project['completion'] = 0
            
            card = ProgressProjectCard(project)
            self.cards_layout.addWidget(card)
            self.cards[project.get('id')] = card
        
        # 添加统计信息
        total = len(projects)
        completed = sum(1 for p in projects if p.get('completion', 0) == 100)
        in_progress = sum(1 for p in projects if 0 < p.get('completion', 0) < 100)
        not_started = sum(1 for p in projects if p.get('completion', 0) == 0)
        
        stats_label = QLabel(
            f"<b>统计：</b> 总计 {total} 个项目 | "
            f"🎉 已完成 {completed} | "
            f"🟡 进行中 {in_progress} | "
            f"❌ 未开始 {not_started}"
        )
        stats_label.setStyleSheet("color: #2196F3; font-weight: bold; margin-top: 10px;")
        self.cards_layout.addWidget(stats_label)
        self.cards_layout.addStretch()
