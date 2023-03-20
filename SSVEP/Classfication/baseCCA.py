# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : baseCCA.py
@Project  : NanoBCIRobitics
@Time     : 2023/3/20 13:55
@Author   : Li JiaYi
@Software : PyCharm
@License  : (C)Copyright 2020-2030
@Last Modify Time      @Version     @Desciption
--------------------       --------        -----------
2023/3/20 13:55        1.0             None
"""

from abc import abstractmethod, ABCMeta

# %% Basic CCA object
class BasicCCA(metaclass=ABCMeta):
    def __init__(self, data, fs=1000):
        '''
        基础CCA类

        -------------
        :param data: 脑电数据，注意输入的格式为[通道x时间点x事件x试验]
        :param fs: 采样频率(float)，单位赫兹，默认是1kHz
        '''
        # config model
        self.data = data
        self.fs = fs



    @abstractmethod
    def fit(self, X_train, y_train):
        pass


    @abstractmethod
    def predict(self, X_test, y_test):
        pass

    @abstractmethod
    def leave_one(self, selected_trial):
        pass


if __name__ == '__main__':
    pass
