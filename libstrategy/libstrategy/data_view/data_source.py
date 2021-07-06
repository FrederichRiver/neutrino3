#!/usr/bin/python3
import pandas as pd
from dev_global.env import TIME_FMT
from libbasemodel.stock_model import StockBase
from pandas import DataFrame
"""
数据源用于获取各种数据，处理之后提交给graph方法来绘制图像用于可视化。
"""
class DataSource(StockBase):
    def get_shibor_data(self, length=60) -> DataFrame:
        df = self.select_values(
            "shibor", 'release_date,one_week')
        # data cleaning
        df.columns = ['Date', 'one_week']
        df['Date'] = pd.to_datetime(df['Date'], format=TIME_FMT)
        df.set_index('Date', inplace=True)
        df.dropna(axis=0, how='any', inplace=True)
        df = df[-length:].copy()
        return df

    def get_treasury_yield_data(self, length=60) -> DataFrame:
        df1 = self.select_values(
            "china_treasury_yield", 'report_date,ten_year')
        # data cleaning
        df1.columns = ['Date', 'China']
        df1['Date'] = pd.to_datetime(df1['Date'], format=TIME_FMT)
        df1.set_index('Date', inplace=True)
        df1.dropna(axis=0, how='any', inplace=True)
        df1 = df1[-length:].copy()

        df2 = self.select_values(
            "us_treasury_yield", 'report_date,ten_year')
        # data cleaning
        df2.columns = ['Date', 'US']
        df2['Date'] = pd.to_datetime(df2['Date'], format=TIME_FMT)
        df2.set_index('Date', inplace=True)
        df2.dropna(axis=0, how='any', inplace=True)
        df2 = df2[-length:].copy()
        df = pd.concat([df1, df2], axis=1)
        return df
