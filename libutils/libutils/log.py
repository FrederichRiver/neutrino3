#!/usr/bin/python38
import os
import re
import logging
import logging.config
import time
from logging.handlers import TimedRotatingFileHandler
from dev_global.env import LOG_TIME_FMT, PROG_NAME
from dev_global.path import LOG_FILE
from functools import wraps


class Neulogger(object):
    def __init__(self, log_file: str) -> None:
        if os.path.exists(log_file):
            self.LOG_FILE = log_file
        else:
            raise FileNotFoundError(f"Log file {log_file} is not found.")
        self.LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
        self.TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    @property
    def logger(self) -> logging.Logger:
        # step 1: create a logger
        neulog = logging.getLogger()
        # step 2: set logger level
        neulog.setLevel(logging.INFO)
        # step 3: create a handler
        Time_Handler = TimedRotatingFileHandler(self.LOG_FILE, when='midnight')
        # step 4: set handler level
        Time_Handler.setLevel(logging.INFO)
        # step 6: add log format to handler
        neu_format = logging.Formatter(self.LOG_FORMAT, self.TIME_FORMAT)
        Time_Handler.setFormatter(neu_format)
        # step 7: add handler to logger
        neulog.addHandler(Time_Handler)
        return neulog


neulog = Neulogger(LOG_FILE).logger


def method(call):
    def wrapper(*args, **kwargs):
        return call(*args, **kwargs)
    return wrapper


class Log(object):
    def __init__(self, func) -> None:
        self._func = func

    def __call__(self, *args, **kv):
        try:
            result = self._func(*args, **kv)
        except Exception as e:
            # neulog.addHandler(Time_Handler)
            neulog.error(f"<Module> {self._func.__name__} <Message> {e}")
            # neulog.removeHandler(Time_Handler)
            result = None
        return result


class LogMonitor(object):
    def __init__(self, log_file: str) -> None:
        self.log_file = log_file

    def run(self):
        while True:
            if not os.path.exists(self.log_file):
                create_file = open(self.log_file, 'a')
                create_file.close()
                with open(self.log_file, 'a') as write_null:
                    os.dup2(write_null.fileno(), 1)
                with open(self.log_file, 'a') as error_null:
                    os.dup2(error_null.fileno(), 2)
                neulog.info(f"{PROG_NAME} started with pid {os.getpid()}.")
            time.sleep(10)
