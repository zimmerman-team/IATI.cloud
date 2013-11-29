from django.contrib import admin
from Cache.models import *
from django.conf.urls import patterns
from django.http import HttpResponse
from Cache.validator import Validator

class RequestAdmin(admin.ModelAdmin):
    search_fields = ['call']
    list_display = ['call', 'cached', 'response_time']

    def get_urls(self):
        urls = super(RequestAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-requests/$', self.admin_site.admin_view(self.update_requests))
        )
        return my_urls + urls

    def update_requests(self, request):
        validator = Validator()
        validator.update_response_times_and_add_to_cache()
        return HttpResponse('Success')


class CallAdmin(admin.ModelAdmin):
    search_fields = ['call']
    list_display = ['call', 'last_fetched']

    def get_urls(self):
        urls = super(CallAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-caches/$', self.admin_site.admin_view(self.update_caches))
        )
        return my_urls + urls

    def update_caches(self, request):
        validator = Validator()
        validator.update_cache_calls()
        return HttpResponse('Success')

admin.site.register(cached_call, CallAdmin)
admin.site.register(requested_call, RequestAdmin)

