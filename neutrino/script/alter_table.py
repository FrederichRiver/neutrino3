#!/usr/bin/python38
from libmysql_utils.mysql8 import mysqlBase, GLOBAL_HEADER


event = mysqlBase(GLOBAL_HEADER)
result = event.engine.execute("show tables").fetchall()
for table in result:
    if table[0].startswith('SZ') or table[0].startswith('SH'):
        print(table[0])
        sql1 = f"Alter table {table[0]} change highest_price high_price float"
        sql2 = f"Alter table {table[0]} change lowest_price low_price float"
        try:
            event.engine.execute(sql1)
            event.engine.execute(sql2)
        except Exception:
            pass
