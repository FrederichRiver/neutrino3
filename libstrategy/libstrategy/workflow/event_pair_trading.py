from dev_global.path import SQL_FILE
from libmysql_utils.mysql8 import mysqlHeader
from libstrategy.strategy.pair_trading import PairTradeStrategy, kalman_param_evalue
from libstrategy.data_engine.data_engine import StockData
from libbasemodel.stock_model import StockBase
from libmysql_utils.header import REMOTE_HEADER
from pandas import DataFrame
import pandas as pd
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

# to Do: 将事件抽象成对象
def event_init_relative_matrix():
    """
    1.调取股票列表
    2.生成矩阵组合
    3.写入数据库
    """
    HEAD = mysqlHeader('stock', 'stock2020', 'analysis', host='115.159.1.221')
    Tmp_Engine = StockBase(HEAD)
    stock_list = StockBase(REMOTE_HEADER).get_all_stock_list()
    for i in range(len(stock_list)):
        for j in range(i+1, len(stock_list)):
            sql = f"REPLACE into capital_relative_matrix (`stock_1`,`stock_2`) VALUES ('{stock_list[i]}','{stock_list[j]}')"
            Tmp_Engine.engine.execute(sql)

def event_relative_coefficient():
    """
    1.调取股票列表
    2.计算相关性
    3.将相关性数据存入数据库
    """
    start_date = '2020-01-01'
    end_date = '2021-05-20'
    stock_1 = 'SZ002460'
    stock_2 = 'SZ002497'
    # stock_2 = 'SH600000'
    DataEngine = StockData(REMOTE_HEADER, start_date, end_date)
    DataEngine.Config(**{'asset': [stock_1, stock_2]})
    df1 = DataEngine.get_data(stock_1, start_date, end_date)
    df2 = DataEngine.get_data(stock_2, start_date, end_date)
    result = cointegration_check(df1[f"{stock_1}_xrdr"], df2[f"{stock_2}_xrdr"])
    print(f"{stock_1},{stock_2},{'%.2f' % result[0]}")

def event_cointegration_check():
    import re
    data_engine = StockData(REMOTE_HEADER)
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

# event_cointegration_check()

# SZ002460 with SZ002497
# SZ002460 with SH603799
if __name__ == '__main__':
    event_relative_coefficient()