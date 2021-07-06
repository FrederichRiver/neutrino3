#!/usr/bin/python38
from abc import ABCMeta
import copy

from .investment import Investment
from .order import TradeOrder
from libstrategy.data_engine.data_engine import EventEngine, XrdrEvent
from math import ceil
import pandas as pd


class Account(metaclass=ABCMeta):
    def __init__(self, name: str, strategy, init_cash=10000.0,):
        self.name = name
        self.unit = 'CNY'
        # init cash
        self.init_cash = init_cash
        self.Strategy = strategy
        self.investment = Investment(cash=init_cash)

    def run(self, data: list, trade_price: list):
        """
        Reserve Method, used in automatic environment.
        Not completed.
        """
        if signal := self.Strategy(data):
            self.trade(signal, trade_price)
    
    def trade(self, signal, date, trade_price):
        raise NotImplementedError

    def xrdr(self, trade_date, event: XrdrEvent):
        self.investment.profolio[event.stock_id].xrdr(trade_date, event.bonus, event.increase, event.dividend)

class Benchmark(Account):
    def __init__(self, name: str, strategy, init_cash: float, stock_id: str):
        super().__init__(name, strategy, init_cash=init_cash)
        self.investment.init_stock([stock_id])
        self.stock_id = stock_id

    def _update_price(self, trade_date: str, price_list):
        self.investment.profolio[self.stock_id].price = price_list[self.stock_id]
        self.investment.add_hist_value(trade_date, self.investment.value)

    def trade(self, signal, trade_date: pd.Timestamp, trade_price):
        trade_date = trade_date.strftime('%Y-%m-%d')
        if signal == 1:
            order = self._positive_trade(trade_date, self.stock_id, trade_price[self.stock_id])
        else:
            order = []
        self._update_price(trade_date, price_list=trade_price)
        return order

    def _positive_trade(self, trade_date: str, stock_id: str, price: float):
        vol = 100 * ceil(self.investment.cash / (100 * price))
        order = self.investment.profolio[stock_id].buy(
            trade_date=trade_date, volume=vol, price=price)
        return [order, ]

    def settle(self, trade_date: str, price):
        if isinstance(trade_date, pd.Timestamp):
            trade_date = trade_date.strftime('%Y-%m-%d')
        order = self.investment.profolio[self.stock_id].settle(trade_date, price[self.stock_id])
        self._update_price(trade_date, price_list=price)
        return [order, ]


class PairTrading(Account):
    """
    Pair Trading Agent.
    Workflow:
    Step 1: Init position
    Step 2: Trade in each time step
        2.1 trade
        2.2 update_price
    Step 3: Settle
    """
    def __init__(self, name: str, strategy, init_cash: float, A: str, B: str, beta: float):
        super().__init__(name, strategy, init_cash=init_cash)
        self.investment.init_stock([A, B])
        self.A = A
        self.B = B
        self.ratio = beta

    def _update_price(self, date, price_list):
        for stock_id in self.investment.pool:
            self.investment.profolio[stock_id].price = price_list[stock_id]
        self.investment.add_hist_value(date, self.investment.value)

    def init_position(self, trade_date, stock_id: str, price: float):
        vol = int(self.investment.cash / price)
        order = self.investment.profolio[stock_id].buy(
            trade_date=trade_date, volume=vol, price=price)
        return [order, ]

    def trade(self, signal, trade_date, trade_price):
        """
        Param:
        param: signal settle(-1), no-action(0), pos-trade(1), neg-trade(2)
        param: trade_date: Timestamp
        param: trade_price: DataFrame
        """
        trade_date = trade_date.strftime('%Y-%m-%d')
        if (signal == 1) or (signal == 3):
            pair = self._positive_trade(trade_date, self.A, trade_price[self.A], self.B, trade_price[self.B])
        elif signal == 2:
            pair = self._negtive_trade(trade_date, self.A, trade_price[self.A], self.B, trade_price[self.B])
        elif signal == -1:
            order1 = self.investment.profolio[self.A].settle(trade_date, trade_price[self.A])
            order2 = self.investment.profolio[self.B].settle(trade_date, trade_price[self.B])
            pair = [order1, order2]
        else:
            pair = []
        self._update_price(trade_date, price_list=trade_price)
        return pair

    def _positive_trade(self, trade_date, stock_1: str, price_1: float, stock_2: str, price_2: float):
        # 如果B仓位不为零，则卖出B
        if v := self.investment.profolio[stock_2].volume:
            order1 = self.investment.profolio[stock_2].sell(
                trade_date=trade_date, volume=v, price=price_2)
        else:
            order1 = TradeOrder(stock_2, trade_date, -1, 0, 0)
        # 如果A仓位为零，则买入A
        if self.investment.profolio[stock_1].volume:
            order2 = TradeOrder(stock_1, trade_date, -1, 0, 0)
        else:
            v1 = 100 * ceil(self.investment.cash / (100 * price_1))
            order2 = self.investment.profolio[stock_1].buy(
                trade_date=trade_date, volume=v1, price=price_1)    
        return [order1, order2]

    def _negtive_trade(self, trade_date, stock_1: str, price_1: float, stock_2: str, price_2: float):
        # 如果A仓位不为0, 则卖出A
        if v := self.investment.profolio[stock_1].volume:
            order1 = self.investment.profolio[stock_1].sell(
                trade_date=trade_date, volume=v, price=price_1)
        else:
            order1 = TradeOrder(stock_1, trade_date, -1, 0, 0)
        # 如果B仓位为0, 则买入B
        if self.investment.profolio[stock_2].volume:
            order1 = TradeOrder(stock_2, trade_date, -1, 0, 0)
        else:
            # v2 = v * ceil(self.ratio)
            v2 = 100 * ceil(self.investment.cash / (100 * price_2))
            order2 = self.investment.profolio[stock_2].buy(
                trade_date=trade_date, volume=v2, price=price_2)
        return [order1, order2]

    def settle(self, trade_date, trade_price):
        if isinstance(trade_date, pd.Timestamp):
            trade_date = trade_date.strftime('%Y-%m-%d')
        order_list = []
        for asset_id in self.investment.asset_list:
            order = self.investment.profolio[asset_id].settle(trade_date, trade_price[asset_id])
            order_list.append(order)
        return order_list