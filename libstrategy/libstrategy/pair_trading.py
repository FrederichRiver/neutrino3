#!/usr/bin/python38
"""
Pair Trading Method
"""
from datetime import datetime, timedelta, date
from libmysql_utils.mysql8 import LOCAL_HEADER, mysqlHeader
import pandas
from pandas import DataFrame
from pandas import isnull
from libmysql_utils.mysql8 import mysqlBase
from libbasemodel.form import formStockManager
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from pandas.core.series import Series
from libstrategy.signal import SignalBase, SignalPairTrade

# from libstrategy.strategy_utils import StockPrice


# 0. 数据准备 load from strategy_utils


class StockPrice(mysqlBase):
    """
    A smart application to get close price.
    : stock_code : benchmark code
    : header : header
    : return: result like DataFrame
    """
    def get_stock_list(self):
        query_stock_code = self.session.query(formStockManager.stock_code).filter_by(flag='t').all()
        df = DataFrame.from_dict(query_stock_code)
        stock_list = df['stock_code'].tolist()
        # should test if stock list is null
        return stock_list

    def get_log_price(self, stock_code: str, start='', end='') -> DataFrame:
        query_column = 'trade_date,close_price'
        def_column = ['trade_date', f"{stock_code}"]
        if start or end:
            result = self.condition_select(stock_code, query_column, f"(trade_date>'{start}') and (trade_date<'{end}')")
        else:
            result = self.select_values(stock_code, query_column)
        if not result.empty:
            result.columns = def_column
            result[stock_code].apply(np.log)
            result['trade_date'] = pandas.to_datetime(result['trade_date'])
            result.set_index('trade_date', inplace=True)
        else:
            result = DataFrame()
        return result

    def get_data(self, stock_code: str, query_type='close', start='', end='') -> DataFrame:
        if query_type == 'close':
            query_column = 'trade_date,close_price'
            def_column = ['trade_date', f"{stock_code}"]
        elif query_type == 'full':
            query_column = 'trade_date,open_price,close_price,high_price,low_price'
            def_column = ['trade_date', 'open', 'close', 'high', 'low']
        else:
            query_column = 'trade_date,open_price,close_price,high_price,low_price'
            def_column = ['trade_date', 'open', 'close', 'high', 'low']
        if start or end:
            result = self.condition_select(stock_code, query_column, f"(trade_date>'{start}') and (trade_date<'{end}')")
        else:
            result = self.select_values(stock_code, query_column)
        if not result.empty:
            result.columns = def_column
            result['trade_date'] = pandas.to_datetime(result['trade_date'])
            result.set_index('trade_date', inplace=True)
        else:
            result = DataFrame()
        return result

    def get_benchmark(self, stock_code: str) -> DataFrame:
        return self.get_data(stock_code, query_type='close')

    @classmethod
    def profit_matrix(cls, stock_code: str, df: DataFrame) -> DataFrame:
        df[stock_code] = df[stock_code] / df[stock_code].shift(1)
        return df

# 1. 寻找相关性


def relative_matrix():
    event = StockPrice(LOCAL_HEADER)
    stock_list = [f"SH000{str(i).zfill(3)}" for i in range(1, 29)]
    df_matrix = DataFrame()
    for stock in stock_list:
        df = event.get_data(stock)
        if not df.empty:
            event.profit_matrix(stock, df)
            df_matrix = pandas.concat([df_matrix, df], axis=1)
    df_matrix.dropna(how='any', axis=0, inplace=True)
    print(df_matrix.corr().to_markdown())


