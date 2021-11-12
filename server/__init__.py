__all__ = ['server_model', 'client_model']

import time

class MsgFrame(object):
    def __init__(self, text: str) -> None:
        self.ts = time.time()
        self.msg = text
        self.FLAG = 1

    def __str__(self):
        return f"{self.ts}: {self.msg}"