# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.


import pandas as pd
import numpy as np
import copy
import pathlib

from pandas.core.frame import DataFrame
from .order import TradeOrder
from .asset import StockAsset


"""
investment module
"""

"""
current state of investment
a typical example is :{
  <instrument_id>: {
    'count': <how many days the security has been hold>,
    'amount': <the amount of the security>,
    'price': <the close price of security in the last trading day>,
    'weight': <the security weight of total investment value>,
  },
}

"""


class Investment(object):
    """Investment is a group of target together with cash. \n
    """

    def __init__(self, cash=0, investment_dict={}, today_account_value=0):
        # NOTE: The investment dict must be copied!!!
        # Otherwise the initial value
        self.INITIAL_VALUE = cash
        self.__cash = cash
        self.profolio = investment_dict.copy()
        self._start_date = 0
        self.history_value = {}
        # self.investment.today_account_value = today_account_value

    def init_stock(self, stock_list: list):
        for stock_id in stock_list:
            self.add_stock(stock_id)

    def add_stock(self, stock_id: str):
        self.profolio[stock_id] = StockAsset(stock_id, cash=0)

    def __str__(self) -> str:
        text = ''
        for asset_id, asset in self.profolio.items():
            text += f"{asset.__str__()}\n"
        return f"Investment:\n{text}"

    def inProfolio(self, stock_id: str) -> bool:
        return stock_id in self.profolio.keys()

    def buy_stock(self, stock_id: str, trade_date, trade_volume: int, trade_price: float):
        # Need to check cash
        if not self.inProfolio(stock_id):
            self.add_stock(stock_id)
        order = self.profolio[stock_id].buy(trade_date=trade_date, volume=trade_volume, price=trade_price)        
        return order

    def sell_stock(self, stock_id: str, trade_date, trade_volume: int, trade_price: float):
        if self.inProfolio(stock_id):
            order = self.profolio[stock_id].sell(trade_date=trade_date, volume=trade_volume, price=trade_price) 
        return order

    def del_stock(self, stock_id: str):
        if self.inProfolio(stock_id):
            del self.profolio[stock_id]

    def update_order(self, order, trade_val, cost, trade_price):
        # handle order, order is a order class, defined in exchange.py
        if order.direction == TradeOrder.BUY:
            # BUY
            self.buy_stock(order.stock_id, trade_val, cost, trade_price)
        elif order.direction == TradeOrder.SELL:
            # SELL
            self.sell_stock(order.stock_id, trade_val, cost, trade_price)
        else:
            raise NotImplementedError("do not support order direction {}".format(order.direction))

    def add_hist_value(self, index, value: float):
        """
        { 'yyyy-mm-dd': price }
        """
        self.history_value[index] = value

    def get_hist_value(self) -> DataFrame:
        df = pd.DataFrame.from_dict(self.history_value, orient='index')
        #df.columns = ['trade_date', 'net_value']
        #df.set_index('trade_date', inplace=True)
        return df

    def update_stock_price(self, stock_id, price):
        self.profolio[stock_id].price = price

    def update_stock_count(self, stock_id, count):
        self.profolio[stock_id].count = count

    def update_stock_weight(self, stock_id, weight):
        self.profolio[stock_id].weight = weight

    @property
    def cash(self):
        return self.__cash

    def add_cash(self, cash: float) -> float:
        self.__cash += cash
        return self.__cash

    @property
    def value(self) -> float:
        value = self.__cash
        for _, asset in self.profolio.items():
            value += asset.value
        return value

    @property
    def asset_list(self) -> list:
        return list(set(self.profolio.keys()))


    def get_stock_price(self, code):
        return self.profolio[code].price

    def get_stock_volume(self, code):
        return self.profolio[code].volume

    def get_stock_count(self, code):
        return self.profolio[code].count

    def get_stock_weight(self, code):
        return self.profolio[code].weight

    def get_stock_amount_dict(self) -> dict:
        """generate stock amount dict {stock_id : amount of stock} """
        d = {}
        stock_list = self.get_stock_list()
        for stock_code in stock_list:
            d[stock_code] = self.get_stock_amount(code=stock_code)
        return d

    def get_stock_weight_dict(self, only_stock=False):
        """get_stock_weight_dict
        generate stock weight fict {stock_id : value weight of stock in the investment}
        it is meaningful in the beginning or the end of each trade date

        :param only_stock: If only_stock=True, the weight of each stock in total stock will be returned
                           If only_stock=False, the weight of each stock in total assets(stock + cash) will be returned
        """
        if only_stock:
            investment_value = self.calculate_stock_value()
        else:
            investment_value = self.calculate_value()
        d = {}
        stock_list = self.get_stock_list()
        for stock_code in stock_list:
            d[stock_code] = self.profolio[stock_code].amount * self.profolio[stock_code].price / investment_value
        return d

    def add_count_all(self):
        stock_list = self.get_stock_list()
        for code in stock_list:
            self.profolio[code].count += 1

    def update_weight_all(self):
        weight_dict = self.get_stock_weight_dict()
        for stock_code, weight in weight_dict.items():
            self.update_stock_weight(stock_code, weight)
