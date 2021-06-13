#!/usr/bin/python3
from .order import TradeOrder


class FeeBase(object):
    def __init__(self, ratio: float) -> None:
        self.ratio = ratio


class CommissionBase(FeeBase):
    def __init__(self) -> None:
        super().__init__(0.003)


class StockCommission(CommissionBase):
    def __call__(self, vol: float) -> float:
        return max(round(abs(vol * self.ratio), 2), 5.0)


class TransferFee(FeeBase):
    def __init__(self) -> None:
        super().__init__(0.00002)

    def __call__(self, vol: float) -> float:
        return abs(round(vol * self.ratio, 2))


class StampTax(FeeBase):
    def __init__(self) -> None:
        super().__init__(0.001)

    def __call__(self, vol: float):
        return abs(round(vol * self.ratio, 2))


class AssetBase(object):
    def __init__(self, stock_code: str, cash=0.0) -> None:
        self.stock_code = stock_code
        self.unit = 'CNY'
        self.price = 0.0
        self.volume = 0.0
        self.cash = cash
        self.TAX = StampTax()
        self.Fee = TransferFee()
        self.Comm = StockCommission()
        self.count = 0
        self.weight = 0.0

    def buy(self, trade_date: str, volume: int, price: float) -> TradeOrder:
        """
        keys: volume, price
        """
        self.volume += volume
        vol = price * volume
        # Any fee
        fee = self.Fee(vol)
        commission = self.Comm(vol)
        # settle
        self.cash -= vol
        self.cash -= (fee + commission)
        self.price = price
        return TradeOrder(self.stock_code, trade_date, 1, price, volume)

    def sell(self, trade_date: str, volume: int, price: float) -> TradeOrder:
        self.volume -= volume
        vol = price * volume
        # Any fee
        tax = self.TAX(vol)
        fee = self.Fee(vol)
        commission = self.Comm(vol)
        # settle
        self.cash += vol
        self.cash -= (tax + fee + commission)
        self.price = price
        return TradeOrder(self.stock_code, trade_date, -1, price, volume)

    def settle(self, trade_date, price: float) -> TradeOrder:
        volume = self.volume
        self.cash += price * volume
        self.volume = 0
        self.price = price
        return TradeOrder(self.stock_code, trade_date, -1, price, volume)

    @property
    def value(self):
        return self.volume * self.price + self.cash

    def __str__(self):
        text = f"Asset {self.stock_code}, volume {self.volume}, currency {'%.2f' % self.cash}"
        return text


class StockAsset(AssetBase):
    pass

