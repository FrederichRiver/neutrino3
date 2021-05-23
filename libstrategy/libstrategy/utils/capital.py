#!/usr/bin/python38


from libstrategy.utils.order import TradeMessage


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


class CapitalBase(object):
    def __init__(self, stock_code: str, currency=0.0) -> None:
        self.stock_code = stock_code
        self.unit = 'CNY'
        self.price = 0.0
        self.volume = 0.0
        self.currency = currency
        self.TAX = StampTax()
        self.Fee = TransferFee()
        self.Comm = StockCommission()
        self.count = 0
        self.weight = 0.0

    def buy(self, **args):
        self.volume += args.get('volume')
        vol = args.get('price') * args.get('volume')
        # Any fee
        fee = self.Fee(vol)
        commission = self.Comm(vol)
        # settle
        self.currency -= round(vol, 2)
        self.currency -= (fee + commission)
        return TradeMessage(self.stock_code, 'null', args.get('price'), args.get('volume'))

    def sell(self, **args):
        self.volume += args.get('volume')
        vol = args.get('price') * args.get('volume')
        # Any fee
        tax = self.TAX(vol)
        fee = self.Fee(vol)
        commission = self.Comm(vol)
        # settle
        self.currency -= round(vol, 2)
        self.currency -= (tax + fee + commission)
        return TradeMessage(self.stock_code, 'null', args.get('price'), args.get('volume'))

    def settle(self, price: float):
        self.currency -= price * self.volume
        return TradeMessage(self.stock_code, 'null', price, self.volume)

    def __str__(self):
        text = f"Capital {self.stock_code}, volume {self.volume}, currency {self.currency}"
        return text


class InvestGroup(object):
    def __init__(self) -> None:
        self.pool = []

    

if __name__ == '__main__':
    capital = CapitalBase('SH600000', 5000.0)
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
