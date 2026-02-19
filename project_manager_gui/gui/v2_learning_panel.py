# -*- coding: utf-8 -*-
"""
V2 Learning System Integration Panel
Quick learning, progress monitoring, and auto-save to knowledge base
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QComboBox, QProgressBar,
    QMessageBox, QGroupBox, QSpinBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


class LearningWorker(QThread):
    """Background worker for V2 learning"""
    progress = pyqtSignal(int, str)  # percent, status_text
    log = pyqtSignal(str)  # log_line
    finished = pyqtSignal(bool, str, dict)  # success, message, stats
    error = pyqtSignal(str)
    
    def __init__(self, topic: str, mode: str = 'fast', num_workers: int = 3):
        super().__init__()
        self.topic = topic
        self.mode = mode
        self.num_workers = num_workers
    
    def run(self):
        """Run learning in background"""
        try:
            workspace_dir = Path(__file__).parent.parent.parent
            v2_dir = workspace_dir / 'v2_learning_system_real'
            
            if not v2_dir.exists():
                self.error.emit(f"V2 学习系统目录不存在：{v2_dir}")
                return
            
            # Create learning script
            learning_script = v2_dir / 'quick_learn.py'
            script_content = f'''
import sys
sys.path.insert(0, r'{v2_dir}')
import asyncio
from learning_engine import LearningEngine
import json
from datetime import datetime

topic = "{self.topic}"
mode = "{self.mode}"
num_workers = {self.num_workers}

# Map mode to perspectives
mode_map = {{
    'fast': 1,
    'deep': 3,
    'comprehensive': 5
}}
perspectives = mode_map.get(mode, 3)

print(f"[INFO] Starting learning: {{topic}}")
print(f"[INFO] Mode: {{mode}} ({{perspectives}} perspectives)")
print(f"[INFO] Workers: {{num_workers}}")

async def learn():
    engine = LearningEngine()
    
    # Start learning
    start_time = datetime.now()
    print(f"[INFO] Learning started at {{start_time}}")
    
    results = await engine.parallel_learning(
        topic,
        num_perspectives=perspectives,
        save_to_kb=True,
        update_existing=True
    )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Stats
    stats = {{
        'topic': topic,
        'mode': mode,
        'workers': num_workers,
        'perspectives': perspectives,
        'duration_seconds': duration,
        'knowledge_points': len(results.get('knowledge_points', [])),
        'saved_to_kb': results.get('saved_to_kb', False),
        'timestamp': datetime.now().isoformat()
    }}
    
    print(f"[INFO] Learning completed in {{duration:.1f}}s")
    print(f"[INFO] Knowledge points: {{stats['knowledge_points']}}")
    print(f"[INFO] Saved to KB: {{stats['saved_to_kb']}}")
    print(f"[STATS]{{json.dumps(stats, ensure_ascii=False)}}[/STATS]")
    
    return stats

if __name__ == "__main__":
    try:
        stats = asyncio.run(learn())
        print(f"[SUCCESS] Learning completed successfully")
    except Exception as e:
        print(f"[ERROR]{{str(e)}}[/ERROR]")
        sys.exit(1)
'''
            learning_script.write_text(script_content, encoding='utf-8')
            
            # Run learning
            self.progress.emit(10, "准备学习环境...")
            self.log.emit(f"[INFO] 开始学习：{self.topic}")
            self.log.emit(f"[INFO] 模式：{self.mode} ({num_workers} workers)")
            
            process = subprocess.Popen(
                [sys.executable, str(learning_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(v2_dir)
            )
            
            # Read output line by line
            progress = 10
            for line in process.stdout:
                line = line.strip()
                if line:
                    self.log.emit(line)
                    
                    # Parse progress
                    if '[INFO]' in line:
                        progress += 5
                        if progress > 90:
                            progress = 90
                        status = line.replace('[INFO]', '').strip()
                        self.progress.emit(min(progress, 90), status)
                    
                    elif '[STATS]' in line:
                        # Extract stats JSON
                        import re
                        match = re.search(r'\[STATS\](.+?)\[/STATS\]', line)
                        if match:
                            stats_json = match.group(1)
                            try:
                                stats = json.loads(stats_json)
                                self.progress.emit(100, "学习完成！")
                                self.finished.emit(True, "学习成功完成", stats)
                                return
                            except:
                                pass
            
            # Check for errors
            stderr = process.stderr.read()
            if stderr:
                error_match = re.search(r'\[ERROR\](.+?)\[/ERROR\]', stderr)
                if error_match:
                    self.error.emit(error_match.group(1))
                    self.finished.emit(False, "学习失败", {})
                    return
            
            # If we get here, learning completed but no stats
            self.progress.emit(100, "学习完成")
            self.finished.emit(True, "学习完成（无详细统计）", {})
            
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit(False, f"学习过程异常：{str(e)}", {})


class LearningHistoryCard(QFrame):
    """Card displaying a learning history item"""
    
    def __init__(self, history_item: dict, parent=None):
        super().__init__(parent)
        self.history_item = history_item
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            LearningHistoryCard {
                background-color: white;
                border-left: 4px solid #FF9800;
                border-radius: 8px;
                margin: 5px;
            }
            LearningHistoryCard:hover {
                background-color: #fff8e1;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Topic
        topic = self.history_item.get('topic', 'Unknown Topic')
        topic_label = QLabel(f"📚 {topic}")
        topic_label.setFont(QFont("Arial", 13, QFont.Bold))
        topic_label.setStyleSheet("color: #FF9800;")
        layout.addWidget(topic_label)
        
        # Details
        details = []
        if 'mode' in self.history_item:
            mode_map = {'fast': '快速', 'deep': '深度', 'comprehensive': '全面'}
            details.append(f"模式：{mode_map.get(self.history_item['mode'], self.history_item['mode'])}")
        if 'duration_seconds' in self.history_item:
            details.append(f"耗时：{self.history_item['duration_seconds']:.1f}秒")
        if 'knowledge_points' in self.history_item:
            details.append(f"知识点：{self.history_item['knowledge_points']}个")
        if 'saved_to_kb' in self.history_item:
            saved = "✅ 已保存" if self.history_item['saved_to_kb'] else "❌ 未保存"
            details.append(f"知识库：{saved}")
        if 'timestamp' in self.history_item:
            try:
                dt = datetime.fromisoformat(self.history_item['timestamp'])
                details.append(f"时间：{dt.strftime('%Y-%m-%d %H:%M')}")
            except:
                pass
        
        details_label = QLabel(" | ".join(details))
        details_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(details_label)
        
        self.setLayout(layout)


class V2LearningPanel(QWidget):
    """Main V2 learning panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.learning_history = []
        self.current_worker = None
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🧠 V2 学习系统")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #FF9800;")
        layout.addWidget(title)
        
        # Learning configuration
        config_group = QGroupBox("学习配置")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FF9800;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #FF9800;
            }
        """)
        config_layout = QVBoxLayout()
        
        # Topic input
        topic_layout = QHBoxLayout()
        topic_label = QLabel("学习主题:")
        topic_label.setFont(QFont("Arial", 12))
        topic_layout.addWidget(topic_label)
        
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("例如：量子力学基础、Python 异步编程、机器学习入门...")
        self.topic_input.setFont(QFont("Arial", 12))
        self.topic_input.setFixedHeight(40)
        topic_layout.addWidget(self.topic_input)
        config_layout.addLayout(topic_layout)
        
        # Mode and workers
        params_layout = QHBoxLayout()
        
        # Mode selection
        mode_label = QLabel("学习模式:")
        mode_label.setFont(QFont("Arial", 11))
        params_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("⚡ 快速学习 (1 个视角)", "fast")
        self.mode_combo.addItem("🔍 深度学习 (3 个视角)", "deep")
        self.mode_combo.addItem("📖 全面学习 (5 个视角)", "comprehensive")
        self.mode_combo.setCurrentIndex(1)  # Default to deep
        self.mode_combo.setFixedWidth(200)
        params_layout.addWidget(self.mode_combo)
        
        params_layout.addSpacing(20)
        
        # Worker count
        workers_label = QLabel("Worker 数量:")
        workers_label.setFont(QFont("Arial", 11))
        params_layout.addWidget(workers_label)
        
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 5)
        self.workers_spin.setValue(3)
        self.workers_spin.setFixedWidth(60)
        params_layout.addWidget(self.workers_spin)
        
        params_layout.addStretch()
        config_layout.addLayout(params_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Start button
        self.start_btn = QPushButton("🚀 开始学习")
        self.start_btn.setFixedHeight(50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.start_btn.clicked.connect(self.start_learning)
        layout.addWidget(self.start_btn)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("准备就绪")
        self.progress.setFixedHeight(30)
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Log area
        log_label = QLabel("学习日志:")
        log_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(log_label)
        
        self.log_scroll = QScrollArea()
        self.log_scroll.setWidgetResizable(True)
        self.log_scroll.setFixedHeight(200)
        self.log_scroll.setStyleSheet("QScrollArea { background-color: #f5f5f5; border-radius: 8px; }")
        
        self.log_container = QWidget()
        self.log_layout = QVBoxLayout()
        self.log_container.setLayout(self.log_layout)
        
        self.log_scroll.setWidget(self.log_container)
        layout.addWidget(self.log_scroll)
        
        # History
        history_label = QLabel("📜 学习历史:")
        history_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(history_label)
        
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setFixedHeight(200)
        self.history_scroll.setStyleSheet("QScrollArea { background-color: #f5f5f5; border-radius: 8px; }")
        
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_container.setLayout(self.history_layout)
        
        self.history_scroll.setWidget(self.history_container)
        layout.addWidget(self.history_scroll)
        
        self.setLayout(layout)
    
    def start_learning(self):
        """Start learning process"""
        topic = self.topic_input.text().strip()
        if not topic:
            QMessageBox.warning(self, "提示", "请输入学习主题")
            return
        
        if len(topic) > 100:
            QMessageBox.warning(self, "提示", "学习主题过长，请控制在 100 字符以内")
            return
        
        # Get configuration
        mode = self.mode_combo.currentData()
        num_workers = self.workers_spin.value()
        
        # Disable button
        self.start_btn.setEnabled(False)
        self.start_btn.setText("学习中...")
        
        # Show progress
        self.progress.show()
        self.progress.setValue(0)
        self.progress.setFormat("准备中...")
        
        # Clear log
        while self.log_layout.count():
            item = self.log_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Start worker
        self.current_worker = LearningWorker(topic, mode, num_workers)
        self.current_worker.progress.connect(self.on_progress)
        self.current_worker.log.connect(self.on_log)
        self.current_worker.finished.connect(self.on_finished)
        self.current_worker.error.connect(self.on_error)
        self.current_worker.start()
    
    def on_progress(self, percent, status):
        """Update progress"""
        self.progress.setValue(percent)
        self.progress.setFormat(f"{percent}% - {status}")
    
    def on_log(self, line):
        """Add log line"""
        log_label = QLabel(line)
        log_label.setFont(QFont("Consolas", 10))
        log_label.setWordWrap(True)
        
        if '[INFO]' in line:
            log_label.setStyleSheet("color: #2196F3;")
        elif '[SUCCESS]' in line:
            log_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        elif '[ERROR]' in line:
            log_label.setStyleSheet("color: #f44336; font-weight: bold;")
        else:
            log_label.setStyleSheet("color: #333;")
        
        self.log_layout.addWidget(log_label)
        self.log_scroll.verticalScrollBar().setValue(
            self.log_scroll.verticalScrollBar().maximum()
        )
    
    def on_finished(self, success, message, stats):
        """Learning finished"""
        self.start_btn.setEnabled(True)
        self.start_btn.setText("🚀 开始学习")
        
        if success:
            self.progress.setFormat("✅ 学习完成！")
            QMessageBox.information(self, "学习完成", message)
            
            # Add to history
            if stats:
                self.learning_history.insert(0, stats)
                self.save_history()
                self.refresh_history()
        else:
            self.progress.setFormat("❌ 学习失败")
            QMessageBox.critical(self, "学习失败", message)
    
    def on_error(self, error_msg):
        """Learning error"""
        self.start_btn.setEnabled(True)
        self.start_btn.setText("🚀 开始学习")
        self.progress.setFormat("❌ 错误")
        
        error_label = QLabel(f"❌ 错误：{error_msg}")
        error_label.setStyleSheet("color: #f44336; font-weight: bold;")
        self.log_layout.addWidget(error_label)
    
    def load_history(self):
        """Load learning history from file"""
        history_file = Path(__file__).parent.parent / 'data' / 'learning_history.json'
        try:
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.learning_history = json.load(f)
                self.refresh_history()
        except Exception as e:
            print(f"Failed to load history: {e}")
            self.learning_history = []
    
    def save_history(self):
        """Save learning history to file"""
        history_file = Path(__file__).parent.parent / 'data' / 'learning_history.json'
        try:
            history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_history[:20], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save history: {e}")
    
    def refresh_history(self):
        """Refresh history display"""
        # Clear
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.learning_history:
            no_history = QLabel("💭 暂无学习记录")
            no_history.setStyleSheet("color: #666; font-style: italic;")
            no_history.setAlignment(Qt.AlignCenter)
            self.history_layout.addWidget(no_history)
            return
        
        # Display history
        for item in self.learning_history[:10]:
            card = LearningHistoryCard(item, self.history_container)
            self.history_layout.addWidget(card)
        
        self.history_layout.addStretch()
