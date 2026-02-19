# -*- coding: utf-8 -*-
"""
Knowledge Base Quick Access Panel
Fast search, recent knowledge, and one-click import

Simplified version using subprocess to call knowledge_base scripts
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QFileDialog, QMessageBox,
    QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import subprocess
import sys
import json
from pathlib import Path


class SearchWorker(QThread):
    """Background worker for knowledge search using subprocess"""
    results_ready = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, query: str, limit: int = 10):
        super().__init__()
        self.query = query
        self.limit = limit
    
    def run(self):
        """Run search in background using knowledge_base CLI"""
        try:
            workspace_dir = Path(__file__).parent.parent.parent
            kb_dir = workspace_dir / 'knowledge_base'
            
            # Create a simple search script
            search_script = kb_dir / 'quick_search.py'
            
            if not search_script.exists():
                # Create the script
                script_content = f'''
import sys
sys.path.insert(0, r'{kb_dir}')
from core.knowledge_index import KnowledgeIndex
from core.knowledge_search import KnowledgeSearch
from core.embedding_generator import EmbeddingGenerator
from pathlib import Path
import json

query = "{self.query}"
limit = {self.limit}

data_dir = Path(r'{kb_dir}') / 'data'
index = KnowledgeIndex(str(data_dir / 'chroma_db'))
embedder = EmbeddingGenerator()
embedding = embedder.generate(query)
searcher = KnowledgeSearch(index)
results = searcher.search(query=query, query_embedding=embedding, limit=limit, use_hybrid=True)

# Convert to JSON-serializable format
serializable_results = []
for r in results:
    serializable_results.append({{
        'content': r.get('content', ''),
        'metadata': r.get('metadata', {{}}),
        'distance': float(r.get('distance', 0)) if r.get('distance') is not None else None
    }})

print(json.dumps(serializable_results, ensure_ascii=False))
'''
                search_script.write_text(script_content, encoding='utf-8')
            
            # Run the script
            result = subprocess.run(
                [sys.executable, str(search_script)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(kb_dir)
            )
            
            if result.returncode == 0:
                results = json.loads(result.stdout)
                self.results_ready.emit(results)
            else:
                self.error.emit(result.stderr)
                
        except subprocess.TimeoutExpired:
            self.error.emit("搜索超时，请缩短查询或重试")
        except Exception as e:
            self.error.emit(str(e))


class KnowledgeCard(QFrame):
    """Card displaying a single knowledge item"""
    
    def __init__(self, knowledge: dict, parent=None):
        super().__init__(parent)
        self.knowledge = knowledge
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            KnowledgeCard {
                background-color: white;
                border-left: 4px solid #4CAF50;
                border-radius: 8px;
                margin: 5px;
            }
            KnowledgeCard:hover {
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Content
        content = self.knowledge.get('content', 'No content')
        if len(content) > 500:
            content = content[:500] + '...'
        
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setFont(QFont("Arial", 11))
        layout.addWidget(content_label)
        
        # Metadata
        metadata = self.knowledge.get('metadata', {})
        if metadata:
            meta_parts = []
            if 'source' in metadata:
                meta_parts.append(f"来源：{Path(metadata['source']).name}")
            if 'created_at' in metadata:
                meta_parts.append(f"时间：{metadata['created_at']}")
            
            if meta_parts:
                meta_label = QLabel(" | ".join(meta_parts))
                meta_label.setStyleSheet("color: #666; font-size: 10px;")
                layout.addWidget(meta_label)
        
        # Distance/Similarity
        distance = self.knowledge.get('distance')
        if distance is not None:
            similarity = (1 - distance) * 100 if distance <= 1 else 0
            dist_label = QLabel(f"相似度：{similarity:.1f}%")
            dist_label.setStyleSheet("color: #2196F3; font-size: 10px; font-weight: bold;")
            layout.addWidget(dist_label)
        
        self.setLayout(layout)


class KnowledgeBasePanel(QWidget):
    """Main knowledge base quick access panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_results = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📚 知识库快速访问")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2196F3;")
        layout.addWidget(title)
        
        # Search box
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索知识库...")
        self.search_input.setFont(QFont("Arial", 12))
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        self.search_input.returnPressed.connect(self.search)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("🔍 搜索")
        self.search_btn.setFixedHeight(40)
        self.search_btn.setFixedWidth(100)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b82d6;
            }
        """)
        self.search_btn.clicked.connect(self.search)
        search_layout.addWidget(self.search_btn)
        
        layout.addLayout(search_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Results label
        results_label = QLabel("搜索结果：")
        results_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(results_label)
        
        # Results area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background-color: #f5f5f5; border-radius: 8px; }")
        
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_layout.setSpacing(10)
        self.results_container.setLayout(self.results_layout)
        
        self.scroll.setWidget(self.results_container)
        layout.addWidget(self.scroll)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("📤 导入文件")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.import_btn.clicked.connect(self.import_file)
        actions_layout.addWidget(self.import_btn)
        
        self.open_web_btn = QPushButton("🌐 打开 Web UI")
        self.open_web_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        self.open_web_btn.clicked.connect(self.open_web_ui)
        actions_layout.addWidget(self.open_web_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Stats
        self.stats_label = QLabel("知识库统计：点击「打开 Web UI」查看")
        self.stats_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
    
    def search(self):
        """Perform search"""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "提示", "请输入搜索关键词")
            return
        
        if len(query) > 200:
            QMessageBox.warning(self, "提示", "查询过长，请控制在 200 字符以内")
            return
        
        # Clear previous results
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Show progress
        self.progress.show()
        self.search_btn.setEnabled(False)
        self.results_label.setText("搜索中...")
        
        # Start search worker
        self.worker = SearchWorker(query)
        self.worker.results_ready.connect(self.on_search_results)
        self.worker.error.connect(self.on_search_error)
        self.worker.start()
    
    def on_search_results(self, results):
        """Handle search results"""
        self.progress.hide()
        self.search_btn.setEnabled(True)
        self.current_results = results
        
        if not results:
            self.results_label.setText("搜索结果：未找到相关知识")
            no_results = QLabel("💭 没有找到相关知识，换个关键词试试？")
            no_results.setStyleSheet("color: #666; font-style: italic;")
            no_results.setAlignment(Qt.AlignCenter)
            self.results_layout.addWidget(no_results)
            return
        
        self.results_label.setText(f"搜索结果：找到 {len(results)} 条相关知识")
        
        # Display results
        for i, result in enumerate(results[:10], 1):
            card = KnowledgeCard(result, self.results_container)
            self.results_layout.addWidget(card)
        
        # Add spacing
        self.results_layout.addStretch()
    
    def on_search_error(self, error_msg):
        """Handle search error"""
        self.progress.hide()
        self.search_btn.setEnabled(True)
        self.results_label.setText("搜索失败")
        
        error_label = QLabel(f"❌ 搜索失败：{error_msg[:200]}")
        error_label.setStyleSheet("color: #f44336;")
        error_label.setWordWrap(True)
        self.results_layout.addWidget(error_label)
        
        # Add suggestion
        suggestion = QLabel("💡 建议：\n1. 确保知识库 Web UI 已启动\n2. 检查知识库中是否有数据\n3. 尝试其他关键词")
        suggestion.setStyleSheet("color: #FF9800;")
        suggestion.setWordWrap(True)
        self.results_layout.addWidget(suggestion)
        
        self.results_layout.addStretch()
    
    def import_file(self):
        """Import file to knowledge base"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择要导入的文件",
            "",
            "文本文件 (*.txt);;Markdown 文件 (*.md);;所有文件 (*.*)"
        )
        
        if file_path:
            QMessageBox.information(
                self,
                "导入提示",
                f"📄 文件选择成功：{file_path}\n\n"
                "请使用知识库 Web UI 完成导入操作：\n"
                "1. 点击「打开 Web UI」按钮\n"
                "2. 切换到「导入文件」标签页\n"
                "3. 拖拽文件或点击上传\n"
                "4. 等待处理完成"
            )
    
    def open_web_ui(self):
        """Open Knowledge Base Web UI in browser"""
        import webbrowser
        webbrowser.open("http://localhost:8501")
        
        # Update stats label
        self.stats_label.setText("💡 知识库 Web UI 已在浏览器中打开")
