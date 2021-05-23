from django.shortcuts import render
from django.http import HttpResponse
from index.models import china_treasury_yield, us_treasury_yield
from django.forms.models import model_to_dict

# Create your views here.

def device_type(request):
    agent = request.headers['User-Agent']
    mobile = ['iphone', 'android', 'symbianos', 'windows phone']
    if any([agent.find(name) + 1 for name in mobile]):
        return 'mobile'
    else:
        return 'pc'

def index(request):
    device = device_type(request)
    context = {'device_type': device}
    return render(request, "index.html", context)

def macro(request):
    device = device_type(request)
    data = china_treasury_yield.objects.using('stock').all()
    length = data.count()
    r = data[length-1:length].get()
    # r = china_treasury_yield.objects.using('stock').get(report_date='2021-03-19')
    data = us_treasury_yield.objects.using('stock').all()
    length = data.count()
    r2 = data[length-1:length].get()
    context = {"device_type": device,"update_date1": r.report_date, "ten_year1": r.ten_year, "update_date2":r2.report_date, "ten_year2": r2.ten_year}
    return render(request, "macro.html", context)
    # return HttpResponse(f"{result}")
