#!/usr/bin/python38
import abc
import copy

from .investment import Investment
from .report import Report


class Account(abc):
    def __init__(self, name: str, strategy, init_cash=10000.0,):
        self.name = name
        self.unit = 'CNY'
        # init cash
        self.init_cash = init_cash
        self.Strategy = strategy
        self.investment = Investment(cash=init_cash)

    def run(self, data: list, trade_data: list):
        if signal := self.Strategy(data):
            self._trade(signal, trade_data)
    
    def _trade(self, signal, trade_data):
        raise NotImplemented


class PairTrading(Account):
    def __init__(self, name: str, strategy, init_cash):
        super().__init__(name, strategy, init_cash=init_cash)