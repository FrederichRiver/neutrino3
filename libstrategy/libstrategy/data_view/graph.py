import matplotlib.pyplot as plt

#!/usr/bin/python38
import os
import mplfinance as mpf
import matplotlib.pyplot as plt
from libbasemodel.stock_model import StockBase, StockData
from libmysql_utils.mysql8 import mysqlHeader
from libmysql_utils.header import GLOBAL_HEADER
from pandas import DataFrame
import pandas as pd
from dev_global.env import TIME_FMT
import datetime
"""
接收各种数据之后绘制图像。
"""

class Plot(object):
    def __init__(self, img_path: str) -> None:
        self.image_path = img_path

    def candle_plot_config(self, title='', plot_type='') -> dict:
        param_dict = {}
        if plot_type == "candle_plot":
            usr_color = mpf.make_marketcolors(up='red', down='green', edge='i', wick='i', volume='in')
            usr_style = mpf.make_mpf_style(marketcolors=usr_color)
            param_dict['returnfig'] = True
            param_dict['type'] = 'candle'
            param_dict['mav'] = (5, 10, 20)
            param_dict['volume'] = True
            param_dict['title'] = title
            param_dict['style'] = usr_style
            param_dict['datetime_format'] = TIME_FMT
            param_dict['figscale'] = 1.0
        return param_dict

    def plot_config(self, title='', plot_type='') -> plt:
        current_date = datetime.date.today().strftime(TIME_FMT)
        plt.figure(figsize=(12, 4), dpi=72)
        plt.xlabel("Date")
        if plot_type == 'shibor':    
            plt.title(f"View of Shibor on {current_date}")
            plt.ylabel("Rate in %")
        elif plot_type == 'treasury':
            plt.title(f"View of Treasury Yield on {current_date}")
            plt.ylabel("Yield in %")
        return plt

    def mpl_plot(self, df: DataFrame, param: dict):
        mpf.plot(df, param)

    def plot(self, df: DataFrame, param: dict, plot_type=''):
        plt = self.plot_config(plot_type=plot_type)
        if plot_type == 'shibor':
            plt.plot(df, label="7 days shibor")
            image_name = "shibor.png"
        elif plot_type == 'treasury':
            plt.plot(df['China'], label="China")
            plt.plot(df['US'], label="US")
            image_name = "treasury_yield.png"
        imgfile = os.path.join(self.image_path, image_name)
        plt.legend()
        plt.savefig(imgfile, format='png')
