#!/usr/bin/python38
from abc import ABCMeta

class SignalBase(metaclass=ABCMeta):
    def __init__(self) -> None:
        """
        0 means start
        -1 means end
        others depends on definition.
        """
        self._value = 0

    @property
    def signal(self):
        return self._value

    def set_end(self):
        self._value = -1
        return self._value


class SignalPairTrade(SignalBase):
    """
    signal value
    0: start
    1: long A short B
    2: long B short A
    -1: end
    """
    def __init__(self) -> None:
        super().__init__()
        self._state = 0
        self._high = 0.0
        self._low = 0.0
        self.beta = 0.0
        self.alpha = 0.0

    def set_threshold(self, **kwargs):
        self._high = kwargs.get('high')
        self._low = kwargs.get('low')
        self.beta = kwargs.get('beta')
        self.alpha = kwargs.get('alpha')

    def __call__(self, a: float, b: float) -> None:
        d = a - self.beta * b - self.alpha
        if (d > self._high) and (self._state != 1):
            self._value = 1
            self._state = 1
        elif (d < self._low) and (self._state != 2):
            self._value = 2
            self._state = 2
        else:
            self._value = 0
        return self.signal


