from django.conf.urls import patterns
from django.contrib import admin
from models import *
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from iati_synchroniser.parse_admin import ParseAdmin


class CodeListAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'count', 'fields', 'date_updated']

    def get_urls(self):
        urls = super(CodeListAdmin, self).get_urls()
        extra_urls = patterns('',
            (r'^sync-codelists/$', self.admin_site.admin_view(self.sync_view))
        )
        return extra_urls + urls

    def sync_view(self, request):
        sync_id = request.GET.get('sync_id')
        from iati_synchroniser.codelist_importer import CodeListImporter
        cli = CodeListImporter()
        cli.synchronise_with_codelists()
        return HttpResponse('Success')


class IATIXMLSourceInline(admin.TabularInline):
    model = IatiXmlSource
    extra = 0


class IATIXMLSourceAdmin(admin.ModelAdmin):
    search_fields = ['ref', 'title']
    list_display = ['ref', 'publisher', 'title', 'date_created', 'update_interval', 'get_parse_status', 'date_updated', 'last_found_in_registry', 'xml_activity_count', 'oipa_activity_count', 'is_parsed']

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
        obj.process()
        return HttpResponse('Success')

    def parse_all(self, request):
        parser = ParseAdmin()
        parser.parseAll()
        return HttpResponse('Success')

    def parse_all_over_interval(self, request):
        parser = ParseAdmin()
        parser.parseSchedule()
        return HttpResponse('Success')

    def parse_all_over_x_days(self, request):
        days = request.GET.get('days')
        parser = ParseAdmin()
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

        pu = ParseAdmin()
        pu.update_publisher_activity_count()
        return HttpResponse('Success')



admin.site.register(Codelist,CodeListAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(IatiXmlSource, IATIXMLSourceAdmin)
