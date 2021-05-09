#!/usr/bin/python38
# -*- coding: utf-8 -*-

import os
import datetime
import importlib
import json
import re
import time
from dev_global.env import CONF_FILE
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from mars.log_manager import log_with_return, log_wo_return
from mars.utils import read_json
# modules loaded into module list
import service_api.event
import service_api.event2

__version__ = '1.2.7'


def decoration_print(func):
    """
    decorater of print function.
    """
    def wrap_func(*args, **kv):
        print('+-' * 15)
        time_string = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"Time: {time_string}")
        func(*args, **kv)
        print('+-' * 15)
    return wrap_func


class taskConfig(object):
    """
    Class for task manager config.
    """
    def __init__(self, task_manage_name: str) -> None:
        self.task_manage_name = task_manage_name
        self._timezone = 'Asia/Shanghai'
        _, _taskfile = read_json("task_file", CONF_FILE)
        self.TASK_FILE = _taskfile
        self.FLAG = taskFlag()

    @property
    def timezone(self):
        return self._timezone


class taskFlag(object):
    """
    private class used in taskConfig only.
    """
    def __init__(self) -> None:
        self.NEW = 'A'
        self.MOD = 'U'


class taskManager(BackgroundScheduler):
    """
    Task manager is a object to manage tasks.
    It will run tasks according to task.json file.
    It will auto load modules without reboot system.
    Workflow : \n
    1.load_event, reload liboratories\n
    2.load_task_file, load task.json\n
    3.
    """
    def __init__(self, task_config: taskConfig, taskfile='', task_manager_name=None, gconfig={}, **options):
        super(BackgroundScheduler, self).__init__(timezone='Asia/Shanghai', **options)
        self.task_manager_name = task_manager_name
        self.start_time = datetime.datetime.now()
        if os.path.exists(taskfile):
            self.taskfile = taskfile
            self.task_solver = taskSolver(taskfile)
            self._task_list = []
        else:
            # if task file is not found.
            raise FileNotFoundError(taskfile)
        self.config = task_config

    def __str__(self):
        runtime = datetime.datetime.now() - self.start_time
        h, m = timedelta_convert(runtime)
        return f"<Task manager ({self.task_manager_name}) has running for {h}:{str(m).zfill(2)}:00>"

    def _update_task_list(self):
        """
        Query task from mysql.
        """
        self._task_list = self.get_jobs()

    @log_with_return
    def check_task_list(self):
        """
        Set flag for tasks. 'A' for new task, 'U' for exist task.
        """
        temp_task_list = self.load_task_list()
        self._update_task_list()
        for task in temp_task_list:
            task.flag = self.config.FLAG.NEW
            for old_task in self._task_list:
                if task.name == old_task.name:
                    task.flag = self.config.FLAG.MOD
        return temp_task_list

    @log_wo_return
    def task_manage(self, task_list):
        """
        Manage task manager to add or update tasks.
        """
        for task in task_list:
            if task.flag == self.config.FLAG.NEW:
                self.add_job(
                    task.func, trigger=task.trigger,
                    id=task.name,
                    timzone=pytz.timezone(self.config.timezone))
            elif task.flag == self.config.FLAG.MOD:
                self.reschedule_job(
                    task.name, trigger=task.trigger,
                    timzone=pytz.timezone(self.config.timezone))

    @log_with_return
    def load_task_list(self):
        with open(self.taskfile, 'r') as f:
            jsdata = json.load(f)
        task_list = []
        for task_data in jsdata:
            task = self.task_solver.task_resolve(task_data)
            if task:
                task_list.append(task)
        return task_list

    @decoration_print
    def task_report(self):
        self.print_jobs()


class taskBase(object):
    def __init__(self, task_name, func, trigger):
        self.name = task_name
        self.func = func
        self.trigger = trigger
        self.flag = None

    def __str__(self):
        return f"<{self.name}:{self.flag}:{self.trigger}>"


