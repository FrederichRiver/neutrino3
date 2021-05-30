import pandas as pd
from datetime import date, datetime, timedelta


class Kalendar(object):
    """
    一个迭代器，可以返回交易日的日期
    """
    def __init__(self, start: tuple) -> None:
        if start:
            self._start = date(start[0], start[1], start[2])
        else:
            self._start = date.today()
        self.ENV = {}
        self.holiday = []
        self.lawday = [(1,1), (4,5), (5,1), (5,2), (10,1), (10,2), (10,3)]
        self.length = 100
        self.i = 0

    def config(self, country: str):
        # 定义国家和地区，对应不同的假日(中国，美国，日本，香港，德国，英国，中东)
        # 定义交易品种(股票，期货等)
        self.ENV['country'] = country

    def __str__(self) -> str:
        TODAY = datetime.strftime(self._start, '%Y-%m-%d')
        return TODAY

    def __next__(self):
        if self.i < self.length:
            self._start += timedelta(days=1)
            while not self.is_tradeday(self._start):
                self._start += timedelta(days=1)
                self.i += 1
        else:
            raise StopIteration
        return self._start

    def __iter__(self):
        return self

    @classmethod
    def eq(cls, a: date, o: object) -> bool:
        if isinstance(o, pd._libs.tslibs.timestamps.Timestamp):
            if (a.year, a.month, a.day) == (o.year, o.month, o.day):
                result = True
            else:
                result = False
        else:
            result = False
        return result

    def is_holiday(self, d: date) -> bool:
        """
        判断是否是节日
        """
        return True if d in self.holiday else False

    def is_lawday(self, d: date) -> bool:
        if (d.month, d.day) in self.lawday:
            return True
        else:
            return False

    def is_weekend(self, d: date) -> bool:
        """
        判断是否是周末
        """
        return True if d.weekday() in [5, 6] else False

    def is_tradeday(self, d: date) -> bool:
        """
        如果是交易日，就返回True，否则返回False。这个API引用了is_holiday和is_weekend
        """
        return False if self.is_holiday(d) or self.is_weekend(d) else True


