#!/usr/bin/python38
from abc import ABCMeta
import copy

from .investment import Investment
from .report import Report
from .order import TradeOrder


class Account(metaclass=ABCMeta):
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
    def __init__(self, name: str, strategy, init_cash: float, A: str, B: str, beta: float):
        super().__init__(name, strategy, init_cash=init_cash)
        self.investment.init_stock([A, B])
        self.A = A
        self.B = B
        self.ratio = beta

    def _trade(self, signal, trade_data):
        if signal == 1:
            pair = self._positive_trade(self.A, trade_data[self.A], self.B, trade_data[self.B])
        elif signal == 2:
            pair = self._negtive_trade(self.A, trade_data[self.A], self.B, trade_data[self.B])
        elif signal == -1:
            order1 = self.investment.investment[self.A].settle(trade_data[self.A])
            order2 = self.investment.investment[self.B].settle(trade_data[self.B])
            pair = [order1, order2]
        else:
            pair = None
        return pair

    def _positive_trade(self, stock_1: str, price_1: float, stock_2: str, price_2: float):
        if v := self.investment.investment[stock_2].volume:
            order1 = self.investment.investment[stock_2].sell(**{"volume": v, "price": price_2})
        else:
            order1 = TradeOrder(stock_2, 'null', 1, 0, 0, 0)
        v1 = int(self.investment.cash / price_1)
        order2 = self.investment.investment[stock_1].buy(**{"volume": v1, "price": price_1})
        return order1, order2

    def _negtive_trade(self, stock_1: str, price_1: float, stock_2: str, price_2: float):
        if v := self.investment.investment[stock_1].volume:
            order1 = self.investment.investment[stock_1].sell(**{"volume": v, "price": price_1})
        else:
            order1 = TradeOrder(stock_1, 'null', 1, 0, 0, 0)
        v2 = int(v * self.ratio)
        order2 = self.investment.investment[stock_2].buy(**{"volume": v2, "price": price_2})
        return order1, order2
