#!/usr/bin/python3
"""
Pair Trading Method
"""
from abc import ABCMeta
from datetime import datetime, timedelta, date
from typing import Tuple
from libmysql_utils.header import LOCAL_HEADER
from libmysql_utils.mysql8 import mysqlBase, mysqlHeader, mysqlQuery
from numpy.ma import mean
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
    def __init__(self, df) -> None:
        """
        初始化卡尔曼滤波过程
        """
        # 构造观测矩阵
        observe = np.vstack(
            (np.ones(len(df)), df.loc[:, 'B'].values)
        ).T
        Shape = observe.shape
        observe = observe.reshape(Shape[0], 1, Shape[1])
        # 构造转移矩阵
        # 初始化参数，期望和协方差
        self.kf = KalmanFilter(
            transition_matrices=np.array([[1, 0], [0, 1]]),
            observation_matrices=observe
            # em_vars= ['transition_matrices', 'observation_matrices']
        )
        np.random.seed(0)
        self.kf.em(df['A'])
        m, c = self.kf.filter(df['A'])
        self.mean = m[-1]
        self.cov = c[-1] 



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
        observation_matrices=np.array(observe)
    )
    np.random.seed(0)
    kf.em(df[:, 'A'])

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
    def __init__(self, stock_1: str, stock_2: str, from_date, to_date, c ) -> None:
        super(PairTradeStrategy, self).__init__(from_date, to_date)
        self._state = 0
        self._high = 0.0
        self._low = 0.0
        self.beta = 0.0
        self.alpha = 0.0
        self.trade_list = []
        self.c = c
        self.std = 0.0
        self.var = []

    def Config(self, alpha: float, beta: float, **args):
        self.alpha = alpha
        self.beta = beta

    def init_param(self, df: DataFrame):
        self.KF = Kalman(df)
        self.beta = self.KF.kf.initial_state_mean[1]
        self.alpha = self.KF.kf.initial_state_mean[0]

    def update_param(self, y: float, x: float):
        # to Do
        # Kalman Filter method.
        self.KF.update(y, x)
        self.alpha = self.KF.mean[0]
        self.beta = self.KF.mean[1]
        
    def add_trade(self, trade_msg: list):
        self.trade_list.extend(trade_msg)

    def __str__(self) -> str:
        text = ''
        for m in self.trade_list:
            text += m.__str__()
        return text

    def run(self,trade_date, price_1: float, price_2: float):
        if self.isTradeStart(trade_date):
            return 3
        self.update_param(price_1, price_2)
        d = price_1 - self.beta * price_2 - self.alpha
        self.var.append(d)
        if len(self.var) > 20:
            self.var.pop(0)
        z = zscore(self.var)
        print(z)
        if (z > self.c) and (self._state != 1):
            self._state = 1
            return 1
        elif (z < (-1 * self.c)) and (self._state != 2):
            self._state = 2
            return 2
        else:
            return 0

def zscore(x: list):
    df = Series(x).fillna(0)
    z = (df - df.mean()) / np.std(df)
    return np.array(z)[0]

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

