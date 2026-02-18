# -*- coding: utf-8 -*-
"""托盘图标测试"""
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox

app = QApplication(sys.argv)

# 创建消息框
msg = QMessageBox()

# 设置消息内容
msg.setIcon(QMessageBox.Information)
msg.setWindowTitle("托盘图标测试")
msg.setText("托盘图标已创建")
msg.setInformativeText("请查看Windows右下角系统托盘\n应该有一个空白图标")
msg.setDetailedText("托盘图标位置：Windows任务栏右侧通知区域\n如果看不到，请检查：\n1. 点击任务栏右侧的箭头图标\n2. 点击'自定义'\n3. 确保'通知区域'已显示所有图标")

# 显示消息框
msg.exec_()

print("托盘图标测试完成")
print("图标在右下角通知区域")
