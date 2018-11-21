from django.contrib import admin

from currency_convert.models import MonthlyAverage


class MonthlyAverageAdmin(admin.ModelAdmin):
    search_fields = ['currency__code', 'year']
    list_display = [
        'currency',
        'year',
        'month',
        'value']
    ordering = ['currency', 'year', 'month']


admin.site.register(MonthlyAverage, MonthlyAverageAdmin)
