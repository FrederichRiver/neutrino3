from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from polaris.mysql8 import mysqlBase, mysqlHeader
from index import models

# Create your views here.


def get_data():
    from libmysql_utils.mysql8 import mysqlBase, mysqlHeader
    head = mysqlHeader(acc="stock", pw="stock2020", db="stock", host="localhost")
    event = mysqlBase(head)
    result = event.select_values('wti_future', 'datetime, price,high_price,prev_price')
    print(result[0])


def index(request):
    context = {'stock_data': stock_data, 'device_type': device}
    return render(request, 'index.html', context)


if __name__ == '__main__':
    get_data()
