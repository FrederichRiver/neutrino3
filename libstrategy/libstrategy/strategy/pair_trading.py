#!/usr/bin/python3
"""
Pair Trading Method
"""
from abc import ABCMeta
from datetime import datetime, timedelta, date
from typing import Tuple
from libmysql_utils.header import LOCAL_HEADER
from libmysql_utils.mysql8 import mysqlBase, mysqlHeader, mysqlQuery
import pandas
from pandas import DataFrame
from pandas import isnull
from libbasemodel.form import formStockManager
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from pandas.core.series import Series
from libstrategy.utils.anzeichen import SignalBase, SignalPairTrade
from libstrategy.utils.order import TradeOrder
from libstrategy.data_engine.data_engine import StockData
from libutils.utils import f2percent
from pykalman import KalmanFilter

# 0. 数据准备 load from strategy_utils
# 1. 寻找相关性
# 2. 判定协整关系
# 基于ENGLE-GRANGER两步法
# ADF假设检验方法

def capital_relativity(df_a: Series, df_b: Series):
    """
    输入股票代码，返回一个列表，包括相关的资产，以及相关系数
    """
    df_matrix = pandas.concat([df_a, df_b], axis=1)
    df_matrix.dropna(how='any', axis=0, inplace=True)
    return df_matrix.corr().iloc[0, 1]


def cointegration_check(df_a: Series, df_b: Series):
    """
    对两个资产进行协整检验
    """
    x_add = sm.add_constant(df_b)
    model = sm.OLS(df_a, x_add).fit()
    # epsilon = y - beta * x - alpha
    e = df_a - model.params[1] * df_b - model.params[0]
    ADF = adfuller(e)
    if ADF[0] < ADF[4].get('1%'):
        result = 0.99
    elif ADF[0] < ADF[4].get('5%'):
        result = 0.95
    elif ADF[0] < ADF[4].get('10%'):
        result = 0.9
    else:
        result = 0
    std = np.std(e)
    return result, model.params[1], model.params[0], std


class Kalman(object):
    def __init__(self, observe) -> None:
        self.kf = KalmanFilter(
            transition_matrices=np.array([[1, 0], [0, 1]]),
            observation_matrices=observe
        )
        self.mean = 0.0
        self.cov = 0.0

    def init_param(self, data: Series):
        """
        初始化卡尔曼滤波过程
        """
        np.random.seed(0)
        self.kf.em(data)
        mean, cov = self.kf.filter(data)
        return mean, cov

    def update(self, y, x) -> np.ndarray:
        """
        更新系数并返回参数[alpha, beta]
        """
        H = np.array([[1, x]])
        y = y
        # 更新均值和协方差
        self.mean, self.cov = self.kf.filter_update(
            filtered_state_mean = self.mean,
            filtered_state_covariance = self.cov,
            observation = y,
            observation_matrix = H)
        return self.mean


def kalman_param_evalue(df: DataFrame):
    """
    用于卡尔曼滤波的参数初始化。
    df col "A", "B"
    """
    observe = np.vstack(
        (np.ones(len(df)), df.loc[:, 'B'].values)
    ).T
    Shape = observe.shape
    observe = observe.reshape(Shape[0], 1, Shape[1])
    kf = KalmanFilter(
        transition_matrices=np.array([[1, 0], [0, 1]]),
        observation_matrices=observe
    )
    np.random.seed(0)
    kf.em(df[:, 'A'])
    mean, cov = kf.filter(df.loc[:, 'A'])
    return mean, cov

# 3. 参数调整
# 4. 创建标的库

# 5. 创建交易费率


# 6. 创建资产组合价值跟踪
# 7. 回测评估

class StrategyBase(metaclass=ABCMeta):
    def __init__(self, from_date: str, to_date: str ) -> None:
        self.from_date = from_date
        self.to_date = to_date
        self.signal = 1

    def Config(self, **args):
        raise NotImplementedError

    def isTradeStart(self, trade_date):
        return (self.from_date == trade_date.strftime('%Y-%m-%d'))

    def isTradeEnd(self, trade_date):
        return (self.to_date == trade_date.strftime('%Y-%m-%d'))

    def built(self, signal: bool):
        self.signal = 0 if signal else 1
    # trade with dividend, increase... accept signal=-2

class PairTradeStrategy(StrategyBase):
    """
    v 1.0
    to Do: 完善注释
    Strategy class
    """
    def __init__(self, stock_1: str, stock_2: str, from_date, to_date ) -> None:
        super(PairTradeStrategy, self).__init__(from_date, to_date)
        self._state = 0
        self._high = 0.0
        self._low = 0.0
        self.beta = 0.0
        self.alpha = 0.0
        self.trade_list = []

    def Config(self, alpha: float, beta: float, **args):
        self.alpha = alpha
        self.beta = beta

    def update_param(self):
        # to Do
        # Kalman Filter method.
        self.alpha = 0
        self.beta = 0

    def param_evalue(cls):
        # to Do
        # Using KF方法估计参数
        pass
        # return 参数

    def add_trade(self, trade_msg: list):
        self.trade_list.extend(trade_msg)

    def __str__(self) -> str:
        text = ''
        for m in self.trade_list:
            text += m.__str__()
        return text

    def set_threshold(self, **kwargs):
        self._high = kwargs.get('high')
        self._low = kwargs.get('low')
        self.beta = kwargs.get('beta')
        self.alpha = kwargs.get('alpha')

    def run(self,trade_date, price_1: float, price_2: float):
        if self.isTradeStart(trade_date):
            return 3
        d = price_1 - self.beta * price_2 - self.alpha
        if (d > self._high) and (self._state != 1):
            self._state = 1
            return 1
        elif (d < self._low) and (self._state != 2):
            self._state = 2
            return 2
        else:
            return 0

class BenchMarkStrategy(StrategyBase):
    """
    Strategy class
    """
    def __init__(self, stock_id: str, from_date, to_date ) -> None:
        super(BenchMarkStrategy, self).__init__(from_date, to_date)
        self._ratio = 0.0
        self.stock_id = stock_id
        self.quant_1 = 0
        self.trade_list = []
        self.Today = from_date

    def add_trade(self, trade_msg: list):
        self.trade_list.extend(trade_msg)

    def __str__(self) -> str:
        text = ''
        for m in self.trade_list:
            text += m.__str__()
        return text

    def run(self,trade_date):
        if self.isTradeEnd(trade_date):
            return -1
        else:
            return self.signal

