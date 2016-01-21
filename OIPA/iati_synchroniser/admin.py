from django.conf.urls import url
from django.contrib import admin
from models import *
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from iati_synchroniser.parse_admin import ParseAdmin

from django.core.urlresolvers import reverse

class CodeListAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'count', 'fields', 'date_updated']

    def get_urls(self):
        urls = super(CodeListAdmin, self).get_urls()
        extra_urls = [
            url(r'^sync-codelists/$', self.admin_site.admin_view(self.sync_view))
        ]
        return extra_urls + urls

    def sync_view(self, request):
        sync_id = request.GET.get('sync_id')
        from iati_synchroniser.codelist_importer import CodeListImporter
        cli = CodeListImporter()
        cli.synchronise_with_codelists()
        return HttpResponse('Success')

import requests
import datetime
from api.export.views import IATIActivityList
from django.http import request, QueryDict
from django.test.client import RequestFactory
from lxml import etree
from lxml.builder import E

# TODO: Make this a celery task - 2016-01-21
def export_xml_by_source(request, source):
    """Call export API with this xml_source_ref, combine paginated responses"""

    if not source:
        return None

    base_url = request.build_absolute_uri(reverse('export:activity-export')) + "?xml_source_ref={source}&format=xml&page_size=100&page={page}".format(source=source, page="{page}")

    def get_result(xml, page_num):
        print('making request, page: ' + str(page_num))
        rf = RequestFactory()
        req = rf.get(base_url.format(page=page_num))

        view = IATIActivityList.as_view()(req).render()
        xml.extend(etree.fromstring(view.content).getchildren())
        
        link_header = view.get('link')

        if not link_header:
            return xml

        link = requests.utils.parse_header_links(link_header)
        has_next = reduce(lambda acc, x: acc or (x['rel'] == 'next'), link, False)

        if has_next:
            return get_result(xml, page_num+1)
        else:
            return xml

    xml = E('iati-activities', version="2.01")

    final_xml = get_result(xml, 1)
    final_xml.attrib['generated-datetime'] = datetime.datetime.now().isoformat()
    
    return etree.tostring(final_xml)
    

class IATIXMLSourceAdmin(admin.ModelAdmin):
    search_fields = ['ref', 'title', 'publisher__org_name']
    list_display = [
        'ref', 
        'publisher', 
        'title', 
        'show_source_url',  
        'date_created', 
        'export_btn',  
        'get_parse_status', 
        'get_parse_activity', 
        'date_updated', 
        'last_found_in_registry', 
        'is_parsed']

    def show_source_url(self, obj):
        return format_html('<a href="{url}">{url}</a>', url=obj.source_url)
    show_source_url.allow_tags = True
    show_source_url.short_description = "Source URL"

    def export_btn(self, obj):
        return format_html('<a class="parse-btn" href="{url}" target="_blank">Export</a>',
            url='export-xml/' + obj.ref)
            # url=reverse('export-xml', kwargs={'xml_source_ref': obj.ref}))
        # return mark_safe('<button export=""></button')
    export_btn.short_description = 'Export XML'
    export_btn.allow_tags = True


    def get_urls(self):
        urls = super(IATIXMLSourceAdmin, self).get_urls()
        extra_urls = [
            url(
                r'^parse-xml/$', 
                self.admin_site.admin_view(self.parse_view)),
            url(
                r'^parse-xml/(?P<activity_id>[^@$&+,/:;=?]+)$', 
                self.admin_site.admin_view(self.parse_activity_view)),
            url(
                r'^parse-sources/$',
                self.admin_site.admin_view(self.parse_sources)),
            url(
                r'^export-xml/(?P<xml_source_ref>[^@$&+,/:;=?]+)$', 
                self.admin_site.admin_view(self.export_xml),
                name='export-xml'),
        ]
        return extra_urls + urls

    def parse_view(self, request):
        xml_id = request.GET.get('xml_id')
        obj = get_object_or_404(IatiXmlSource, id=xml_id)
        obj.process()
        return HttpResponse('Success')

    def parse_activity_view(self, request, activity_id):
        xml_id = request.GET.get('xml_id')

        obj = get_object_or_404(IatiXmlSource, id=xml_id)
        obj.process_activity(activity_id)
        return HttpResponse('Success')

    def parse_sources(self, request):
        from iati_synchroniser.dataset_syncer import DatasetSyncer
        syncer = DatasetSyncer()
        syncer.synchronize_with_iati_api()
        return HttpResponse('Success')

    def export_xml(self, request, xml_source_ref):
        xml_response = export_xml_by_source(request, xml_source_ref)

        return HttpResponse(xml_response, content_type='application/xml')
        
class IATIXMLSourceInline(admin.TabularInline):
    model = IatiXmlSource
    extra = 0


class PublisherAdmin(admin.ModelAdmin):
    inlines = [IATIXMLSourceInline]

    list_display = (
        'org_id', 
        'org_abbreviate', 
        'org_name')

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.js',
            '/static/js/publisher_admin.js',
            )

    def get_urls(self):
        urls = super(PublisherAdmin, self).get_urls()
        extra_urls = [
            url(
                r'^parse-publisher/$', 
                self.admin_site.admin_view(self.parse_view)),
        ]
        return extra_urls + urls


    def parse_view(self, request):
        publisher_id = request.GET.get('publisher_id')
        for obj in IatiXmlSource.objects.filter(publisher__id=publisher_id):
            obj.process()
        return HttpResponse('Success')


admin.site.register(Codelist,CodeListAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(IatiXmlSource, IATIXMLSourceAdmin)
