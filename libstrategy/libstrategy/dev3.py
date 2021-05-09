#!/usr/bin/python38

class SignalEngineBase(object):
    def __init__(self) -> None:
        pass

    def signal(self, parameter_list):
        raise NotImplementedError


class EventSignal(SignalEngineBase):
    def signal(self, parameter_list):
        Signal = SignalBase()
        return Signal


class SignalBase(object):
    def __init__(self) -> None:
        self.event_date = None
