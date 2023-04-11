# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : GUI_utils.py
@Project  : example_benckmark_ecca.py
@Time     : 2023/4/5 18:01
@Author   : Li JiaYi
@Software : PyCharm
@License  : (C)Copyright 2020-2030
@Last Modify Time      @Version     @Desciption
--------------------       --------        -----------
2023/4/5 18:01        1.0             None
"""
import socket

from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QMessageBox


def get_host_ip() -> str:
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip





if __name__ == '__main__':
    pass
