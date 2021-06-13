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
    
    def _trade(self, signal, date, trade_data):
        raise NotImplementedError


class Benchmark(Account):
    def __init__(self, name: str, strategy, init_cash: float, benchmark: str):
        super().__init__(name, strategy, init_cash=init_cash)
        self.investment.init_stock([benchmark])
        self.stock_id = benchmark

    def update_price(self, date, price_list):
        self.investment.profolio[self.stock_id].price = price_list[self.stock_id]
        self.investment.add_hist_value(date, self.investment.value)

    def _trade(self, signal, trade_date, trade_data):
        trade_date = trade_date.strftime('%Y-%m-%d')
        if signal == 1:
            order = self._positive_trade(trade_date, self.stock_id, trade_data[self.stock_id])
        elif signal == -1:
            order = self._settle(trade_date, trade_data[self.stock_id])
        else:
            order = []
        return order

    def _positive_trade(self, trade_date, stock_id: str, price: float):
        vol = int(self.investment.cash / price)
        order = self.investment.profolio[stock_id].buy(
            trade_date=trade_date, volume=vol, price=price)
        return [order, ]

    def _settle(self, trade_date, price: float):
        order = self.investment.profolio[self.stock_id].settle(trade_date, price)
        return [order, ]

class PairTrading(Account):
    def __init__(self, name: str, strategy, init_cash: float, A: str, B: str, beta: float):
        super().__init__(name, strategy, init_cash=init_cash)
        self.investment.init_stock([A, B])
        self.A = A
        self.B = B
        self.ratio = beta

    def update_price(self, date, price_list):
        self.investment.profolio[self.A].price = price_list[self.A]
        self.investment.profolio[self.B].price = price_list[self.B]
        self.investment.add_hist_value(date, self.investment.value)

    def _trade(self, signal, trade_date, trade_data):
        trade_date = trade_date.strftime('%Y-%m-%d')
        if signal == 1:
            pair = self._positive_trade(trade_date, self.A, trade_data[self.A], self.B, trade_data[self.B])
        elif signal == 2:
            pair = self._negtive_trade(trade_date, self.A, trade_data[self.A], self.B, trade_data[self.B])
        elif signal == -1:
            order1 = self.investment.profolio[self.A].settle(trade_date, trade_data[self.A])
            order2 = self.investment.profolio[self.B].settle(trade_date, trade_data[self.B])
            pair = [order1, order2]
        else:
            pair = []
        return pair

    def _positive_trade(self, trade_date, stock_1: str, price_1: float, stock_2: str, price_2: float):
        if v := self.investment.profolio[stock_2].volume:
            order1 = self.investment.profolio[stock_2].sell(
                trade_date=trade_date, volume=v, price=price_2)
        else:
            order1 = TradeOrder(stock_2, trade_date, -1, 0, 0)
        v1 = int(self.investment.cash / price_1)
        order2 = self.investment.profolio[stock_1].buy(
            trade_date=trade_date, volume=v1, price=price_1)
        return [order1, order2]

    def _negtive_trade(self, trade_date, stock_1: str, price_1: float, stock_2: str, price_2: float):
        if v := self.investment.profolio[stock_1].volume:
            order1 = self.investment.profolio[stock_1].sell(
                trade_date=trade_date, volume=v, price=price_1)
        else:
            order1 = TradeOrder(stock_1, trade_date, -1, 0, 0)
        v2 = int(v * self.ratio)
        order2 = self.investment.profolio[stock_2].buy(
            trade_date=trade_date, volume=v2, price=price_2)
        return [order1, order2]
