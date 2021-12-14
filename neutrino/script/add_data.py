#!/usr/bin/python3
from libmysql_utils.mysql8 import mysqlBase
from libmysql_utils.header import LOCAL_HEADER

event = mysqlBase(LOCAL_HEADER)

sql1 = f"Insert into industry (idx, industry_name) values (1042, '医药商业')"
try:
    event.engine.execute(sql1)
except Exception:
    pass
