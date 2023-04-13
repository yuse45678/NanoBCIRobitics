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


class WorkerThread(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, socket, trials):
        super().__init__()
        self.socket = socket
        self.trials = trials

    def run(self) -> None:
        for i in range(self.trials):
            self.socket.write("BG+OFFLINE".encode())
            self.sleep(2000)
            while not self.socket.waitForReadyRead():
                pass
            self.progress.emit(self.socket.readAll().data().decode())
        self.finished.emit()


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
        self.SettingButton.clicked.connect(self.SettingButtonClicked)
        self.OfflineBeginButton.clicked.connect(self.OfflineBeginButtionClicked)

    def ConnectButtonClicked(self):
        try:
            self.socket.connectToHost(self.ServiceIPlineEdit.text(), int(self.ClientIPPortlineEdit.text()))
            self.sleep(100)
            if self.socket.waitForReadyRead(2000):
                self.printf(self.textBrowser, self.socket.readAll().data().decode())
                self.ConnectButton.setEnabled(False)
            else:
                self.printf(self.textBrowser, "连接失败，请确认IP地址是否正确")
        except Exception as e:
            self.printf(self.textBrowser, "发生错误{}".format(e))

    def SettingButtonClicked(self):
        try:
            self.printf(self.textBrowser, "--" * 20)
            self.socket.write(("SET+LED+1+" + self.LED1lineEdit.text()).encode())
            if self.socket.waitForReadyRead():
                self.printf(self.textBrowser, self.socket.readAll().data().decode())
            self.socket.write(("SET+LED+2+" + self.LED2lineEdit.text()).encode())
            if self.socket.waitForReadyRead():
                self.printf(self.textBrowser, self.socket.readAll().data().decode())
            self.socket.write(("SET+LED+3+" + self.LED3lineEdit.text()).encode())
            if self.socket.waitForReadyRead():
                self.printf(self.textBrowser, self.socket.readAll().data().decode())
            self.socket.write(("SET+LED+4+" + self.LED4lineEdit.text()).encode())
            if self.socket.waitForReadyRead():
                self.printf(self.textBrowser, self.socket.readAll().data().decode())
            self.socket.write(("SET+TRIAL+" + self.TrialslineEdit.text()).encode())
            if self.socket.waitForReadyRead():
                self.printf(self.textBrowser, self.socket.readAll().data().decode())
            self.socket.write(("SET+EV_DU+" + self.EVTimelineEdit.text()).encode())
            if self.socket.waitForReadyRead():
                self.printf(self.textBrowser, self.socket.readAll().data().decode())
            self.socket.write(("SET+TR_DU+" + self.TrialTimelineEdit.text()).encode())
            if self.socket.waitForReadyRead():
                self.printf(self.textBrowser, self.socket.readAll().data().decode())
            self.printf(self.textBrowser, "--" * 20)
            self.setOfflineButtonState(False)

        except Exception as e:
            self.printf(self.textBrowser, "发生错误{}".format(e))

    def setOfflineButtonState(self, state):
        self.SettingButton.setEnabled(state)
        self.OfflineBeginButton.setEnabled(not state)
        self.LED1lineEdit.setEnabled(state)
        self.LED2lineEdit.setEnabled(state)
        self.LED3lineEdit.setEnabled(state)
        self.LED4lineEdit.setEnabled(state)
        self.TrialslineEdit.setEnabled(state)
        self.EVTimelineEdit.setEnabled(state)
        self.TrialTimelineEdit.setEnabled(state)

    def OfflineBeginButtionClicked(self):
        try:
            if self.TrialslineEdit.isEnabled() is False:
                self.OfflineBeginButton.setEnabled(False)
                # self.worker_thread = WorkerThread(self.socket, int(self.TrialslineEdit.text()))
                # self.worker_thread.progress.connect(lambda progress: self.printf(self.textBrowser, progress))
                # self.worker_thread.finished.connect(lambda: self.OfflineBeginButton.setEnabled(True))
                # self.worker_thread.start()
                for i in range(int(self.TrialslineEdit.text())):
                    self.printf(self.textBrowser, ">>" * 20)
                    self.printf(self.textBrowser, "正在第{}次实验".format(i + 1))
                    self.socket.write("BG+OFFLINE".encode())
                    self.sleep(2000)
                    while not self.socket.waitForReadyRead():
                        pass
                    self.printf(self.textBrowser, "服务器::" + self.socket.readAll().data().decode())
                self.setOfflineButtonState(True)
        except Exception as e:
            self.printf(self.textBrowser, "发生错误{}".format(e))

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
