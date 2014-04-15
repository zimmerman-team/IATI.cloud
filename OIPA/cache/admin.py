from django.contrib import admin
from cache.models import *
from django.conf.urls import patterns
from django.http import HttpResponse
from cache.validator import Validator

class RequestAdmin(admin.ModelAdmin):
    search_fields = ['call']
    list_display = ['call', 'cached', 'response_time', 'last_requested', 'count']

    def get_urls(self):
        urls = super(RequestAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-requests/$', self.admin_site.admin_view(self.update_requests)),
            (r'^cache-all-requests/$', self.admin_site.admin_view(self.cache_all_requests)),
            (r'^delete-all-under-x-count/$', self.admin_site.admin_view(self.delete_all_under_x))
        )
        return my_urls + urls

    def update_requests(self, request):
        validator = Validator()
        validator.update_response_times_and_add_to_cache()
        return HttpResponse('Success')

    def cache_all_requests(self, request):
        validator = Validator()
        validator.cache_all_requests()
        return HttpResponse('Success')

    def delete_all_under_x(self, request):
        count = request.GET.get('count')
        validator = Validator()
        validator.delete_all_under_x(count)
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

admin.site.register(CachedCall, CallAdmin)
admin.site.register(RequestedCall, RequestAdmin)

