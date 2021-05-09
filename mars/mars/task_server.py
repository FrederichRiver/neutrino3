import socket
from polaris.mysql8 import mysqlBase, mysqlHeader
import datetime


__version__ = (1, 0, 0)


class SocketServer(object):
    """
    event = SocketServer(GLOBAL_HEADER)
    event.run()
    SQL table:
    ids(int) |  task name (varchar)  |  trigger  |  next run time (time) | flag(varchar)
    """
    def __init__(self, header: mysqlHeader, name='127.0.0.1', port=0, forbid_port_table_file=None) -> None:
        self.socket = socket.socket()
        if name is None:
            name = socket.gethostname()
        forbid_port = [0, 21, 22, 23, 80, 8080]
        if port in forbid_port:
            port = 12001
        self.socket.bind((name, port))
        self.task_list = ['test', 'event_mysql_backup', 'system_update']
        self.mysql = mysqlBase(header)

    def run(self):
        self.socket.listen(2)
        while True:
            conn, addr = self.socket.accept()
            # msg format: S/E|xxx
            data = conn.recv(1024)
            flag, content = self.msg_resolve(data.decode())
            delta = 0
            if self._in_task_list(content):
                if flag == 'E':
                    delta = self.next_run_time(content)
                    self._update_time(content, 'time')
                elif flag == 'Q':
                    delta = self.next_run_time(content)
                elif flag == 'U':
                    self.load_task()
            # print(delta)
            conn.send(str.encode(f"{str(delta)}"))
            conn.close()
            # Each time a task is updated, the task list will be reloaded.
            # A update request could be send to active the loading action.
            self.load_task()

    @staticmethod
    def msg_resolve(msg: str):
        flag, content = msg.split('|')
        return flag, content

    def _in_task_list(self, task_name: str) -> bool:
        if isinstance(task_name, str):
            flag = True if task_name in self.task_list else False
        else:
            flag = False
        return flag

    def next_run_time(self, task_name: str) -> int:
        """
        Return a integer present the next run time of task.
        """
        trigger, next_run_time = self.mysql.select_one('task_scheduler', 'time_trigger,next_run_time', f"task_name='{task_name}'")
        if trigger == 'time':
            nrt = int((next_run_time - datetime.datetime.now()).total_seconds())
        else:
            nrt = 0
        return max(nrt, 0)

    def set_task_finish(self, task_name: str) -> int:
        return 0

    def _pending_task(self, task_name: str):
        self.mysql.update_value('task_scheduler', 'flag', "'P'", f"task_name='{task_name}'")

    def _update_time(self, task_name: str, trigger: str):
        n = datetime.datetime.now()
        dt = datetime.timedelta(seconds=86400)
        if trigger == 'time' or trigger == 'day':
            dt = datetime.timedelta(hours=24)
        elif trigger == 'week':
            dt = datetime.timedelta(days=7)
        elif trigger == 'month':
            dt = datetime.timedelta(days=30)
        # workday
        # weekend
        # mon, tue, wed, thu, fri, sat, sun
        nrt = self.mysql.select_one('task_scheduler', 'next_run_time', f"task_name='{task_name}'")
        next_time = nrt[0] + dt
        while next_time < n:
            next_time += dt
        self.mysql.update_value('task_scheduler', 'next_run_time', f"'{next_time}'", f"task_name='{task_name}'")

    def _task_delay(self):
        df = self.mysql.select_values('task_scheduler', 'task_name,time_trigger,next_run_time')
        n = datetime.datetime.now()
        for index, row in df.iterrows():
            if row[2] < n:
                self._update_time(row[0], row[1])

    def load_task(self):
        df = self.mysql.select_values('task_scheduler', 'task_name')
        self.task_list = list(df[0])


class SocketClient(object):
    def __init__(self, name='127.0.0.1', port=0) -> None:
        self.socket = socket.socket()
        if name is None:
            name = socket.gethostname()
        self.name = name
        forbid_port = [0, 21, 22, 23, 80, 8080]
        if port in forbid_port:
            self.port = 12001

    def connect(self):
        self.socket.connect((self.name, self.port))

    def send(self, msg: str):
        self.socket.send(str.encode(msg))

    def recieve(self) -> str:
        data = self.socket.recv(1024)
        return data.decode()

    def close(self):
        self.socket.close()


"""
from polaris.mysql8 import GLOBAL_HEADER
event = SocketServer(GLOBAL_HEADER)
event.run()
# event._update_time('test', 'time')
# event._task_delay()
# event.load_task()
"""
