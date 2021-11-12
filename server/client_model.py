#!/usr/bin/python3
import socket
import time
import pickle

HOST = '127.0.0.1'    # The remote host
PORT = 9000              # The same port as used by the server



class MsgFrame(object):
    def __init__(self, stock_code: str, start: str, end: str) -> None:
        self.stock_code = stock_code
        self.start_time = start
        self.end_time = end

    def __str__(self):
        return f"SELECT close_price from {self.stock_code} WHERE trade_date BETWEEN '{self.start_time}' and '{self.end_time}'"

    @property
    def sql(self):
        return self.__str__()

class Client(object):
    def __init__(self, host, port) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.FLAG = 1

    def send(self, msg):
        self.client.send(msg)
        data = self.client.recv(102400)
        result = pickle.loads(data)
        return result

    def close(self):
        self.client.close()
        self.FLAG = 0

    def request(self):
        import json
        req = MsgFrame('SH600000', '2019-01-01', '2020-12-31')
        return pickle.dumps(req)

client = Client(HOST, PORT)
for i in range(3):
    data = client.send(client.request())
    print(data)
client.close()