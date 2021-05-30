#!/usr/bin/python3


class ForeignExchange(object):
    def __init__(self) -> None:
        self.__ratio = { "USD2CNY": 6.35, "EUR2CNY": 7.73, "GBP2CNY": 9.06, "HKD2CNY": 0.81, "JPY2CNY": 0.0581}

    def update(self):
        pass

    def USD2CNY(self, cash: float) -> float:
        return self.__ratio["USD2CNY"] * cash