from django.conf.urls import patterns
from django.contrib import admin
from models import *
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from iati_synchroniser.management.commands.parse_all import ParseAll
from iati_synchroniser.management.commands.parse_schedule import ParseSchedule
from iati_synchroniser.management.commands.parse_x_days import ParseXDays
from iati_synchroniser.management.commands.update_publisher_activity_count import PublisherUpdater
from iati_synchroniser.admin import AdminTools

class DatasetSyncAdmin(admin.ModelAdmin):
    list_display = ['type', 'interval', 'date_updated', 'sync_now']

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.js',
            '/static/js/dataset_sync_admin.js',
            )

    def get_urls(self):
        urls = super(DatasetSyncAdmin, self).get_urls()
        extra_urls = patterns('',
            (r'^sync-datasets/$', self.admin_site.admin_view(self.sync_view))
        )
        return extra_urls + urls

    def sync_view(self, request):
        sync_id = request.GET.get('sync_id')
        obj = get_object_or_404(DatasetSync, id=sync_id)
        obj.sync_dataset_with_iati_api()
        return HttpResponse('Success')


class CodeListSyncAdmin(admin.ModelAdmin):
    list_display = ['date_updated', 'sync_now']

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.js',
            '/static/js/codelist_sync_admin.js',
            )

    def get_urls(self):
        urls = super(CodeListSyncAdmin, self).get_urls()
        extra_urls = patterns('',
            (r'^sync-codelists/$', self.admin_site.admin_view(self.sync_view))
        )
        return extra_urls + urls

    def sync_view(self, request):
        sync_id = request.GET.get('sync_id')
        obj = get_object_or_404(CodelistSync, id=sync_id)
        obj.sync_codelist()
        return HttpResponse('Success')

class IATIXMLSourceInline(admin.TabularInline):
    model = IatiXmlSource
    extra = 0


class IATIXMLSourceAdmin(admin.ModelAdmin):
    list_display = ['ref', 'publisher', 'date_created', 'update_interval', 'get_parse_status', 'date_updated', 'last_found_in_registry', 'xml_activity_count', 'oipa_activity_count']
    list_filter = ('publisher', 'type')

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.js',
            '/static/js/xml_source_admin.js',
        )

    def get_urls(self):
        urls = super(IATIXMLSourceAdmin, self).get_urls()
        extra_urls = patterns('',
            (r'^parse-xml/$', self.admin_site.admin_view(self.parse_view)),
            (r'^parse-all/$', self.admin_site.admin_view(self.parse_all)),
            (r'^parse-all-over-interval/$', self.admin_site.admin_view(self.parse_all_over_interval)),
            (r'^parse-all-over-two-days/$', self.admin_site.admin_view(self.parse_all_over_x_days)),
        )
        return extra_urls + urls

    def parse_view(self, request):
        xml_id = request.GET.get('xml_id')
        obj = get_object_or_404(IatiXmlSource, id=xml_id)
        obj.save()
        return HttpResponse('Success')

    def parse_all(self, request):
        parser = ParseAll()
        parser.parseAll()
        return HttpResponse('Success')

    def parse_all_over_interval(self, request):
        parser = ParseSchedule()
        parser.parseSchedule()
        return HttpResponse('Success')

    def parse_all_over_x_days(self, request):
        days = request.GET.get('days')
        parser = ParseXDays()
        parser.parseXDays(days)
        return HttpResponse('Success')


class PublisherAdmin(admin.ModelAdmin):
    inlines = [IATIXMLSourceInline]

    list_display = ('org_id', 'org_abbreviate', 'org_name', 'XML_total_activity_count', 'OIPA_total_activity_count')

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.js',
            '/static/js/publisher_admin.js',
            )

    def get_urls(self):
        urls = super(PublisherAdmin, self).get_urls()
        extra_urls = patterns('',
            (r'^parse-publisher/$', self.admin_site.admin_view(self.parse_view)),
            (r'^count-publisher-activities/', self.admin_site.admin_view(self.count_publisher_activities))
        )
        return extra_urls + urls


    def parse_view(self, request):
        publisher_id = request.GET.get('publisher_id')
        for obj in IatiXmlSource.objects.filter(publisher__id=publisher_id):
            obj.process()
        return HttpResponse('Success')

    def count_publisher_activities(self, request):

        pu = PublisherUpdater()
        pu.update_publisher_activity_count()
        return HttpResponse('Success')


admin.site.register(DatasetSync,DatasetSyncAdmin)
admin.site.register(CodelistSync,CodeListSyncAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(IatiXmlSource, IATIXMLSourceAdmin)