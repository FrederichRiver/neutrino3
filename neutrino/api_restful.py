#!/usr/bin/python38
from venus.stock_base2 import StockBase
from flask import Flask
from flask import jsonify
from dev_global.basic import deamon


# Usage: import app, and app.run()
app = Flask('Proton')


# On Server
@app.route('/test')
def test():
    return "Hello world!"


@app.route('/totalstocklist')
def api_get_total_stock_list():
    from polaris.mysql8 import GLOBAL_HEADER
    event = StockBase(GLOBAL_HEADER)
    stock_list = event.get_all_security_list()
    return jsonify(stock_list)


@app.route('/stock')
def api_get_stock():
    from polaris.mysql8 import GLOBAL_HEADER
    from venus.stock_base2 import StockBase
    event = StockBase(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    return jsonify(stock_list)


@app.route('/index')
def api_get_index():
    from polaris.mysql8 import GLOBAL_HEADER
    from venus.stock_base2 import StockBase
    event = StockBase(GLOBAL_HEADER)
    stock_list = event.get_all_index_list()
    return jsonify(stock_list)


if __name__ == "__main__":
    deamon('/tmp/api_restful.pid', '/tmp/api_restful.log', 'flask_api')
    app.run()
    # resolve_stock_list('HK')
