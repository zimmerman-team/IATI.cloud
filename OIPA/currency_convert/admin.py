from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse

from currency_convert.models import MonthlyAverage
from currency_convert.imf_rate_parser import RateParser


class MonthlyAverageAdmin(admin.ModelAdmin):
    search_fields = ['currency__code', 'year']
    list_display = [
        'currency',
        'year',
        'month',
        'value']
    ordering = ['currency', 'year', 'month']

admin.site.register(MonthlyAverage, MonthlyAverageAdmin)