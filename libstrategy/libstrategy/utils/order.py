#!/usr/bin/python3


class TradeOrder(object):

    SELL = -1
    BUY = 1

    def __init__(self, stock_code: str, trade_time: str, direction, price: float, bid: int) -> None:
        """Parameter
        direction : Order.SELL(-1) for sell; Order.BUY(1) for buy
        trade_time: str in format Y-m-d
        stock_code : str
        amount : float
        # trade_date : pd.Timestamp
        price : float
        factor : float
            presents the weight factor assigned in Exchange()
        """
        # check direction
        if direction not in {TradeOrder.SELL, TradeOrder.BUY}:
            raise NotImplementedError("direction not supported, `Order.SELL` for sell, `Order.BUY` for buy")
        self.stock_code = stock_code
        # amount of generated orders
        self.price = price
        self.bid = bid
        # amount of successfully completed orders
        self.deal_amount = 0
        self.direction = direction
        self.trade_time = trade_time
        self.price = price

    def __str__(self) -> str:
        direction = "Buy" if self.direction > 0 else "Sell"
        return f"{direction} {self.bid} {self.stock_code} at price of {self.price} at {self.trade_time}."