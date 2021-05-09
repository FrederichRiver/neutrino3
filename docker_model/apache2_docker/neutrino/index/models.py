from django.db import models

# Create your models here.

class StockData(models.Model):
    trade_date = models.DateField()
    close_price = models.FloatField()
