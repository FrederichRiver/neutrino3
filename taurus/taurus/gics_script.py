#!/usr/bin/python38
import re
import json

def gics_to_json_file():
    path = "/home/friederich/Downloads/tmp/"
    origin_file = path + 'GICS2'
    dest_file = path + 'GICS3'
    dest_jfile = path + 'GICS4.json'
    x = {}
    gics = []
    gics_dict = {}
    with open(origin_file, 'r') as f:
        while line := f.readline():
            if line:
                if m := re.match(r'(\d+):(\w+)', line):
                    x[m.group(1)] = m.group(2)
        for k, v in x.items():
            gics_dict = {}
            gics_dict['index'] = k
            gics_dict['name'] = v
            gics.append(gics_dict)
    with open(dest_jfile, 'w') as j:
        json.dump(gics, j, ensure_ascii=False)


def gics_to_sql():
    from dev_global.env import GLOBAL_HEADER
    from venus.stock_base import StockEventBase
    path = "/home/friederich/Dev/neutrino2/data/"
    dest_jfile = path + 'GICS4.json'
    with open(dest_jfile, 'r') as j:
        result = j.read()
        gics_j = json.loads(result)
    event = StockEventBase(GLOBAL_HEADER)
    for gics in gics_j:
        if len(gics['index']) == 2:
            level = 0
        elif len(gics['index']) == 4:
            level = 1
        elif len(gics['index']) == 6:
            level = 2
        elif len(gics['index']) == 8:
            level = 3
        else:
            level = 9
        sql = (
            "INSERT IGNORE into gics (code,name,level) "
            f"VALUES ('{gics['index']}','{gics['name']}',{level})"
        )
        event.mysql.engine.execute(sql)



if __name__ == "__main__":
    gics_to_sql()
