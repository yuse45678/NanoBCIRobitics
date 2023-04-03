# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : utils.py
@Project  : NanoBCIRobitics
@Time     : 2023/4/3 18:01
@Author   : Li JiaYi
@Software : PyCharm
@License  : (C)Copyright 2020-2030
@Last Modify Time      @Version     @Desciption
--------------------       --------        -----------
2023/4/3 18:01        1.0             None
"""

def mapping(x, in_min, in_max, out_min, out_max):  # change a num(0-255) to (0-100).
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min



if __name__ == '__main__':
    pass
