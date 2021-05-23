#!/usr/bin/python3
from libmysql_utils.header import GLOBAL_HEADER

def service_treasury_yield_data_plot():
    from libbasemodel.data_view import TreasuryYieldView
    from libutils.utils import read_json
    from dev_global.path import CONF_FILE
    image_path = '/home/fred/Downloads'
    # _, image_path = read_json("image_path", CONF_FILE)
    event = TreasuryYieldView(GLOBAL_HEADER, image_path)
    event.plot()

service_treasury_yield_data_plot()