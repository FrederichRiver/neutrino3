#!/usr/bin/python38
import os
import mplfinance as mpf
import matplotlib.pyplot as plt
from libbasemodel.stock_model import StockBase, StockData
from libmysql_utils.mysql8 import GLOBAL_HEADER, mysqlHeader
from pandas import DataFrame
import pandas as pd
from dev_global.env import TIME_FMT
import datetime


class ShiborView(StockBase):
    def __init__(self, header: mysqlHeader, img_path: str) -> None:
        super(ShiborView, self).__init__(header)
        self.image_path = img_path

    def get_raw_data(self, length=60) -> DataFrame:
        df = self.select_values(
            "shibor", 'release_date,one_week')
        # data cleaning
        df.columns = ['Date', 'one_week']
        df['Date'] = pd.to_datetime(df['Date'], format=TIME_FMT)
        df.set_index('Date', inplace=True)
        df.dropna(axis=0, how='any', inplace=True)
        df = df[-length:].copy()
        return df

    def plot(self):
        df = self.get_raw_data()
        # data constructing
        self._matplot_config(df)

    def _matplot_config(self, df: DataFrame):

        current_date = datetime.date.today().strftime(TIME_FMT)
        plt.figure(figsize=(12, 4), dpi=72)
        plt.title(f"View of Shibor on {current_date}")
        plt.xlabel("Date")
        plt.ylabel("Rate in %")
        plt.plot(df, label="7 days shibor")
        plt.legend()
        img = os.path.join(self.image_path, "shibor.png")
        plt.savefig(img, format='png')
        return plt


class TreasuryYieldView(StockBase):
    def __init__(self, header: mysqlHeader, img_path: str) -> None:
        super(TreasuryYieldView, self).__init__(header)
        self.image_path = img_path

    def get_raw_data(self, length=60) -> DataFrame:
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

    def plot(self):
        df = self.get_raw_data()
        # data constructing
        self._matplot_config(df)

    def _matplot_config(self, df: DataFrame):
        import datetime
        import os
        current_date = datetime.date.today().strftime(TIME_FMT)
        plt.figure(figsize=(12, 4), dpi=72)
        plt.title(f"View of Treasury Yield on {current_date}")
        plt.xlabel("Date")
        plt.ylabel("Yield in %")
        plt.plot(df['China'], label="China")
        plt.plot(df['US'], label="US")
        plt.legend()
        img = os.path.join(self.image_path, "treasury_yield.png")
        plt.savefig(img, format='png')
        return plt

"""
作为图形绘制的基础类。
CandleView作为K线绘制的基础类，CandleView2在基类基础上衍生。
"""


class CandleView(StockData):
    """
    K Plot of stock.
    """
    def __init__(self, header: mysqlHeader, img_path: str) -> None:
        super(CandleView, self).__init__(header)
        self.image_path = img_path

    def plot(self, stock_code: str):
        df = self.get_stock_data(stock_code)
        df.dropna(axis=0, how="any", inplace=True)
        # data constructing
        self._matplot_config(df, stock_code)

    def _matplot_config(self,  df: DataFrame, stock_code: str):
        usr_color = mpf.make_marketcolors(up='red', down='green', edge='i', wick='i', volume='in')
        usr_style = mpf.make_mpf_style(marketcolors=usr_color)
        img = os.path.join(self.image_path, f"{stock_code}.png")
        mpf.plot(
            df, returnfig=True, type='candle', mav=(5, 10, 20),
            volume=True, title=stock_code, style=usr_style,
            datetime_format=TIME_FMT, figscale=1.0, savefig=img
            )
        return plt


if __name__ == "__main__":
    from libmysql_utils.mysql8 import mysqlHeader
    head = mysqlHeader(acc="stock", pw="stock2020", db="stock", host="115.159.1.221")
    event = TreasuryYieldView(head, '/home/friederich/Dev/neutrino2/data')
    event.plot()
