#!/usr/bin/python3
"""
Pair Trading Method
"""
from abc import ABCMeta
from datetime import datetime, timedelta, date
from libmysql_utils.header import LOCAL_HEADER
from libmysql_utils.mysql8 import mysqlBase, mysqlHeader, mysqlQuery
import pandas
from pandas import DataFrame
from pandas import isnull
from libbasemodel.form import formStockManager
import numpy as np
from statsmodels.tsa.stattools import adfuller
from pandas.core.series import Series
from libstrategy.utils.anzeichen import SignalBase, SignalPairTrade
from libstrategy.utils.order import TradeOrder
from libstrategy.data_engine.data_engine import StockData
from libutils.utils import f2percent

# from libstrategy.strategy_utils import StockPrice


# 0. 数据准备 load from strategy_utils
# 1. 寻找相关性
# 2. 判定协整关系
# 基于ENGLE-GRANGER两步法
# ADF假设检验方法
def cointegration():
    # import matplotlib.pyplot as plt
    event = StockData(LOCAL_HEADER)
    bm = event.get_log_price('SH600000', start='2019-01-01', end='2019-04-01')
    # event.profit_matrix('SZ002460', bm)
    df = event.get_log_price('SH601988', start='2019-01-01', end='2019-04-01')
    # event.profit_matrix('SZ002466', df)
    df_matrix = pandas.concat([bm, df], axis=1)
    df_matrix.dropna(how='any', axis=0, inplace=True)
    # r = df_matrix.corr().iloc[0, 1]
    df_matrix['div'] = df_matrix['SH600000'] - df_matrix['SH601988']
    # df_matrix['div'].plot()
    # plt.plot(bm, df)
    # plt.show()

    import statsmodels.api as sm
    x_add = sm.add_constant(df_matrix['SH600000'])
    model = sm.OLS(df_matrix['SH601988'], x_add).fit()
    # print("statsmodel.api.OLS:", model.params[:])
    # print(model.summary())
    # y = beta * x + b + epsilon
    df_matrix['div'] = df_matrix['SH601988'] - model.params[1] * df_matrix['SH600000'] - model.params[0]
    df_matrix['signal'] = 0
    high_th = 0.02
    low_th = -0.02
    state = 0
    for index, row in df_matrix.iterrows():
        if (row['div'] > high_th) and (state != 1):
            df_matrix.loc[index, 'signal'] = 1
            state = 1
        elif (row['div'] < low_th) and (state != -1):
            df_matrix.loc[index, 'signal'] = -1
            state = -1
    epsilon = df_matrix['div']
    from statsmodels.tsa.stattools import adfuller
    result = adfuller(epsilon)
    # 生成adf检验结果
    # print(result)
    # print('The ADF Statistic: %f' % result[0])
    # print('The p value: %f' % result[1])
    import numpy as np
    width = 1.5
    mu = np.mean(epsilon)
    sd = np.std(epsilon)
    UpperBound = mu + width * sd
    LowerBound = mu - width * sd
    # print(UpperBound, LowerBound)
    df_matrix['signal'].plot()
    # plt.show()
    beta = model.params[1]
    a = 0
    for index, row in df_matrix.iterrows():
        if row['signal'] == 1:
            print('SH601988', row['SH601988'], -100)
            print('SH600000', row['SH600000'], 100 * beta)
            a += row['SH600000'] * 100 * beta - row['SH601988'] * 100
        elif row['signal'] == -1:
            print('SH601988', row['SH601988'], 100)
            print('SH600000', row['SH600000'], -100 * beta)
            a += row['SH601988'] * 100 - row['SH600000'] * 100 * beta
    print(a)

# 3. 参数调整
# 4. 创建标的库

# 5. 创建交易费率


# 6. 创建资产组合价值跟踪
# 7. 回测评估

class StrategyBase(metaclass=ABCMeta):
    def __init__(self, from_date, to_date ) -> None:
        self.from_date = from_date
        self.to_date = to_date


