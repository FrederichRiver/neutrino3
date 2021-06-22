import pandas as pd
from datetime import date, datetime, timedelta
import re


class Kalendar(object):
    """
    一个迭代器，可以返回交易日的日期
    """
    def __init__(self, start: tuple, end: tuple) -> None:
        if result := re.match(r'(\d{4})-(\d+)-(\d+)', start):
            self._start = pd.Timestamp(year=int(result[1]), month=int(result[2]), day=int(result[3]))
        if result := re.match(r'(\d{4})-(\d+)-(\d+)', end):
            self._end = pd.Timestamp(year=int(result[1]), month=int(result[2]), day=int(result[3]))
        else:
            self._end = pd.Timestamp.today()
        self.ENV = {}
        self.holiday = []
        self.lawday = [(1,1), (4,5), (5,1), (5,2), (10,1), (10,2), (10,3)]
        self.length = 100
        self._today = self._start
        self.i = 0

    def config(self, country: str):
        # 定义国家和地区，对应不同的假日(中国，美国，日本，香港，德国，英国，中东)
        # 定义交易品种(股票，期货等)
        self.ENV['country'] = country

    def __str__(self) -> str:
        TODAY = self._start.strftime('%Y-%m-%d')
        return TODAY

    def __next__(self):
        if self._today < self._end:
            self._today = self._start + pd.Timedelta(days=self.i)
            self.i += 1
            while not self.isTradeday(self._today):
                self._today = self._start + pd.Timedelta(days=self.i)
                self.i += 1
        else:
            raise StopIteration
        return self._today

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

    def isHoliday(self, d: date) -> bool:
        """
        判断是否是节日
        """
        return True if d in self.holiday else False

    def isLawday(self, d: date) -> bool:
        if (d.month, d.day) in self.lawday:
            return True
        else:
            return False

    def isWeekend(self, d: date) -> bool:
        """
        判断是否是周末
        """
        return True if d.weekday() in [5, 6] else False

    def isTradeday(self, d: date) -> bool:
        """
        如果是交易日，就返回True，否则返回False。这个API引用了is_holiday和is_weekend
        """
        return False if self.isHoliday(d) or self.isWeekend(d) else True

if __name__ == '__main__':
    ca = Kalendar('2021-01-03', '2021-02-03')