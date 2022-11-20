#!/usr/bin/python3
"""
This is a library dealing with mysql which is based on sqlalchemy.
Library support MYSQL version 8.
Auther: Friederich River
"""
from abc import ABCMeta
import abc
import json
import datetime
from typing import Tuple
from libutils.log import Log, method
import pandas as pd
from dev_global.env import TIME_FMT
from dev_global.path import CONF_FILE
from pandas import Series
from pandas.core.frame import DataFrame
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


__version__ = '4.4.20'

__all__ = ['mysqlBase', 'mysqlHeader', 'GLOBAL_HEADER']


class mysqlHeader(object):
    """ Here defines the parameters passed into mysql engine.
    """

    def __init__(self, acc, pw, db,
                 host='localhost', port=3306, charset='utf8'):
        if not isinstance(acc, str):
            raise TypeError(f"{acc=} is not correct.")
        if not isinstance(pw, str):
            raise TypeError("Password is not correct.")
        if not isinstance(db, str):
            raise TypeError(f"{db=} is not correct.")
        self.account = acc
        self.password = pw
        self.database = db
        self.host = host
        self.port = port
        self.charset = 'utf8'

    def __str__(self):
        return f"<{self.account}@{self.host}:{self.port}>"


class mysqlMeta(metaclass=abc.ABCMeta):
    def __init__(self, header: mysqlHeader):
        """
        :param header: Defines the mysql engine parameters.
        :param engine: is the object returned from create_engine.
        :param session: contains the cursor object.
        """
        self.account = header.account
        self.host = header.host
        self.port = header.port
        self.database = header.database
        mysql_url = (
            f"mysql+pymysql://{header.account}:"
            f"{header.password}"
            f"@{header.host}:{header.port}"
            f"/{header.database}")
        self.engine = create_engine(mysql_url, encoding='utf8', echo=False)
        s = sessionmaker(bind=self.engine)
        self.session = s()

    def __str__(self):
        return f"mysql engine <{self.account}@{self.host}>"

    @property
    def version(self):
        """
        Use for testing. Return mysql version in str format. 
        """
        version = self.engine.execute("SELECT VERSION()").fetchone()
        return version[0]


class mysqlBase(object):
    def __init__(self, header):
        """
        :param header: Defines the mysql engine parameters.
        :param engine: is the object returned from create_engine.
        :param session: contains the cursor object.
        """
        self.account = header.account
        self.host = header.host
        self.port = header.port
        self.database = header.database
        mysql_url = (
            f"mysql+pymysql://{header.account}:"
            f"{header.password}"
            f"@{header.host}:{header.port}"
            f"/{header.database}")
        self.engine = create_engine(mysql_url, encoding='utf8', echo=False)
        db_session = sessionmaker(bind=self.engine)
        self.session = db_session()
 
    def __str__(self):
        return f"mysql engine <{self.account}@{self.host}>"


    def insert(self, table: str, value: dict):
        """
        This method is use only when the value is surely confirmed.
        """
        if isinstance(value, dict):
            sql = f"INSERT IGNORE INTO {table} set "
            for key in value.keys():
                sql += f"{key}={value[key]} "
            self.engine.execute(sql)

    def show_column(self, table: str) -> Series:
        """
        Return a DataFrame like df['col', 'col_type']
        """
        # query for column definition.
        sql = "Show columns from stock_manager"
        select_value = self.engine.execute(sql)
        # translate into dataframe
        df = pd.DataFrame(select_value)
        # dataframe trimming
        col_info = df.loc[:, :1]
        col_info.columns = ['col', 'col_type']
        return col_info

    def select_one(self, table, field, condition) -> Tuple:
        """
        Result is a tuple like structure data.
        """
        sql = f"SELECT {field} FROM {table} WHERE {condition}"
        result = self.engine.execute(sql).fetchone()
        return result

    def simple_select(self, table, field):
        """
        Return a tuple like result
        """
        sql = f"SELECT {field} from {table}"
        result = self.engine.execute(sql)
        return result

    def select_values(self, table, field) -> DataFrame:
        """
        Return a DataFrame type result.
        """
        sql = f"SELECT {field} from {table}"
        select_value = self.engine.execute(sql)
        result = pd.DataFrame(select_value)
        return result

    def update_value(self, table, field, value, condition):
        """
        Single value update.
        """
        sql = (f"UPDATE {table} set {field}={value} WHERE {condition}")
        self.engine.execute(sql)

    def condition_select(self, table, field, condition) -> DataFrame:
        """
        Return a DataFrame type result.
        """
        sql = f"SELECT {field} from {table} WHERE {condition}"
        select_value = self.engine.execute(sql)
        result = pd.DataFrame(select_value)
        return result

    def query(self, sql) -> Tuple:
        result = self.engine.execute(sql).fetchone()
        return result

    def drop_table(self, table_name: str):
        sql = f"DROP TABLE {table_name}"
        self.engine.execute(sql)
        return 1

    def truncate_table(self, table_name: str):
        sql = f"TRUNCATE TABLE {table_name}"
        self.engine.execute(sql)
        return 1

    def create_table(self, table):
        """
        : param table: It is form template defined in form module.
        : param engine: It is a sqlalchemy mysql engine.
        """
        table.metadata.create_all(self.engine)
        return 1

    def create_table_from_table(self, name, table_template):
        """
        Base on a table, create another form which
        is similar with the original table.
        Only name was changed.\n
        Params :\n
        name : which is the target table name.\n
        tableName : which is the original table name.\n
        engine : a database engine base on MySQLBase.\n
        """
        sql = f"CREATE table if not exists {name} like {table_template}"
        self.engine.execute(sql)
        return 1

    @method
    @Log
    def exec(self, SQL: str):
        self.engine.execute(SQL)
        return 1