class PairTradeStrategy(StrategyBase):
    """
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

    def add_trade(self, trade_msg: list):
        self.trade_list.extend(trade_msg)

    def __str__(self) -> str:
        text = ''
        for m in self.trade_list:
            text += m.__str__()
        return text

    @staticmethod
    def capital_relativity(df_a: Series, df_b: Series):
        """
        输入股票代码，返回一个列表，包括相关的资产，以及相关系数
        """
        df_matrix = pandas.concat([df_a, df_b], axis=1)
        df_matrix.dropna(how='any', axis=0, inplace=True)
        return df_matrix.corr().iloc[0, 1]

    @staticmethod
    def cointegration_check(df_a: Series, df_b: Series):
        """
        对两个资产进行协整检验
        """
        import statsmodels.api as sm
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

    def set_threshold(self, **kwargs):
        self._high = kwargs.get('high')
        self._low = kwargs.get('low')
        self.beta = kwargs.get('beta')
        self.alpha = kwargs.get('alpha')

    def __call__(self, a: float, b: float) -> None:
        d = a - self.beta * b - self.alpha
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

    def isTradeStart(self, trade_date):
        return (self.from_date == trade_date.strftime('%Y-%m-%d'))

    def isTradeEnd(self, trade_date):
        return (self.to_date == trade_date.strftime('%Y-%m-%d'))

    def run(self,trade_date):
        if self.isTradeEnd(trade_date):
            return -1
        elif self.isTradeStart(trade_date):
            return 1
        else:
            return 0


class BackTest(object):
    def __init__(self, strategy: StrategyBase) -> None:
        super().__init__()
        self.trade = []
        self.strategy = strategy
        self.init_cash = 0.0
        self.annualized_return = 0.0
        self.total_return = 0.0
        self.max_draw = 0.0
        self.period = self._time_delta()

    def get_trade_data(self, trade: list):
        self.trade = trade

    def _time_delta(self) -> timedelta:
        self.period = datetime.strptime(self.strategy.to_date, '%Y-%m-%d') - datetime.strptime(self.strategy.from_date, '%Y-%m-%d')
        return self.period

    def print_annual_return(self):
        # self.annualized_return = self.total_return * 250 / self.period.days
        self.annualized_return = (1 + self.total_return) ** (250 / self.period.days) -1 
        f = f2percent(self.annualized_return)
        print(f"Annualized Return: {f}")

    def report(self):
        profit = 0.0
        for m in self.trade:
            profit += m.price * m.bid
        self.total_return = profit / self.init_cash
        self.print_annual_return()


class InvestmentGroup(object):
    def __init__(self) -> None:
        super().__init__()
        self.pool = []

    def add_capital(self, stock_code: str):
        self.pool.append(stock_code)


def backtest2():
    head = mysqlHeader(acc='stock', pw='stock2020', db='stock', host='115.159.1.221')
    start = '2020-01-01'
    end = '2021-05-28'
    stock_market = StockData(head , start, end)
    print(stock_market)
    # A = 'SH600000'
    # B = 'SH601988'
    A = 'SZ002460'
    B = 'SZ002497'
    stock_market.add_asset(A)
    stock_market.add_asset(B)
    stock_market.update()
    Trade = PairTradeStrategy(A, B, '2019-01-01', '2021-03-01')
    result, beta, mean, std = Trade.cointegration_check(stock_market.data[A], stock_market.data[B])
    print(mean, std)
    Signal = SignalPairTrade()
    Signal.set_threshold(high=std, low=-std, beta=beta, alpha=mean)
    print(Signal.signal)
    for index, row in stock_market:
        Signal.get_data(row[A], row[B])
        Trade.trade(Signal, row[A], row[B])
        # print(Signal.signal)
    Signal.set_end()
    print(Trade)
    backtest = BackTest(Trade)
    backtest.get_trade_data(Trade.trade_list)
    backtest.report()


if __name__ == '__main__':
    # cointegration()
    # param_adjust()
    backtest2()
