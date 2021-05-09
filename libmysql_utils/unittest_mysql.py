#!/usr/bin/python38
import unittest
from libmysql_utils import mysql8


class unittest_mysql(unittest.TestCase):
    def setUp(self):
        print("Test start.")

    def tearDown(self):
        pass

    def test_connect(self):
        header = mysql8.mysqlHeader(acc="stock", pw="stock2020", db="stock")
        mysql = mysql8.mysqlBase(header)
        version = mysql.engine.execute("select version()").fetchone()
        print(f"MySQL version: {version[0]}")

    def test_json2sql(self):
        header = mysql8.mysqlHeader(acc="stock", pw="stock2020", db="stock")
        j2s = mysql8.Json2Sql(header)
        j2s.load_table('template_stock')


if __name__ == "__main__":
    unittest.main()