def test_relativity():
    event = StockPrice(LOCAL_HEADER)
    stock_list = event.get_stock_list()
    bm = event.get_data('SZ002460', query_type='close', start='2019-01-01', end='2020-01-01')
    event.profit_matrix('SZ002460', bm)
    # result = DataFrame(columns=['stock_code', 'r'])
    # stock_list = ['SZ002460']
    for stock in stock_list:
        df = event.get_data(stock, query_type='close', start='2019-01-01', end='2020-01-01')
        if not df.empty:
            event.profit_matrix(stock, df)
            df_matrix = pandas.concat([bm, df], axis=1)
            df_matrix.dropna(how='any', axis=0, inplace=True)
            r = df_matrix.corr().iloc[0, 1]
            if not isnull(r):
                """new = DataFrame({'stock_code': [stock], 'r': [r]}, columns=['stock_code', 'r'])
                result = result.append(new, ignore_index=True)"""
                # with open('/home/friederich/Dev/neutrino2/data/relative', 'a') as f:
                #    f.write(f"{stock}: %.3f\n" % r)
                if r > 0.6:
                    with open('/home/friederich/Dev/neutrino2/data/relative2', 'a') as f:
                        f.write(f"{stock}: %.3f\n" % r)


# 2. 判定协整关系
# 基于ENGLE-GRANGER两步法
# ADF假设检验方法
def cointegration():
    # import matplotlib.pyplot as plt
    event = StockPrice(LOCAL_HEADER)
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


def param_adjust():
    param = [0.001 * x for x in range(-50, 75)]
    print(param[:3])

# 4. 创建标的库


class Calendar(object):
    """
    一个迭代器，可以返回交易日的日期
    """
    def __init__(self, start: tuple) -> None:
        if start:
            self._start = date(start[0], start[1], start[2])
        else:
            self._start = date.today()
        self.holiday = []
        self.lawday = [(5, 14), ]

    def config(self):
        # 定义国家和地区，对应不同的假日(中国，美国，日本，香港，德国，英国，中东)
        # 定义交易品种(股票，期货等)
        pass

    def __str__(self) -> str:
        TODAY = datetime.strftime(self._start, '%Y-%m-%d')
        return TODAY

    def __next__(self):
        self._start += timedelta(days=1)
        while not self.is_tradeday(self._start):
            self._start += timedelta(days=1)
        return self._start

    def __iter__(self):
        return self

    @classmethod
    def eq(cls, a: date, o: object) -> bool:
        if isinstance(o, pandas._libs.tslibs.timestamps.Timestamp):
            if (a.year, a.month, a.day) == (o.year, o.month, o.day):
                result = True
            else:
                result = False
        else:
            result = False
        return result

    def is_holiday(self, d: date) -> bool:
        """
        判断是否是节日
        """
        return True if d in self.holiday else False

    def is_lawday(self, d: date) -> bool:
        if (d.month, d.day) in self.lawday:
            return True
        else:
            return False

    def is_weekend(self, d: date) -> bool:
        """
        判断是否是周末
        """
        return True if d.weekday() in [5, 6] else False

    def is_tradeday(self, d: date) -> bool:
        """
        如果是交易日，就返回True，否则返回False。这个API引用了is_holiday和is_weekend
        """
        return False if self.is_holiday(d) or self.is_weekend(d) else True

# 5. 创建交易费率


class TradeMessage(object):
    def __init__(self, stock_code: str, trade_time, price: float, bid: int) -> None:
        self.code = stock_code
        self.trade_time = trade_time
        self.price = price
        self.bid = bid

    def __str__(self) -> str:
        direction = "Buy" if self.bid > 0 else "Sell"
        text = f"{direction} {self.bid} {self.code} at price of {self.price}.\n"
        return text
# 6. 创建资产组合价值跟踪
# 7. 回测评估


