from django.contrib import admin
from currency_converter.models import *
from django.conf.urls import patterns
from django.http import HttpResponse

class ConverterAdmin(admin.ModelAdmin):
    list_display = ['date_updated']

    def get_urls(self):
        urls = super(ConverterAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^convert-all/$', self.admin_site.admin_view(self.convert_all)),
        )
        return my_urls + urls

    @staticmethod
    def convert_all():
        converter = CurrencyConverter()
        converter.convert_all()
        return HttpResponse('Success')

admin.site.register(Converter, ConverterAdmin)

