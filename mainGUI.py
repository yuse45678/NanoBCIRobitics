# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : mainGUI.py
@Project  : NanoBCIRobitics
@Time     : 2023/4/5 18:09
@Author   : Li JiaYi
@Software : PyCharm
@License  : (C)Copyright 2020-2030
@Last Modify Time      @Version     @Desciption
--------------------       --------        -----------
2023/4/5 18:09        1.0             None
"""
import sys
import random
import time

import serial
import serial.tools.list_ports
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QMessageBox
from gui_lib.GUI import Ui_MainWindow
from gui_lib.GUI_utils import get_host_ip
from SSVEP.Inspire.RaspberryPi import LED, loop_remote


class System(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.IPtextBrowser.insertPlainText(get_host_ip())
        self.get_serial_info()
        self.setWindowIcon(QIcon('文件.png'))
        self.offlineBeginButton.clicked.connect(self.offlineButtonClicked)

    def get_serial_info(self):  # 获取可用串口列表

        # 打印可用串口列表
        # self.need_serial = ''

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

    def offlineButtonClicked(self):
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)

            self.offlineTextBrowser.clear()
            self.printf(self.offlineTextBrowser, "正在加载中")
            self.sleep(1000)

            Ntrial = 10
            trial_duration=4
            evoke_duration=3
            self.offlineTextBrowser.clear()
            self.printf(self.offlineTextBrowser, "感谢参加本次实验，本次实验共{}组试验".format(Ntrial))
            self.printf(self.offlineTextBrowser, "每组试验共四次闪烁，请按照提示依次注视LED灯")
            self.sleep(1000)
            self.sleep(1000)

            for i in range(Ntrial):
                self.printf(self.offlineTextBrowser, "--" * 50)
                self.offlineTextBrowser.append("当前为试验为第{}次".format(i + 1))
                self.sleep(1000)
                sequence = random.sample(range(1, 5), 4)
                for seq in sequence:
                    if seq == 1:
                        self.printf(self.offlineTextBrowser, "请注视上面的LED灯，两秒后开始闪烁！")
                        self.sleep(2000)
                        self.printf(self.offlineTextBrowser, "开始闪烁！")

                        trial_timer = time.time()
                        Led1 = LED([12, 18, 16], "Led1").set_color(LED.YELLOW).set_evoke_fre(40)
                        loop_remote(trial_timer, [Led1], trial_duration, evoke_duration)
                        Led1.pwm_clear()
                    elif seq == 2:
                        self.printf(self.offlineTextBrowser, "请注视下面的LED灯，两秒后开始闪烁！")
                        self.sleep(2000)
                        self.printf(self.offlineTextBrowser, "开始闪烁！")
                        trial_timer = time.time()
                        Led4 = LED([11, 15, 13], "Led4").set_color(LED.YELLOW).set_evoke_fre(35)
                        loop_remote(trial_timer, [Led4], trial_duration, evoke_duration)
                        Led4.pwm_clear()
                    elif seq == 3:
                        self.printf(self.offlineTextBrowser, "请注视右边的LED灯，两秒后开始闪烁！")
                        self.sleep(2000)
                        self.printf(self.offlineTextBrowser, "开始闪烁！")
                        trial_timer = time.time()
                        Led2 = LED([35, 38, 37], "Led2").set_color(LED.YELLOW).set_evoke_fre(20)
                        loop_remote(trial_timer, [Led2], trial_duration, evoke_duration)
                        Led2.pwm_clear()
                    elif seq == 4:
                        self.printf(self.offlineTextBrowser, "请注视左边的LED灯，两秒后开始闪烁！")
                        self.sleep(2000)
                        self.printf(self.offlineTextBrowser, "开始闪烁！")
                        trial_timer = time.time()
                        Led3 = LED([22, 36, 32], "Led3").set_color(LED.YELLOW).set_evoke_fre(30)
                        loop_remote(trial_timer, [Led3], trial_duration, evoke_duration)
                        Led3.pwm_clear()
                    GPIO.cleanup()
                    self.printf(self.offlineTextBrowser, "休息时间：5s")
                    self.printf(self.offlineTextBrowser, "--" * 50)
                    self.sleep(5000)


        except Exception as e:
            self.offlineTextBrowser.insertPlainText(e)


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    system = System()
    system.show()
    sys.exit(app.exec_())
