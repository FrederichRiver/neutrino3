import unittest
from libmysql_utils.mysql8 import mysqlBase
from libmysql_utils.header import GLOBAL_HEADER, _IP


class TestMysql(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def testConnection(self):
        mysql = mysqlBase(GLOBAL_HEADER)
        print(mysql._version())

    def testIP(self):
        print(_IP)


if __name__ == '__main__':
    unittest.main()
