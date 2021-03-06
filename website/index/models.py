from django.db import models


class china_treasury_yield(models.Model):
    report_date = models.DateField(primary_key=True)
    two_year = models.FloatField(blank=True, null=True)
    five_year = models.FloatField(blank=True, null=True)
    ten_year = models.FloatField(blank=True, null=True)
    three_decade = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'china_treasury_yield'


class us_treasury_yield(models.Model):
    report_date = models.DateField(primary_key=True)
    two_year = models.FloatField(blank=True, null=True)
    five_year = models.FloatField(blank=True, null=True)
    ten_year = models.FloatField(blank=True, null=True)
    three_decade = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'us_treasury_yield'
