#!/usr/bin/python3
from django.urls import path
from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('macro', views.macro, name='macro'),
        ]
