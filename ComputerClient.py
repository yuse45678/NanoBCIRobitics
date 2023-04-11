# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : ComputerClient.py
@Project  : example_benckmark_ecca.py
@Time     : 2023/4/10 17:35
@Author   : Li JiaYi
@Software : PyCharm
@License  : (C)Copyright 2020-2030
@Last Modify Time      @Version     @Desciption
--------------------       --------        -----------
2023/4/10 17:35        1.0             None
"""

import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser
from PyQt5.QtCore import pyqtSignal, QObject, QThread
from PyQt5.QtNetwork import QTcpSocket

class ClientWindow(QDialog):
    def __init__(self):
        super().__init__()

        # 创建Qt网络socket对象
        self.socket = QTcpSocket(self)

        # 连接服务器
        self.socket.connectToHost('192.168.10.101', 8000)

        # 创建界面
        self.create_ui()

    def create_ui(self):
        self.setWindowTitle("Client")

        # 创建输入框和发送按钮
        self.input_edit = QLineEdit()
        self.input_edit.setText("BG.OFFLINE")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        # 创建消息显示框
        self.message_box = QTextBrowser()

        # 布局
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.send_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Enter message:"))
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.message_box)

        self.setLayout(main_layout)

    def send_message(self):
        # 从输入框获取消息并发送
        message = self.input_edit.text()
        self.socket.write(message.encode())
        self.input_edit.setText("")

    def receive_message(self):
        # 从socket接收消息并显示
        message = self.socket.readAll().data().decode()
        self.message_box.append(message)

    def closeEvent(self, event):
        # 关闭socket连接
        self.socket.disconnectFromHost()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 创建客户端窗口并显示
    client_window = ClientWindow()
    client_window.show()

    sys.exit(app.exec_())

