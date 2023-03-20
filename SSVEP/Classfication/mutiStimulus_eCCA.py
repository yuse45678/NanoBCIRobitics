# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : mutiStimulus_eCCA.py
@Project  : NanoBCIRobitics
@Time     : 2023/3/19 23:35
@Author   : Li JiaYi
@Software : PyCharm
@License  : (C)Copyright 2020-2030
@Last Modify Time      @Version     @Desciption
--------------------       --------        -----------
2023/3/19 23:35        1.0             None
"""

import numpy as np
import math

from SSVEP.Classfication.baseCCA import BasicCCA
from .utils import timer


def cal_CCA(X, Y):
    """ CCA count
    :param X: (num of sample points * num of channels1 )
    :param Y: (num of sample points * num of channels2 )
    :return:
    """

    #  Center the variables
    if X.ndim == 1:
        Xnew = X.reshape(X.shape[0], 1)  # reshape（num of sample points）to（num of sample points * 1）
        del X
        X = Xnew
        X = X - np.tile(np.mean(X, 0), (X.shape[0], 1))
    else:
        X = X - np.tile(np.mean(X, 0), (X.shape[0], 1))

    if Y.ndim == 1:
        Ynew = Y.reshape(Y.shape[0], 1)  # reshape（num of sample points）to（num of sample points * 1）
        del Y
        Y = Ynew
        Y = Y - np.tile(np.mean(Y, 0), (Y.shape[0], 1))
    else:
        Y = Y - np.tile(np.mean(Y, 0), (Y.shape[0], 1))

    #  Calculate corr_cca
    P_U = Y @ np.linalg.inv(Y.T @ Y) @ Y.T
    b_U = (np.linalg.inv(X.T @ X)) @ (X.T @ P_U @ X)
    [eig_value_U, eig_U] = np.linalg.eig(b_U)  # Calculate U
    U = eig_U[:, 0]
    P_V = X @ np.linalg.inv(X.T @ X) @ X.T
    b_V = (np.linalg.inv(Y.T @ Y)) @ (Y.T @ P_V @ Y)
    [eig_value_V, eig_V] = np.linalg.eig(b_V)  # Calculate V
    V = eig_V[:, 0]

    corr = np.corrcoef(U.T @ X.T, V.T @ Y.T)
    corr_cca = corr[0, 1]
    return U.real, V.real, corr_cca.real


class mutiStimulus_eCCA(BasicCCA):

    def __init__(self, data: dict, nTemplates: int, fs: int, freqsList, phaseList, Nh: int):
        """
        :param data:
        :param nTemplates:    the number of neighboring frequencies
        :param fs:            the sample rate
        :param freqsList:        the all frequency of reference signal
        :param phaseList:      the all phase of reference signal
        :param Nh:            the number of harmonics
        """
        super().__init__(data, fs)
        self.Xmean = dict()
        self.V = dict()
        self.U = dict()
        self.trainData = dict()
        self.testData = dict()
        self.freqsList = freqsList
        self.phaseList = phaseList
        self.Nh = Nh
        self.nTemplates = nTemplates
        self.nBank = len(data)
        for bank in data:
            data = data[bank]
            [self.nChannels, self.nTimes, self.nEvents, self.nTrials] = data.shape
            traindata = np.zeros((self.nChannels, self.nTimes, self.nEvents, self.nTrials - 1))
            testdata = np.zeros((self.nChannels, self.nTimes, self.nEvents, 1))
            for i in range(self.nTrials - 1):
                traindata[:, :, :, i] = data[:, :, :, i]
            testdata[:, :, :, 0] = data[:, :, :, self.nTrials - 1]
            self.trainData[bank] = traindata
            self.testData[bank] = testdata
            del traindata, testdata

    def leave_one(self, selectedTrial):
        for bank in self.data:
            data = self.data[bank]
            traindata = np.zeros((self.nChannels, self.nTimes, self.nEvents, self.nTrials - 1))
            testdata = np.zeros((self.nChannels, self.nTimes, self.nEvents, 1))
            index = 0
            for i in range(self.nTrials):
                if selectedTrial == i:
                    testdata[:, :, :, 0] = data[:, :, :, selectedTrial]
                else:
                    traindata[:, :, :, index] = data[:, :, :, i]
                    index += 1
            self.trainData[bank] = traindata
            self.testData[bank] = testdata
            del traindata, testdata

    def ms_eCCA_spatialFilter(self, mean_temp_all, iEvent):
        """
        @Author:https://github.com/RuixinLuo/transfer-learning-canonical-correlation-analysis-tlCCA--python

        -------------------------------

        spatialFilter for multi-stimulus extended canonical correlation analysis (ms-eCCA)
        adopted from https://github.com/edwin465/SSVEP-MSCCA-MSTRCA

        :param mean_temp_all: ndarray(n_channels, n_times, n_events)
        :param iEvent:        the i-th event for the selection of neighboring frequencies
        :return:  U, V        Spatial Filters
        """

        mean_temp_all = np.transpose(mean_temp_all, [1, 0, 2])

        [nTimes, nChannels, nEvents] = mean_temp_all.shape
        d0 = self.nTemplates / 2
        d1 = nEvents

        n = iEvent + 1
        if n <= d0:
            template_st = 1
            template_ed = self.nTemplates
        elif (n > d0) & (n < (d1 - d0 + 1)):
            template_st = n - d0
            template_ed = n + (self.nTemplates - d0 - 1)
        else:
            template_st = (d1 - self.nTemplates + 1)
            template_ed = d1
        template_st = int(template_st - 1)
        template_ed = int(template_ed)

        #  Concatenation of the templates (or sine-cosine references)
        mscca_ref = np.zeros((self.nTemplates * nTimes, 2 * self.Nh))
        mscca_template = np.zeros((self.nTemplates * nTimes, nChannels))

        index = 0
        for j in range(template_st, template_ed, 1):
            # sine-cosine references
            f = self.freqsList[j]
            phi = self.phaseList[j]
            Ts = 1 / self.fs
            n = np.arange(nTimes) * Ts
            Yf = np.zeros((nTimes, self.Nh * 2))
            for iNh in range(self.Nh):
                y_sin = np.sin(2 * np.pi * f * (iNh + 1) * n + (iNh + 1) * np.pi * phi)
                Yf[:, iNh * 2] = y_sin
                y_cos = np.cos(2 * np.pi * f * (iNh + 1) * n + (iNh + 1) * np.pi * phi)
                Yf[:, iNh * 2 + 1] = y_cos
            mscca_ref[index * nTimes: (index + 1) * nTimes, :] = Yf
            # templates
            ss = mean_temp_all[:, :, j]
            # ss = ss - np.tile(np.mean(ss, 0), (ss.shape[0], 1))
            mscca_template[index * nTimes:(index + 1) * nTimes, :] = ss
            index = index + 1

        # calculate U and V
        U, V, r = cal_CCA(mscca_template, mscca_ref)

        if r < 0:  # Symbol Control
            V = -V

        return U, V


    @timer
    def fit(self):
        for bank in self.trainData:
            # bank (channel,times,event,trial)
            data = self.trainData[bank]
            U = np.zeros((self.nChannels, self.nEvents))
            V = np.zeros((self.Nh * 2, self.nEvents))
            for iEvent in range(self.nEvents):
                # multistimulus_mutisetCCA: u,v
                u, v = self.ms_eCCA_spatialFilter(np.mean(data, -1), iEvent=iEvent)
                U[:, iEvent] = u
                V[:, iEvent] = v
            self.U[bank] = U
            self.V[bank] = V
            self.Xmean[bank] = np.mean(data, -1)

    @timer
    def predict(self):
        b = 1
        res = np.zeros((self.nEvents, self.nEvents))
        for bank in self.testData:
            data = self.testData[bank]
            U = self.U[bank]
            V = self.V[bank]
            Xmean = self.Xmean[bank]
            # sine-cosine references
            Ts = 1 / self.fs
            n = np.arange(self.nTimes) * Ts
            for real_event in range(self.nEvents):
                if Xmean.ndim == 3:
                    X_mean = Xmean[:, :, real_event]
                else:
                    X_mean = Xmean[:, :, real_event, 0]
                test_data = data[:, :, real_event, 0]  # (channel,timepoint)
                for test_event in range(self.nEvents):
                    u = U[:, test_event]  # (channel,1)
                    v = V[:, test_event]  # (2*Nh,1)
                    # 生成参考信号
                    f = self.freqsList[test_event]
                    phi = self.phaseList[test_event]
                    Yf_cca = np.zeros((self.nTimes, self.Nh * 2))
                    for iNh in range(self.Nh):
                        y_sin = np.sin(2 * np.pi * f * (iNh + 1) * n + (iNh + 1) * np.pi * phi)
                        Yf_cca[:, iNh * 2] = y_sin
                        y_cos = np.cos(2 * np.pi * f * (iNh + 1) * n + (iNh + 1) * np.pi * phi)
                        Yf_cca[:, iNh * 2 + 1] = y_cos
                    # 计算相关系数
                    rr1 = np.corrcoef(u.T @ test_data, v.T @ Yf_cca.T)[0, 1]
                    rr1 = (abs(rr1) / rr1) * (rr1 ** 2)
                    rr2 = np.corrcoef(u.T @ test_data, u.T @ X_mean)[0, 1]
                    rr2 = (abs(rr2) / rr2) * (rr2 ** 2)
                    w = math.pow(b, -1.25) + 0.25
                    res[real_event, test_event] += w * (rr1 + rr2) ** 2
        return res


if __name__ == '__main__':
    pass
