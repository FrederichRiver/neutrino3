#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
# import re
import datetime
from libutils.log import neulog, Log
from libmysql_utils.mysql8 import create_table, mysqlBase, mysqlHeader
from libmysql_utils.header import GLOBAL_HEADER
from libbasemodel.stock_model import StockBase
from libbasemodel.form import Base
from libutils.utils import read_json


__version__ = '1.1.6'
__all__ = ['event_mysql_backup', 'event_initial_database']


# event back up


class databaseBackup(object):
    def __init__(self):
        # database will be backuped.
        self.database_list = []
        # Setting path.
        _, data_path = read_json('data_path', '/opt/neutrino/config/conf.json')
        self.temp_path = f"{data_path}/tmp/"
        self.backup_path = f"{data_path}/neutrino/"
        self.user = 'root'
        self.pwd = '6414939'

    def get_database_list(self):
        """
        Set database list. -> self.database_list
        """
        self.database_list = ['stock', 'natural_language']
        return self.database_list

    def database_backup(self):
        """
        CMD : mysqldump -u user --password=pw --databases db > file.sql
        """
        for db in self.database_list:
            dumpcmd = (
                f"mysqldump -u {self.user} "
                f"--password={self.pwd} "
                f"--databases {db}"
                f" > {self.temp_path}{db}.sql"
                )
            os.system(dumpcmd)

    def file_compress(self):
        zip_time = time.strftime('%Y-%m-%d')
        file_name = 'mysql_database'
        compress_file = f"{self.backup_path}{file_name}_{zip_time}.tar.gz"
        os.chdir(self.backup_path)
        os.system(f"tar -czvPf {compress_file} {self.temp_path}")

    def remove_old_backup(self):
        file_list = os.listdir(self.backup_path)
        for f in file_list:
            file_name, file_time = self.get_file_info(self.backup_path + f)
            if file_time < self.get_today_time(3):
                os.system(f"rm {file_name}")

    def get_today_time(self, n=0):
        import datetime
        timestamp = datetime.datetime.now()
        dest_time = timestamp - datetime.timedelta(days=n)
        return dest_time

    def get_file_info(self, file_name):
        """
        get timestamp from file info.
        return type timestamp
        """
        result = os.stat(file_name)
        file_time = datetime.datetime.fromtimestamp(result.st_mtime)
        return file_name, file_time


@Log
def event_initial_database():
    mysql = mysqlBase(GLOBAL_HEADER)
    create_table(formTemplate, mysql.engine)
    create_table(formFinanceTemplate, mysql.engine)
    create_table(formInfomation, mysql.engine)


@Log
def event_mysql_backup():
    event = databaseBackup()
    event.get_database_list()
    event.database_backup()
    event.file_compress()
    neulog.info("Database backup successfully.")


def event_mysql_remove_backup():
    from libmysql_utils.database_manager import databaseBackup
    event = databaseBackup()
    event.remove_old_backup()


def change_stock_template_definition():
    root_header = mysqlHeader('stock', 'stock2020', 'stock')
    event = StockBase(root_header)
    stock_list = event.get_all_stock_list()
    col = [
        'close_price', 'highest_price', 'lowest_price',
        'open_price', 'prev_close_price', 'change_rate', 'amplitude',
        'turnover']
    for stock_code in stock_list:
        # print(stock_code)
        for name in col:
            sql = f"alter table {stock_code} change {name} {name} float default 0"
            event.mysql.engine.execute(sql)
        sql = f"alter table {stock_code} change volume volume int(11) default 0"
        event.mysql.engine.execute(sql)
        sql = f"alter table {stock_code} change adjust_factor adjust_factor float default 1"
        event.mysql.engine.execute(sql)


def test():
    event = databaseBackup()
    event.remove_old_backup()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("maint init|backup")
        raise SystemExit(1)
    if sys.argv[1] == "init":
        try:
            event_initial_database()
        except Exception as e:
            print(e)
    elif sys.argv[1] == "backup":
        try:
            event_mysql_backup()
        except Exception as e:
            print(e)
    elif sys.argv[1] == "test":
        test()