class mysqlTest(mysqlBase):
    @property
    def version(self):
        """
        Use for testing. Return mysql version in str format. 
        """
        version = self.engine.execute("SELECT VERSION()").fetchone()
        return version[0]


class mysqlQuery(mysqlBase):
    def __str__(self):
        return f"mysql query engine <{self.account}@{self.host}>"

    def select_one(self, table, field, condition) -> Tuple:
        """
        Result is a tuple like structure data.
        """
        sql = f"SELECT {field} FROM {table} WHERE {condition}"
        result = self.engine.execute(sql).fetchone()
        return result

    def select_values(self, table, field) -> DataFrame:
        """
        Return a DataFrame type result.
        """
        sql = f"SELECT {field} from {table}"
        select_value = self.engine.execute(sql)
        df = pd.DataFrame(select_value)
        return df

    def condition_select(self, table, field, condition) -> DataFrame:
        """
        Return a DataFrame type result.
        """
        sql = f"SELECT {field} from {table} WHERE {condition}"
        select_value = self.engine.execute(sql)
        df = pd.DataFrame(select_value)
        return df


def _drop_all(base, engine):
    """
    This will drop all tables in database.
    It is a private method only for maintance.
    """
    base.metadata.drop_all(engine)


def create_table(table, engine):
    """
    : param table: It is form template defined in form module.
    : param engine: It is a sqlalchemy mysql engine.
    """
    table.metadata.create_all(engine)


class Json2Sql(mysqlBase):
    """
    Translate Json data into Sql (insert or update)\n
    Working flow :\n
    1. load_table;\n
    2. query and fetch dataframe;\n
    3. translate dataframe to json;\n
    4. to_sql (insert or update)
    """
    def __init__(self, header):
        super(Json2Sql, self).__init__(header)
        self.table_def = dict()
        self.tablename = None

    def load_table(self, tablename):
        """
        Must be a dict to get the definition.\n
        Load table infomation like column name and type.\n
        Return : dict{ column_name: column_type in sql}
        """
        self.table_def = dict()
        self.tablename = tablename
        # query for column definition.
        sql = f"Show columns from {self.tablename}"
        select_value = self.engine.execute(sql)
        # translate into dataframe
        df = pd.DataFrame(select_value)
        # dataframe trimming
        col_info = df.loc[:, :1]
        col_info.columns = ['col', 'col_type']
        # tranlate dataframe into json
        for index, row in col_info.iterrows():
            self.table_def[row['col']] = row['col_type']
        return self.table_def

    @staticmethod
    def dataframe_to_json(df: pd.DataFrame, keys=[]) -> list:
        """
        Key is the definition of insert table.
        """
        jsonlist = []
        tmp = {}
        for index, row in df.iterrows():
            tmp = {}
            for k in keys:
                tmp[k] = row[k]
            jsonlist.append(tmp)
        return jsonlist

    def to_sql_insert(self, json_data: json, table_name=None):
        """
        Generate a sql like 'Replace into <table> (<cols>) values (<vals>)'
        """
        # initial 2 list
        col_section = []
        value_section = []
        # set table name
        if not table_name:
            table_name = self.tablename
        # iter for each key in json.
        for k, v in json_data.items():
            if k in self.table_def.keys():
                col_section.append(k)
                # values should be tranlate into sql format
                value_section.append(self.trans_value(v))
        # combine into sql and returns.
        col = ','.join(col_section)
        val = ','.join(value_section)
        sql = f"REPLACE into {table_name} ({col}) values ({val})"
        return(sql)

    def to_sql_update(self, json_data: json, keys: list, table_name=None):
        val = []
        cond = []
        if not table_name:
            table_name = self.tablename
        for k, v in json_data.items():
            if k in self.table_def.keys():
                tmp = f"{k}={self.trans_value(v)}"
                val.append(tmp)
        value = ','.join(val)
        for k in keys:
            tmp = f" ({k}={self.trans_value(json_data[k])}) "
            cond.append(tmp)
        condition = 'AND'.join(cond)
        sql = f"UPDATE {table_name} set {value} WHERE {condition}"
        return sql

    @staticmethod
    def trans_value(value):
        if isinstance(value, str):
            result = value if value else 'NULL'
            return f"'{result}'"
        elif isinstance(value, int):
            return f"{value}"
        elif isinstance(value, float):
            return f"{value}"
        elif isinstance(value, datetime.date):
            if pd.isna(value):
                return 'NULL'
            else:
                return f"'{value.strftime(TIME_FMT)}'"
        else:
            return 'NULL'

