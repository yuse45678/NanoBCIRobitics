# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : ComputerClient.py
@Project  : NanoBCIRobitics
@Time     : 2023/4/12 22:08
@Author   : Li JiaYi
@Software : PyCharm
@License  : (C)Copyright 2020-2030
@Last Modify Time      @Version     @Desciption
--------------------       --------        -----------
2023/4/12 22:08        1.0             None
"""
import sys
import random
import time


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QEventLoop, QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtNetwork import QTcpServer, QTcpSocket
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QMessageBox
from gui_lib.mainGUI import Ui_MainWindow
from gui_lib.GUI_utils import get_host_ip



class ClientWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()

        # 创建Qt网络socket对象
        self.socket = QTcpSocket(self)

        # 创建界面
        self.setupUi(self)
        self.setWindowIcon(QIcon('文件.png'))
        self.ClientIPlineEdit.setText(get_host_ip())
        self.ConnectButton.clicked.connect(self.ConnectButtonClicked)

    def ConnectButtonClicked(self):
        try:
            self.socket.connectToHost(self.ServiceIPlineEdit.text(),int(self.ClientIPPortlineEdit.text()))
            self.printf(self.textBrowser,self.socket.readAll().data().decode())
            self.ConnectButton.setEnabled(False)
        except Exception as e:
            self.printf(self.textBrowser,"发生错误{}".format(e))
    def closeEvent(self, event):
        # 关闭socket连接
        self.socket.disconnectFromHost()
        event.accept()

    def printf(self, browser, mes):
        browser.append(mes)  # 在指定的区域显示提示信息
        self.cursot = browser.textCursor()
        browser.moveCursor(self.cursot.End)
        QtWidgets.QApplication.processEvents()

    def sleep(self, time):
        # 创建一个事件循环
        loop = QEventLoop()
        # 创建一个定时器
        timer = QTimer()
        timer.timeout.connect(loop.quit)
        timer.start(time)  # time秒后定时器超时
        # 进入事件循环，直到定时器超时
        loop.exec_()


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    system = ClientWindow()
    system.show()
    sys.exit(app.exec_())

