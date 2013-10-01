from django.conf.urls import patterns
from django.contrib import admin
from models import *
from django.http import HttpResponse
from django.shortcuts import get_object_or_404



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
        obj = get_object_or_404(dataset_sync, id=sync_id)
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
        obj = get_object_or_404(codelist_sync)
        obj.sync_codelist()
        return HttpResponse('Success')




class IATIXMLSourceInline(admin.TabularInline):
    model = iati_xml_source
    extra = 0


class IATIXMLSourceAdmin(admin.ModelAdmin):
    list_display = ['ref', 'publisher', 'type', 'date_created', 'get_parse_status', 'date_updated']
    list_filter = ('publisher', 'type')

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.js',
            '/static/js/xml_source_admin.js',
        )

    def get_urls(self):
        urls = super(IATIXMLSourceAdmin, self).get_urls()
        extra_urls = patterns('',
            (r'^parse-xml/$', self.admin_site.admin_view(self.parse_view))
        )
        return extra_urls + urls

    def parse_view(self, request):
        xml_id = request.GET.get('xml_id')
        obj = get_object_or_404(iati_xml_source, id=xml_id)
        obj.process(1)
        return HttpResponse('Success')


class PublisherAdmin(admin.ModelAdmin):
    inlines = [IATIXMLSourceInline]

    list_display = ('org_name', 'org_abbreviate')

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.js',
            '/static/js/publisher_admin.js',
            )

    def get_urls(self):
        urls = super(PublisherAdmin, self).get_urls()
        extra_urls = patterns('',
            (r'^parse-publisher/$', self.admin_site.admin_view(self.parse_view))
        )
        return extra_urls + urls

    def parse_view(self, request):
        publisher_id = request.GET.get('publisher_id')
        for obj in iati_xml_source.objects.filter(publisher__id=publisher_id):
            obj.process(1)
        return HttpResponse('Success')

admin.site.register(dataset_sync,DatasetSyncAdmin)
admin.site.register(codelist_sync,CodeListSyncAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(iati_xml_source, IATIXMLSourceAdmin)