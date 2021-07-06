from abc import ABC
from enum import Enum


class EventBase(ABC):
    def __init__(self) -> None:
        self.id = 0
        self._timestamp = None
        self.dataline = {}


class EventType(Enum):
    XRDR = 1


class XrdrEvent(EventBase):
    def __init__(self, date_time, dataline) -> None:
        self.id = 1
        self._timestamp = date_time
        self.stock_id = dataline['stock_code']
        self.bonus= dataline['bonus']
        self.increase = dataline['increase']
        self.dividend = dataline['dividend']

    def __str__(self) -> str:
        text = f"{self.stock_id} Xrdr on {self._timestamp}, bonus {self.bonus}, increase {self.increase}, dividend {self.dividend}."
        return text
