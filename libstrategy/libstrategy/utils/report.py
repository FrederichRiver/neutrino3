#!/usr/bin/python38


from collections import OrderedDict
from libstrategy.utils.order import TradeOrder
from libstrategy.utils.investment import Investment
import pandas as pd
import pathlib

class Report(object):
    def __init__(self) -> None:
        super().__init__()
        self.__earning_rate = 0.0
        self.__annalized_return = 0.0
        self.winning_rate = 0.0
        self.profit_loss_ratio = 0.0
        self.max_draw = 0.0
        self.sharpe_ratio = 0.0
        self.sotino_ratio = 0.0
        self.trade_list = []
        self.period = 0

    def get_investment(self, investment: Investment):
        self.init_cash = investment.INITIAL_VALUE

    def earning_rate(self):
        self.__earning_rate = 0
        return self.__earning_rate

    @property
    def annalized_return(self):
        return self.__annalized_return

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