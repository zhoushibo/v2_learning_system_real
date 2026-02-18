# -*- coding: utf-8 -*-
"""任务提交组件"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QProgressBar
from PyQt5.QtCore import QTimer, pyqtSignal
import requests
import json


class TaskSubmitWidget(QWidget):
    """任务提交组件"""

    # 信号
    task_submitted = pyqtSignal(str)  # task_id

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_task_id = None
        self.polling = False

        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()

        # 标题
        title_label = QLabel("<b>任务提交（V2 Gateway）</b>")
        layout.addWidget(title_label)

        # 任务输入
        input_label = QLabel("任务内容：")
        layout.addWidget(input_label)

        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText("输入你要执行的任务...")
        self.task_input.setMaximumHeight(100)
        layout.addWidget(self.task_input)

        # 提交按钮
        button_layout = QHBoxLayout()

        self.submit_btn = QPushButton("提交任务")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.submit_btn.clicked.connect(self._on_submit)
        button_layout.addWidget(self.submit_btn)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self._on_clear)
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

        # 状态显示
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)

        # 结果显示
        result_label = QLabel("<b>任务结果：</b>")
        layout.addWidget(result_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(200)
        layout.addWidget(self.result_text)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # 定时器用于轮询任务状态
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self._poll_task_status)

    def _on_submit(self):
        """提交任务"""
        task_content = self.task_input.toPlainText().strip()

        if not task_content:
            self.status_label.setText("❌ 请输入任务内容")
            return

        try:
            # 提交任务
            self.status_label.setText("提交中...")
            self.submit_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 不确定进度

            response = requests.post(
                "http://127.0.0.1:8000/tasks",
                json={"content": task_content},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.current_task_id = data['task_id']
                self.status_label.setText(f"✅ 任务已提交: {self.current_task_id}")
                self.result_text.clear()
                self.result_text.append(f"任务ID: {self.current_task_id}")
                self.result_text.append("状态: 处理中...")

                # 开始轮询
                self.polling = True
                self.poll_timer.start(1000)  # 每秒查询

                self.task_submitted.emit(self.current_task_id)
            else:
                self.status_label.setText(f"❌ 提交失败: {response.status_code}")
                self.submit_btn.setEnabled(True)
                self.progress_bar.setVisible(False)

        except requests.exceptions.ConnectionError:
            self.status_label.setText("❌ 无法连接到Gateway (http://127.0.0.1:8000)")
            self.result_text.setText("错误: Gateway未运行\n请先启动Gateway")
            self.submit_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
        except Exception as e:
            self.status_label.setText(f"❌ 错误: {e}")
            self.submit_btn.setEnabled(True)
            self.progress_bar.setVisible(False)

    def _poll_task_status(self):
        """轮询任务状态"""
        if not self.current_task_id:
            return

        try:
            response = requests.get(
                f"http://127.0.0.1:8000/tasks/{self.current_task_id}",
                timeout=5
            )

            if response.status_code == 200:
                task = response.json()
                status = task['status']

                if status == 'completed':
                    self._on_task_completed(task)
                elif status == 'failed':
                    self._on_task_failed(task)
                # 仍在处理中，继续轮询

        except Exception as e:
            print(f"[TaskSubmit] 轮询错误: {e}")

    def _on_task_completed(self, task):
        """任务完成"""
        self.polling = False
        self.poll_timer.stop()
        self.submit_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        self.status_label.setText("✅ 任务完成")
        self.result_text.clear()
        self.result_text.append(f"任务ID: {self.current_task_id}")
        self.result_text.append(f"状态: {task['status']}")
        self.result_text.append(f"模型: {task.get('metadata', {}).get('model', '未知')}")
        self.result_text.append(f"耗时: {task.get('metadata', {}).get('latency', 0):.2f}秒")
        self.result_text.append(f"\n结果:")
        self.result_text.append(task.get('result', ''))

    def _on_task_failed(self, task):
        """任务失败"""
        self.polling = False
        self.poll_timer.stop()
        self.submit_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        self.status_label.setText("❌ 任务失败")
        self.result_text.clear()
        self.result_text.append(f"任务ID: {self.current_task_id}")
        self.result_text.append(f"状态: {task['status']}")
        self.result_text.append(f"错误: {task.get('error', '未知错误')}")

    def _on_clear(self):
        """清空"""
        self.task_input.clear()
        self.status_label.setText("就绪")
        self.result_text.clear()
        self.current_task_id = None

    def stop_polling(self):
        """停止轮询"""
        self.polling = False
        self.poll_timer.stop()