class taskSolver(object):
    def __init__(self, taskfile=None, timezone="Asia/Shanghai"):
        if taskfile:
            self.module_list = [
                service_api.event,
                ]
            self.taskfile = taskfile
            self.timezone = timezone
            self.func_list = {}
            self.load_event()
        else:
            raise FileNotFoundError(taskfile)

    @log_wo_return
    def load_event(self):
        """
        This function will reload modules automatically.
        """
        for mod in self.module_list:
            importlib.reload(mod)
            for func in mod.__all__:
                self.func_list[func] = eval(f"{mod.__name__}.{func}")

    @log_with_return
    def task_resolve(self, jsdata: dict):
        task = None
        if task_name := jsdata['task']:
            if (func := self.func_list.get(task_name)) and (trigger := self._trigger_resolve(jsdata)):
                task = taskBase(task_name, func, trigger)
        return task

    @log_with_return
    def _trigger_resolve(self, jsdata):
        """
        Resolve the trigger.
        FORMAT:
        day_of_week: 0~6 stands for sun to sat.
        day        : 1~31 stands for day in month.
        hour       : 18 stands for 18:00.
        time       : 18:31 stands for real time.
        work day   : in time format like 18:31, means time on work day.
        sat, sun   : the same like work day
        """
        for k in jsdata.keys():
            if k == 'day of week':
                trigger = CronTrigger(day_of_week=jsdata['day_of_week'], timezone=self.timezone)
            elif k == 'day':
                trigger = CronTrigger(day=jsdata['day'], timezone=self.timezone)
            elif k == 'hour':
                trigger = CronTrigger(hour=jsdata['hour'], timezone=self.timezone)
            elif k == 'time':
                if m := re.match(r'(\d{1,2}):(\d{2})', jsdata['time']):
                    trigger = CronTrigger(
                        hour=int(m.group(1)),
                        minute=int(m.group(2)),
                        timezone=self.timezone)
                else:
                    trigger = None
            elif k == 'work day':
                if m := re.match(r'(\d{1,2}):(\d{2})', jsdata['work day']):
                    trigger = CronTrigger(
                        day_of_week='mon,tue,wed,thu,fri',
                        hour=int(m.group(1)),
                        minute=int(m.group(2)),
                        timezone=self.timezone)
                else:
                    trigger = None
            elif k == 'sat':
                if m := re.match(r'(\d{1,2}):(\d{2})', jsdata['sat']):
                    trigger = CronTrigger(
                        day_of_week='sat',
                        hour=int(m.group(1)),
                        minute=int(m.group(2)),
                        timezone=self.timezone)
                else:
                    trigger = None
            elif k == 'sun':
                if m := re.match(r'(\d{1,2}):(\d{2})', jsdata['sun']):
                    trigger = CronTrigger(
                        day_of_week='sun',
                        hour=int(m.group(1)),
                        minute=int(m.group(2)),
                        timezone=self.timezone)
                else:
                    trigger = None
            else:
                trigger = None
        return trigger

    def _load_task_file(self) -> dict:
        with open(self.taskfile, 'r') as f:
            task_json = json.load(f)
        return task_json


def timedelta_convert(dt: datetime.timedelta) -> tuple:
    """
    convert timedelta to hh:mm
    param  : dt  datetime.timedelta
    return : ( hours of int, minute of int )
    """
    h = 24 * dt.days + dt.seconds // 3600
    m = (dt.seconds % 3600) // 60
    return (h, m)


def format_timedelta(dt: datetime.timedelta) -> str:
    h, m = timedelta_convert(dt)
    return f"{h}:{str(m).zfill(2)}"


if __name__ == "__main__":
    import datetime
    event = taskManager(
        '/home/friederich/Dev/neutrino2/config/task.json', 'neutrino')
    event.task_solver.load_event()
    # print(event.task_solver.func_list)
    result = event.task_solver._load_task_file()
    task_list = []
    for task_data in result:
        task = event.task_solver.task_resolve(task_data)
        if task:
            task_list.append(task)
    print(task_list)
