#!/usr/bin/python38


class Order(object):

    SELL = -1
    BUY = 1

    def __init__(self, stock_code: str, amount: float, trade_date, direction, price: float, factor: float):
        """Parameter
        direction : Order.SELL(-1) for sell; Order.BUY(1) for buy
        stock_code : str
        amount : float
        trade_date : pd.Timestamp
        price : float
        factor : float
            presents the weight factor assigned in Exchange()
        """
        # check direction
        if direction not in {Order.SELL, Order.BUY}:
            raise NotImplementedError("direction not supported, `Order.SELL` for sell, `Order.BUY` for buy")
        self.stock_code = stock_code
        # amount of generated orders
        self.price = price
        self.amount = amount
        # amount of successfully completed orders
        self.deal_amount = 0
        self.trade_date = trade_date
        self.direction = direction
        self.factor = factor

    def __str__(self) -> str:
        direction = "Buy" if self.amount > 0 else "Sell"
        text = f"{direction} {self.amount} {self.stock_code} at price of {self.price}.\n"
        return text


class TradeMessage(object):
    def __init__(self, stock_code: str, trade_time, price: float, bid: int) -> None:
        self.code = stock_code
        self.trade_time = trade_time
        self.price = price
        self.bid = bid

    def __str__(self) -> str:
        direction = "Buy" if self.bid > 0 else "Sell"
        text = f"{direction} {self.bid} {self.code} at price of {self.price}.\n"
        return text