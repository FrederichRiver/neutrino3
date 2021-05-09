from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from polaris.mysql8 import mysqlBase, mysqlHeader
from django.core import serializers

# Create your views here.


def get_data():
    head = mysqlHeader(acc="stock", pw="stock2020", db="stock", host="115.159.1.221")
    event = mysqlBase(head)
    # result = event.select_values('wti_future', 'date_time,price,prev_price')
    sql = "select date_time,price,prev_price from wti_future order by date_time DESC limit 1"
    result = event.engine.execute(sql).fetchall()
    # data = serializers.serialize('json', result)
    t = result[0][0].strftime("%Y-%m-%d %H:%M:%S")
    dict_result = {}
    dict_result['date_time'] = t
    dict_result['price'] = result[0][1]
    dict_result['prev_price'] = result[0][2]
    print(JsonResponse(dict_result))


def device_type(request):
    agent = request.META['HTTP_USER_AGENT'].lower()
    mobile = ['iphone', 'android', 'symbianos', 'windows phone']

    if any([agent.find(name) + 1 for name in mobile]):
        return 'mobile'
    else:
        return 'pc'


def index(request):
    # return HttpResponse("Hallo wert!")
    # return HttpResponse(dict_result)
    device = device_type(request)
    context = {'stock_data': stock_data, 'device_type': device}
    return render(request, 'index.html', context)


if __name__ == '__main__':
    get_data()
