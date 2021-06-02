# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.


import pandas as pd
import numpy as np
import copy
import pathlib
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
        self.investment = investment_dict.copy()
        # self.investment.today_account_value = today_account_value

    def init_stock(self, stock_list: list):
        for stock_id in stock_list:
            self.add_stock(stock_id)

    def add_stock(self, stock_id: str):
        self.investment[stock_id] = StockAsset(stock_id, cash=0)

    def __str__(self) -> str:
        text = ''
        for asset_id, asset in self.investment.items():
            text += f"{asset.__str__()}\n"
        return f"Investment:\n{text}."

    def buy_stock(self, stock_id: str, trade_volume: int, trade_price: float):
        # Need to check cash
        if stock_id not in self.investment.keys():
            self.add_stock(stock_id)
        order = self.investment[stock_id].buy(**{"volume": trade_volume, "price": trade_price})        
        return order

    def sell_stock(self, stock_id: str, trade_volume: int, trade_price: float):
        if stock_id in self.investment.keys():
            order = self.investment[stock_id].buy(**{"volume": trade_volume, "price": trade_price}) 
        else:
            order = TradeOrder(stock_id, 'null', 1, 0, 0, 0)
        return order

    def del_stock(self, stock_id: str):
        if stock_id in self.investment.keys():
            del self.investment[stock_id]

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

    def update_stock_price(self, stock_id, price):
        self.investment[stock_id].price = price

    def update_stock_count(self, stock_id, count):
        self.investment[stock_id].count = count

    def update_stock_weight(self, stock_id, weight):
        self.investment[stock_id].weight = weight

    @property
    def cash(self):
        return self.__cash

    def add_cash(self, cash: float) -> float:
        self.__cash += cash
        return self.__cash

    @property
    def value(self) -> float:
        value = self.__cash
        for _, asset in self.investment.items():
            value += asset.value
        return value

    @property
    def asset_list(self) -> list:
        return list(set(self.investment.keys()))


    def get_stock_price(self, code):
        return self.investment[code].price

    def get_stock_volume(self, code):
        return self.investment[code].volume

    def get_stock_count(self, code):
        return self.investment[code].count

    def get_stock_weight(self, code):
        return self.investment[code].weight

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
            d[stock_code] = self.investment[stock_code].amount * self.investment[stock_code].price / investment_value
        return d

    def add_count_all(self):
        stock_list = self.get_stock_list()
        for code in stock_list:
            self.investment[code].count += 1

    def update_weight_all(self):
        weight_dict = self.get_stock_weight_dict()
        for stock_code, weight in weight_dict.items():
            self.update_stock_weight(stock_code, weight)

    def save_investment(self, path, last_trade_date):
        path = pathlib.Path(path)
        p = copy.deepcopy(self.investment)
        cash = pd.Series(dtype=np.float)
        cash.init_cash = self.init_cash
        cash.cash = p.cash
        cash.today_account_value = p.today_account_value
        cash.last_trade_date = str(last_trade_date.date()) if last_trade_date else None
        del p.cash
        del p.today_account_value
        investments = pd.DataFrame.from_dict(p, orient="index")
        with pd.ExcelWriter(path) as writer:
            investments.to_excel(writer, sheet_name="investment")
            cash.to_excel(writer, sheet_name="info")

    def load_investment(self, path):
        """load investment information from a file
        should have format below
        sheet "investment"
            columns: ['stock', 'count', 'amount', 'price', 'weight']
                'count': <how many days the security has been hold>,
                'amount': <the amount of the security>,
                'price': <the close price of security in the last trading day>,
                'weight': <the security weight of total investment value>,

        sheet "cash"
            index: ['init_cash', 'cash', 'today_account_value']
            'init_cash': <inital cash when account was created>,
            'cash': <current cash in account>,
            'today_account_value': <current total account value, should equal to sum(price[stock]*amount[stock])>
        """
        path = pathlib.Path(path)
        investments = pd.read_excel(open(path, "rb"), sheet_name="investment", index_col=0)
        cash_record = pd.read_excel(open(path, "rb"), sheet_name="info", index_col=0)
        investments = investments.to_dict(orient="index")
        init_cash = cash_record.loc["init_cash"].values[0]
        cash = cash_record.loc["cash"].values[0]
        today_account_value = cash_record.loc["today_account_value"].values[0]
        last_trade_date = cash_record.loc["last_trade_date"].values[0]

        # assign values
        self.investment = {}
        self.init_cash = init_cash
        self.investment = investments
        self.investment.cash = cash
        self.investment.today_account_value = today_account_value

        return None if pd.isna(last_trade_date) else pd.Timestamp(last_trade_date)
