#!/usr/bin/python3
import socket
import time
import threading
import pickle
from libbasemodel.stock_manager import StockBase
from libmysql_utils.header import REMOTE_HEADER

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

class Server(object):
    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', 9000))
        self.server.listen(5)
        self.pool = []


    def add_connection(self, client: threading.Thread):
        self.pool.append(client)
        client.start()

    def remove_connection(self, conn):
        self.pool.remove(conn)

    def run(self):
        while True:
            conn, addr = s.server.accept()
            x = SocketConnection(client= conn)
            self.add_connection(x)


class SocketConnection(threading.Thread):
    Buffer_size = 102400
    def __init__(self, client: socket.socket) -> None:
        super().__init__()
        self.client = client
        self.setDaemon(True)
    
    def run(self):
        while self.client:
            data = self.client.recv(self.Buffer_size)
            if data:
                msg = pickle.loads(data)
                data = self.request_solve(msg)
                self.client.send(data)
        self.client.close()

    def request_solve(self, req: MsgFrame):
        datahub = StockBase(REMOTE_HEADER)
        data = self.engine.execute(req.sql).fetchall()
        result = pickle.dumps(data)
        return result

s = Server()
s.run()
