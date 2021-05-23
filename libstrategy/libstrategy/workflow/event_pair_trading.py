from libstrategy.pair_trading import PairTrade
from libstrategy.utils.strategy_utils import StockPrice
from libbasemodel.stock_model import StockBase
from libmysql_utils.header import REMOTE_HEADER
from pandas import DataFrame
import pandas as pd


def event_relative_check():
    stock_list = StockBase(REMOTE_HEADER).get_all_stock_list()
    event = StockPrice(REMOTE_HEADER)
    df_matrix = DataFrame()
    i = 0
    for stock in stock_list:
        i += 1
        print(i)
        df = event.get_data(stock, query_type='close', start='2020-01-01', end='2021-05-20')
        if not df.empty:
            event.profit_matrix(stock, df)
            try:
                df_matrix = pd.concat([df_matrix, df], axis=1)
            except:
                pass
    relative_matrix = df_matrix.corr()
    with open('/opt/neutrino/data/relative_matrix', 'w') as f:
        stock_list = df_matrix.columns
        for i in range(len(stock_list)):
            for j in range(i + 1, len(stock_list)):
                f.write(f"{stock_list[i]}, {stock_list[j]}, {relative_matrix.loc[stock_list[i], stock_list[j]]}\n")


def event_filter():
    import re
    with open('/opt/neutrino/data/Relative_matrix', 'r') as f:
        with open('/opt/neutrino/data/High_relative', 'w') as g:
            while (line := f.readline()):
                code1, code2, corr = re.split(',', line)
                if float(corr) > 0.7:
                    g.write(f"{code1},{code2},{corr}")

import numpy as np
from statsmodels.tsa.stattools import adfuller
from pandas import Series

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

def event_cointegration_check():
    import re
    data_engine = StockPrice(REMOTE_HEADER)
    with open('/opt/neutrino/data/High_relative', 'r') as f:
        with open('/opt/neutrino/data/Cointegration_check', 'w', 100) as g:        
            while (line := f.readline()):
                code1, code2, corr = re.split(',', line)
                df1 = data_engine.get_data(stock_code=code1, query_type='close', start='2020-01-01', end='2021-05-20')        
                df2 = data_engine.get_data(stock_code=code2, query_type='close', start='2020-01-01', end='2021-05-20')
                df = pd.concat([df1, df2], axis=1)
                df.dropna(axis=0, inplace=True)
                try:
                    result = cointegration_check(df[code1], df[code2])
                    if float(result[0]) != 0:
                        print(f"{code1},{code2},{'%.2f' % result[0]}")
                        g.write(f"{code1},{code2},{'%.2f' % result[0]}\n")
                except Exception as e:
                    g.write(f'{code1},{code2},ERROR!\n')

event_cointegration_check()