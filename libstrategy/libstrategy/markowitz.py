#!/usr/bin/python38
from libmysql_utils.mysql8 import mysqlBase, LOCAL_HEADER
from libbasemodel.form import formStockManager
import pandas
from pandas import DataFrame
from pandas import isnull
import matplotlib.pyplot as plt
from libstrategy.strategy_utils import StockPrice


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


event = StockPrice(LOCAL_HEADER)
stock_list = event.get_stock_list()
bm = event.get_data('SZ002460', query_type='close', start='2019-01-01', end='2020-01-01')
# event.profit_matrix('SZ002460', bm)
result = DataFrame(columns=['stock_code', 'r'])
# stock_list = ['SZ002460']
# print(stock_list)
for stock in stock_list[:1]:
    df = event.get_data(stock, query_type='close', start='2019-01-01', end='2020-01-01')
    if not df.empty:
        # event.profit_matrix(stock, df)
        df_matrix = pandas.concat([bm, df], axis=1)
        diff = df_matrix['SZ002460'] - df_matrix[stock]
        diff.plot()
        plt.show()
