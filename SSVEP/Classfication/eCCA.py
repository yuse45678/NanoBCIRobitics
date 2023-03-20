# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : eCCA.py
@Project  : NanoBCIRobitics
@Time     : 2023/3/19 22:14
@Author   : Li JiaYi
@Software : PyCharm
@License  : (C)Copyright 2020-2030
@Last Modify Time      @Version     @Desciption
--------------------       --------        -----------
2023/3/19 22:14        1.0             重构项目
"""
import numpy as np
from .utils import timer, sine_template
from SSVEP.Classfication.baseCCA import BasicCCA


class eCCA(BasicCCA):
    """
    - 集成典型相关分析算法

    -------------------

    - 引用：Nakanishi M., Wang Y., Wang Y.T., et al. A High-Speed Brain Speller Using Steady-State Visual Evoked Potentials[J]. International Journal of Neural Systems, 2014, 24(6):767–2179.
    - 创建时间: 2022/09/21 11:19
    ------------------

    - 更新日志:
        - 2022/09/21 16:47  Li JiaYi    完成导入数据集并且复现算法
        - 2022/10/23 17:09  Li JiaYi    重构测试代码结构并优化
        - 2023/3/19 22:14   Li JiaYi    重构项目并修改部分错误
    """

    def __init__(self, data, freqsList, n_harmonics, fs=1000):
        '''
        eCCA初始化

        -----------------------------------
        :param data: 脑电数据，注意输入的格式为[通道x时间点x事件x试验]
        :param freqsList: 正弦波频率(float),单位赫兹
        :param n_harmonics: 正余弦模板谐波数量
        :param fs: 采样频率(float)，单位赫兹，默认是1kHz
        '''
        super().__init__(data, fs)
        [self.nChannels, self.nTimes, self.nEvents, self.nTrials] = self.data.shape
        self.TrainData = np.zeros((self.nChannels, self.nTimes, self.nEvents, self.nTrials - 1))
        self.TestData = np.zeros((self.nChannels, self.nTimes, self.nEvents, 1))
        self.f_list = freqsList
        self.template = np.zeros((len(freqsList), 2 * n_harmonics, self.nTimes))
        for nf, freq in enumerate(freqsList):
            self.template[nf, ...] = sine_template(freq=freq, phase=0, nPoints=self.nTimes, nHarmonics=n_harmonics,
                                                   sfreq=fs).T

    @timer
    def fit(self):
        pass

    def leave_one(self, selected_trial):
        index = 0
        for i in range(self.nTrials):
            if selected_trial == i:
                self.TestData[:, :, :, 0] = self.data[:, :, :, selected_trial]
            else:
                self.TrainData[:, :, :, index] = self.data[:, :, :, i]
                index += 1

    def __corr_coef_1D(self, X, y):
        """
        皮尔森相关系数计算函数
        ------------------------

        :param X: (ndarray): (m, n_points)
        :param y: (ndarray): (1, n_points)
        :return: Pearson_Correlation_Coefficient: (ndarray): (1,m)
        """
        cov_yX = y @ X.T
        std_XX = np.sqrt(np.diagonal(X @ X.T))
        std_yy = np.sqrt(y @ y.T)
        Pearson_Correlation_Coefficient = cov_yX / (std_XX * std_yy)
        return Pearson_Correlation_Coefficient

    def __cca_compute(self, X, Y):
        # GEP
        Cxx = X @ X.T  # (Nc,Nc)
        Cyy = Y @ Y.T  # (2Nh,2Nh)
        Cxy = X @ Y.T  # (Nc,2Nh)
        Cyx = Y @ X.T  # (2Nh,Nc)
        # AU = lambda*U
        A = np.linalg.solve(Cxx, Cxy) @ np.linalg.solve(Cyy, Cyx)
        # Bv = lambda*V
        B = np.linalg.solve(Cyy, Cyx) @ np.linalg.solve(Cxx, Cxy)
        # EEG part
        e_val, e_vec = np.linalg.eig(A)
        U = e_vec[:, [np.argmax(e_val)]].T  # (1,Nc)

        # template part
        e_val, e_vec = np.linalg.eig(B)
        V = e_vec[:, [np.argmax(e_val)]].T  # (1,2Nh)
        return U, V

    def __ecca_compute(self, Xmean, Y, data):
        # correlation coefficient from CCA process
        U1, V1 = self.__cca_compute(X=data, Y=Y)
        r1 = self.__corr_coef_1D(U1 @ data, V1 @ Y)[0, 0]

        # correlation coefficients between single-trial EEG and SSVEP templates
        U2, V2 = self.__cca_compute(X=data, Y=Xmean)  # (1,Nc)
        r2 = self.__corr_coef_1D(U2 @ data, U2 @ Xmean)[0, 0]

        # U3, _ = cca(X=data, Y=Y)  # (1,Nc)
        r3 = self.__corr_coef_1D(U1 @ data, U1 @ Xmean)[0, 0]

        U4, _ = self.__cca_compute(X=Xmean, Y=Y)  # (1,Nc)
        r4 = self.__corr_coef_1D(U4 @ data, U4 @ Xmean)[0, 0]
        # combined features
        res = self._combine_feature([r1, r2, r3, r4])
        return res

    def _combine_feature(self, X):
        """Two-level feature extraction.

        Args:
            X (list of float): List of one-level features.

        Returns:
            tl_feature (float): Two-level feature.
        """
        tl_feature = 0
        for feature in X:
            sign = abs(feature) / feature  # sign(*) function
            tl_feature += sign * (feature ** 2)
        return tl_feature

    @timer
    def predict(self):
        # n_chans * n_samples * n_classes * n_trials
        train_data = np.transpose(self.TrainData, [2, 3, 0, 1])
        test_data = np.transpose(self.TestData, [2, 3, 0, 1])
        n_events = self.TrainData.shape[2]
        n_trial = self.TestData.shape[3]
        res = np.zeros((n_events, n_trial, n_events))
        for event in range(n_events):
            for trial in range(n_trial):
                temp_data = test_data[event, trial, ...]
                for eventn in range(n_events):
                    Xmean = train_data[eventn, ...].mean(axis=0)
                    res[event, trial, eventn] = self.__ecca_compute(Xmean, self.template[eventn, ...], temp_data)
        return res


if __name__ == '__main__':
    pass
