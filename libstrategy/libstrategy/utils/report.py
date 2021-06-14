#!/usr/bin/python38


from collections import OrderedDict
from libstrategy.utils.order import TradeOrder
from libstrategy.utils.investment import Investment
import pandas as pd
import pathlib

from pandas.core.frame import DataFrame

class Report(object):
    def __init__(self, id: str) -> None:
        self.id = id
        self.earning_rate = 0.0
        self.annalized_return = 0.0
        self.winning_rate = 0.0
        self.profit_loss_ratio = 0.0
        self.max_draw = 0.0
        self.sharpe_ratio = 0.0
        self.sotino_ratio = 0.0
        self.trade_list = []
        self.period = 0
        self.history_value = None

    def get_investment(self, investment: Investment):
        self.init_cash = investment.INITIAL_VALUE
        self.history_value = investment.history_value.copy()
        self.history_value.columns = [self.id]

    def get_data(self, data: DataFrame):
        self.history_value = data.copy()
        self.history_value.columns = [self.id]

    def run(self) -> dict:
        self.history_value['ret'] = self.history_value[self.id] / self.history_value[self.id].shift(1)
        self.history_value['cum_return'] = self.history_value['ret'].cumprod()
        self.history_value["draw"] = self.history_value['cum_return'].diff()
        nu = self.history_value['ret'].mean() - 1
        Rf = 0.03 / 252
        self.history_value['var'] = self.history_value['ret'] - nu
        sigma = self.history_value['var'].var()
        self.period = self.history_value.shape[0]
        self.total_return = self.history_value.iloc[[-1]]['cum_return'].values[0] - 1
        self.annalized_return = self.total_return * 252 / self.period
        self.sharpe_ratio = (nu - Rf) / sigma
        self.max_draw =  self.history_value['cum_return'].diff().min()
        return {
            "total_return": self.total_return, "annalized_return": self.annalized_return,
            "sharpe_ratio": self.sharpe_ratio, "max_draw": self.max_draw
        }

    def add_trade(self, trade_order):
        if isinstance(trade_order, list):
            self.trade_list.extend(trade_order)
        elif isinstance(trade_order, TradeOrder):
            self.trade_list.append(trade_order)

    def simple_report(self, title: str):
        report = (
                    f"Backtest Report for {title}:\n"
                    f"Earning Rate: {'%2.f%' % (self.earning_rate * 100)}\n"
                    f"Annalized Return: {'%2.f%' % (self.annalized_return * 100)}\n"
                    f"Winning Rate: {'%2.f%' % (self.winning_rate * 100)}\n"
                    f"Profit Loss Ratio: {'%2.f%' % (self.profit_loss_ratio * 100)}\n"
                    f"Max Draw: {'%2.f%' % (self.max_draw * 100)}\n"
                    f"Sharpe Ratio: {'%2.f%' % (self.sharpe_ratio * 100)}\n"
                    f"Sotino Ratio: {'%2.f%' % (self.sotino_ratio * 100)}\n"
                    )
        print(report)