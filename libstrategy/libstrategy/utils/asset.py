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

    def buy(self, **args):
        """
        keys: volume, price
        """
        self.volume += args.get('volume')
        vol = args.get('price') * args.get('volume')
        # Any fee
        fee = self.Fee(vol)
        commission = self.Comm(vol)
        # settle
        self.cash -= round(vol, 2)
        self.cash -= (fee + commission)
        self.price = args.get('price')
        return TradeOrder(self.stock_code, 'null', 1, args.get('price'), args.get('volume'), 1.0)

    def sell(self, **args):
        self.volume += args.get('volume')
        vol = args.get('price') * args.get('volume')
        # Any fee
        tax = self.TAX(vol)
        fee = self.Fee(vol)
        commission = self.Comm(vol)
        # settle
        self.cash -= round(vol, 2)
        self.cash -= (tax + fee + commission)
        self.price = args.get('price')
        return TradeOrder(self.stock_code, 'null', -1, args.get('price'), args.get('volume'), 1.0)

    def settle(self, price: float):
        volume = self.volume
        self.cash += price * self.volume
        self.volume = 0
        return TradeOrder(self.stock_code, 'null', -1, price, volume, 1.0)

    @property
    def value(self):
        return self.volume * self.price + self.cash

    def __str__(self):
        text = f"Asset {self.stock_code}, volume {self.volume}, currency {'%.2f' % self.cash}"
        return text


class StockAsset(AssetBase):
    pass


class InvestGroup(object):
    def __init__(self) -> None:
        self.pool = []

    

if __name__ == '__main__':
    capital = AssetBase('SH600000', 5000.0)
    print(capital)
    trade_set = [
        {'price': 6.02, 'volume': 100},
        {"price": 5.37, "volume": 100},
        {"price": 6.75, "volume": 100},
        {"price": 7.12, "volume": -100},
        {"price": 7.34, "volume": -100},
        {"price": 8.57, "volume": -100},
    ]
    for trade in trade_set:
        if trade['volume'] > 0:
            capital.buy(**trade)
        else:
            capital.sell(**trade)
        print(capital)
    capital.settle(9.03)
    print(capital)
