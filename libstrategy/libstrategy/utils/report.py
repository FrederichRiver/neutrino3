#!/usr/bin/python38


from collections import OrderedDict
import pandas as pd
import pathlib

class Report(object):
    def __init__(self) -> None:
        super().__init__()
        self.earning_rate = 0.0
        self.annalized_return = 0.0
        self.winning_rate = 0.0
        self.profit_loss_ratio = 0.0
        self.max_draw = 0.0
        self.sharpe_ratio = 0.0
        self.sotino_ratio = 0.0

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