from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse

from currency_convert.models import MonthlyAverage
from currency_convert.imf_rate_parser import RateParser


class MonthlyAverageAdmin(admin.ModelAdmin):
    search_fields = ['currency__code', 'year']
    list_display = [
        'currency',
        'month',
        'year',
        'value']
    ordering = ['currency', 'year', 'month']

    def get_urls(self):
        urls = super(MonthlyAverageAdmin, self).get_urls()
        extra_urls = [
            url(
                r'^parse-imf-rates/$',
                self.admin_site.admin_view(self.parse_imf_rates)),
        ]
        return extra_urls + urls

    def parse_imf_rates(self, request):
        r = RateParser()
        r.update_rates(force=False)
        return HttpResponse('Success')


admin.site.register(MonthlyAverage, MonthlyAverageAdmin)