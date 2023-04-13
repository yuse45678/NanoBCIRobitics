# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : RaspberryPiGUI.py
@Project  : NanoBCIRobitics
@Time     : 2023/4/10 14:57
@Author   : Li JiaYi
@Software : PyCharm
@License  : (C)Copyright 2020-2030
@Last Modify Time      @Version     @Desciption
--------------------       --------        -----------
2023/4/10 14:57        1.0             None
"""
import sys
import random
import time

import serial
import serial.tools.list_ports
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QEventLoop, QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtNetwork import QTcpServer, QTcpSocket
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QMessageBox
from gui_lib.GUI import Ui_MainWindow
from gui_lib.GUI_utils import get_host_ip
import RPi.GPIO as GPIO
from SSVEP.Inspire.RaspberryPi import LED
from neuracle_lib.triggerBox import TriggerBox


class ServerWorker(QObject):
    # 创建信号
    new_message = pyqtSignal(str)

    def __init__(self, socket):
        super().__init__()

        self.socket = socket

    def run(self):
        while True:
            # 从socket接收消息并发送信号
            message = self.socket.readAll().data().decode()
            self.new_message.emit(message)

            # 将消息回传给客户端
            self.socket.write(message.encode())


class ServerWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()
        # 创建Qt网络socket对象

        self.server = QTcpServer(self)
        self.clients = []

        # 监听8000端口
        self.server.listen(port=8000)
        self.server.newConnection.connect(self.handle_new_connection)

        # 创建界面
        self.setupUi(self)
        self.count = 0
        self.trials = 10
        self.evoke_duration = 3
        self.trial_duration = 4
        self.Led1 = LED([12, 18, 16], "上Led").set_color(LED.BLACK).set_evoke_fre(11.1)
        self.Led2 = LED([22, 36, 32], "左Led").set_color(LED.BLACK).set_evoke_fre(12.4)
        self.Led3 = LED([35, 38, 37], "右Led").set_color(LED.BLACK).set_evoke_fre(9.8)
        self.Led4 = LED([11, 15, 13], "下Led").set_color(LED.BLACK).set_evoke_fre(13.7)
        self.printf(self.offlineTextBrowser, "当前系统已加载完成")
        self.IPtextBrowser.setText(get_host_ip())
        self.get_serial_info()

        self.setWindowIcon(QIcon('文件.png'))
        # self.connectButton.clicked.connect()

    def handle_new_connection(self):
        self.get_serial_info()
        # 处理新连接
        client_socket = self.server.nextPendingConnection()
        client_socket.readyRead.connect(self.handle_ready_read)

        self.printf(self.offlineTextBrowser, "客户机{}正在连接.....".format(client_socket.peerAddress().toString()))
        self.printf(self.offlineTextBrowser,
                    "客户机{}已连接树莓派{}".format(client_socket.peerAddress().toString(), self.IPtextBrowser.text()))
        self.ClientIPtextBrowser.setText(client_socket.peerAddress().toString())
        self.triggerbox = TriggerBox("/dev/" + self.comComboBox.currentText())
        client_socket.write(
            ("客户机{}已连接树莓派{}".format(client_socket.peerAddress().toString(),
                                             self.IPtextBrowser.text())).encode())
        # 将客户端socket添加到列表中
        self.clients.append(client_socket)

    def handle_ready_read(self):
        self.get_serial_info()
        # 处理新消息
        for client_socket in self.clients:
            if client_socket.bytesAvailable() > 0:
                message = client_socket.readAll().data().decode()
                # self.printf(self.offlineTextBrowser,message)
                res = message.split('+')
                self.printf(self.offlineTextBrowser, '服务端接收到{}指令'.format(message))
                try:
                    if res[0] == 'BG':
                        if res[1] == 'ONLINE':
                            self.config_color([LED.GREEN, LED.GREEN, LED.GREEN, LED.GREEN])
                            trial_timer = time.time()
                            self.loop_remote(trial_timer)
                        elif res[1] == 'OFFLINE':
                            self.printf(self.offlineTextBrowser, "--" * 50)
                            self.printf(self.offlineTextBrowser, '开始第{}次离线实验'.format(self.count + 1))
                            self.printf(self.offlineTextBrowser, "每组试验共四次闪烁，请按照提示依次注视LED灯")
                            self.printf(self.offlineTextBrowser, "--" * 50)
                            self.sleep(2000)
                            if self.count < self.trials:
                                self.count = self.count + 1
                                sequence = random.sample(range(1, 5), 4)
                                for seq in sequence:
                                    if seq == 1:
                                        self.printf(self.offlineTextBrowser, "请注视上面的LED灯，两秒后开始闪烁！")
                                        self.sleep(1000)
                                        self.Led1.set_color(LED.GREEN)
                                        self.printf(self.offlineTextBrowser, "开始闪烁！")
                                        self.triggerbox.output_event_data(1)
                                        trial_timer = time.time()
                                        self.single_loop_remote(trial_timer, self.Led1)
                                    elif seq == 2:
                                        self.printf(self.offlineTextBrowser, "请注视下面的LED灯，两秒后开始闪烁！")
                                        self.sleep(1000)
                                        self.printf(self.offlineTextBrowser, "开始闪烁！")
                                        self.Led4.set_color(LED.GREEN)
                                        self.triggerbox.output_event_data(2)
                                        trial_timer = time.time()
                                        self.single_loop_remote(trial_timer, self.Led4)
                                    elif seq == 3:
                                        self.printf(self.offlineTextBrowser, "请注视左边的LED灯，两秒后开始闪烁！")
                                        self.sleep(1000)
                                        self.printf(self.offlineTextBrowser, "开始闪烁！")
                                        self.Led2.set_color(LED.GREEN)
                                        self.triggerbox.output_event_data(3)
                                        trial_timer = time.time()
                                        self.single_loop_remote(trial_timer, self.Led2)
                                    elif seq == 4:
                                        self.printf(self.offlineTextBrowser, "请注视右边的LED灯，两秒后开始闪烁！")
                                        self.sleep(1000)
                                        self.printf(self.offlineTextBrowser, "开始闪烁！")
                                        self.Led3.set_color(LED.GREEN)
                                        self.triggerbox.output_event_data(4)
                                        trial_timer = time.time()
                                        self.single_loop_remote(trial_timer, self.Led3)
                                self.printf(self.offlineTextBrowser, "当前试次实验已完成！！")
                                message = "当前第{}次实验已完成".format(self.count)
                                client_socket.write(message.encode())
                                self.printf(self.offlineTextBrowser, "--" * 50)
                                self.offlineProgressBar.setValue(int(self.count / self.trials * 100))
                            else:
                                self.printf(self.offlineTextBrowser, '已经达到所设置的离线实验试验数')
                                self.count = 0
                    elif res[0] == 'SET':
                        if res[1] == 'TRIAL':
                            self.trials = int(res[2])
                            message = '当前最大试验数为{}'.format(self.trials)
                            client_socket.write(message.encode())
                            self.printf(self.offlineTextBrowser, message)
                            self.count = 0
                            self.offlineProgressBar.setValue(int(self.count / self.trials * 100))
                        elif res[1] == 'EV_DU':
                            self.evoke_duration = float(res[2])
                            message = '当前视觉刺激时间为{}s'.format(self.evoke_duration)
                            client_socket.write(message.encode())
                            self.printf(self.offlineTextBrowser, message)
                        elif res[1] == 'TR_DU':
                            self.trial_duration = float(res[2])
                            message = '当前试验时间为{}s'.format(self.trial_duration)
                            client_socket.write(message.encode())
                            self.printf(self.offlineTextBrowser, message)
                        elif res[1] == 'LED':
                            if res[2] == '1':
                                self.Led1.set_evoke_fre(float(res[3]))
                                message = '当前{}闪烁频率为{}Hz'.format(self.Led1.name, self.Led1.evoke_fre)
                                client_socket.write(message.encode())
                                self.printf(self.offlineTextBrowser, message)
                            if res[2] == '2':
                                self.Led2.set_evoke_fre(float(res[3]))
                                message = '当前{}闪烁频率为{}Hz'.format(self.Led2.name, self.Led2.evoke_fre)
                                client_socket.write(message.encode())
                                self.printf(self.offlineTextBrowser, message)
                            if res[2] == '3':
                                self.Led3.set_evoke_fre(float(res[3]))
                                message = '当前{}闪烁频率为{}Hz'.format(self.Led3.name, self.Led3.evoke_fre)
                                client_socket.write(message.encode())
                                self.printf(self.offlineTextBrowser, message)
                            if res[2] == '4':
                                self.Led4.set_evoke_fre(float(res[3]))
                                message = '当前{}闪烁频率为{}Hz'.format(self.Led4.name, self.Led4.evoke_fre)
                                client_socket.write(message.encode())
                                self.printf(self.offlineTextBrowser, message)
                    if res[0] == 'LIST':
                        message = "**" * 50
                        message = message + '\n当前最大试验数为{}'.format(self.trials)
                        message = message + '\n当前试验时间为{}s'.format(self.trial_duration)
                        message = message + '\n当前视觉刺激时间为{}s'.format(self.evoke_duration)
                        message = message + '\n当前{}闪烁频率为{}Hz'.format(self.Led1.name, self.Led1.evoke_fre)
                        message = message + '\n当前{}闪烁频率为{}Hz'.format(self.Led2.name, self.Led2.evoke_fre)
                        message = message + '\n当前{}闪烁频率为{}Hz'.format(self.Led3.name, self.Led3.evoke_fre)
                        message = message + '\n当前{}闪烁频率为{}Hz'.format(self.Led4.name, self.Led4.evoke_fre)
                        self.printf(self.offlineTextBrowser, message)
                    # client_socket.write(self.offlineTextBrowser.toPlainText().encode())
                except Exception as e:
                    self.printf(self.offlineTextBrowser, "发生错误{}".format(e))

    def closeEvent(self, event):
        # 关闭socket连接
        for client_socket in self.clients:
            client_socket.disconnectFromHost()

        self.server.close()
        event.accept()

    def config_color(self, colors):
        for led, color in zip([self.Led1, self.Led2, self.Led3, self.Led4], colors):
            led.set_color(color)

    def get_serial_info(self):  # 获取可用串口列表
        self.plist = list(serial.tools.list_ports.comports())
        if len(self.plist) <= 0:
            print('未找到串口')
            qm = QMessageBox.warning(self, '提示窗口', '未找到串口!请检查接线和电脑接口。',
                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            if qm == QMessageBox.Yes:
                print('Yes')
            else:
                print('No')
        else:
            for i in list(self.plist):
                self.comComboBox.addItem(i.name)

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

    def loop_remote(self, trial_timer):
        trial_time = time.time() - trial_timer
        while trial_time < self.trial_duration:
            if trial_time < self.evoke_duration:
                for Led in [self.Led1, self.Led2, self.Led3, self.Led4]:
                    pass_time = trial_time - Led.counter * Led.half_period * 2
                    if pass_time < Led.half_period:
                        Led.turn_off()
                    elif Led.half_period < pass_time < Led.half_period * 2:
                        Led.turn_on()
                    elif pass_time > Led.half_period * 2:
                        Led.counter += 1
                        Led.turn_off()
            elif self.evoke_duration < trial_time < self.trial_duration:
                for Led in [self.Led1, self.Led2, self.Led3, self.Led4]:
                    Led.turn_off()
                    print("%s: count %d" % (Led.name, Led.counter))
                break
            trial_time = time.time() - trial_timer
        for Led in [self.Led1, self.Led2, self.Led3, self.Led4]:
            Led.counter = 0

    def single_loop_remote(self, trial_timer, Led):
        trial_time = time.time() - trial_timer
        while trial_time < self.trial_duration:
            if trial_time < self.evoke_duration:
                pass_time = trial_time - Led.counter * Led.half_period * 2
                if pass_time < Led.half_period:
                    Led.turn_off()
                elif Led.half_period < pass_time < Led.half_period * 2:
                    Led.turn_on()
                elif pass_time > Led.half_period * 2:
                    Led.counter += 1
                    Led.turn_off()
            elif self.evoke_duration < trial_time < self.trial_duration:
                Led.turn_off()
                print("%s: count %d" % (Led.name, Led.counter))
                break
            trial_time = time.time() - trial_timer
        Led.counter = 0


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    system = ServerWindow()
    system.show()
    sys.exit(app.exec_())