class PairTrade(object):
    def __init__(self, stock_1: str, stock_2: str) -> None:
        self._ratio = 0.0
        self.stock_1 = stock_1
        self.quant_1 = 0
        self.stock_2 = stock_2
        self.quant_2 = 0
        self.trade_list = []

    def set_ratio(self, value):
        self._ratio = value

    def add_trade(self, trade_msg: list):
        self.trade_list.extend(trade_msg)

    def __str__(self) -> str:
        text = ''
        for m in self.trade_list:
            text += m.__str__()
        return text

    @classmethod
    def capital_relativity(cls, df_a: Series, df_b: Series):
        """
        输入股票代码，返回一个列表，包括相关的资产，以及相关系数
        """
        df_matrix = pandas.concat([df_a, df_b], axis=1)
        df_matrix.dropna(how='any', axis=0, inplace=True)
        return df_matrix.corr().iloc[0, 1]

    @classmethod
    def cointegration_check(cls, df_a: Series, df_b: Series):
        """
        对两个资产进行协整检验
        """
        x_add = sm.add_constant(df_b)
        model = sm.OLS(df_a, x_add).fit()
        # epsilong = y - beta * x - alpha
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
        return result, model.params[1], model.params[0]

    def trade(self, signal: SignalBase, price_a: float, price_b: float):
        if signal.signal == 0:
            pass
        elif signal.signal == 1:
            self.add_trade(
                self.pair_trade_1(self.stock_1, price_a, self.stock_2, price_b)
                )
        elif signal.signal == 2:
            self.add_trade(
                self.pair_trade_2(self.stock_1, price_a, self.stock_2, price_b)
                )
        elif signal.signal == -1:
            pass
        else:
            pass

    def pair_trade_1(self, stock_1: str, a: float, stock_2: str, b: float):
        bid_1 = 100
        bid_2 = -bid_1 * round(self._ratio)
        msg_1 = self._long_trade(stock_1, a, bid_1)
        msg_2 = self._short_trade(stock_2, b, bid_2)
        return [msg_1, msg_2]

    def pair_trade_2(self, stock_1: str, a: float, stock_2: str, b: float):
        bid_1 = -100
        bid_2 = -bid_1 * round(self._ratio)
        msg_1 = self._short_trade(stock_1, a, bid_1)
        msg_2 = self._long_trade(stock_2, b, bid_2)
        return [msg_1, msg_2]

    def _long_trade(self, stock: str, price: float, bid: int):
        return TradeMessage(stock, 'null', price, bid)

    def _short_trade(self, stock: str, price: float, bid: int):
        return TradeMessage(stock, 'null', price, bid)

    def summary(self):
        profit = 0.0
        for m in self.trade_list:
            profit += m.price * m.bid
        print(round(profit, 2))


class MarketBase(object):
    def __init__(self) -> None:
        super().__init__()
        self.pool = []
        self.data = DataFrame()

    def Config(self, **args):
        raise NotImplementedError

    def _check_capital(self, stock_code: str):
        """
        Checking capital data from database.
        """
        return None

    def add_capital(self, stock_code: str):
        self.pool.append(stock_code)


class StockMarket(MarketBase):
    def __init__(self, from_date, to_data) -> None:
        self.from_date = from_date
        self.to_date = to_data
        super().__init__()

    def __str__(self) -> str:
        text = f"From {self.from_date} to {self.to_date}"
        return text

    def init_data(self, head: mysqlHeader):
        price_engine = StockPrice(head)
        if self.pool:
            for stock in self.pool:
                df = price_engine.get_data(stock_code=stock, start=self.from_date, end=self.to_date)
                self.data = pandas.concat([self.data, df], axis=1)
            self.data.dropna(axis=0, how='any', inplace=True)

    def print_stock_list(self):
        for stock in self.pool:
            print(stock)

    def __iter__(self):
        return self.data.iterrows()


class InvestmentGroup(object):
    def __init__(self) -> None:
        super().__init__()
        self.pool = []

    def add_capital(self, stock_code: str):
        self.pool.append(stock_code)


def backtest2():
    head = mysqlHeader(acc='stock', pw='stock2020', db='stock')
    stock_market = StockMarket('2019-01-01', '2021-03-01')
    print(stock_market)
    A = 'SH600000'
    B = 'SH601988'
    stock_market.add_capital(A)
    stock_market.add_capital(B)
    stock_market.print_stock_list()
    stock_market.init_data(head)
    Trade = PairTrade(A, B)
    result, beta, alpha = Trade.cointegration_check(stock_market.data[A], stock_market.data[B])
    Trade.set_ratio(beta)
    Signal = SignalPairTrade()
    Signal.set_threshold(high=0.02, low=-0.02, beta=beta, alpha=alpha)
    print(Signal.signal)
    for index, row in stock_market:
        Signal.get_data(row[A], row[B])
        Trade.trade(Signal, row[A], row[B])
        # print(Signal.signal)
    Signal.set_end()
    print(Trade)
    Trade.summary()


if __name__ == '__main__':
    # cointegration()
    # param_adjust()
    backtest2()
