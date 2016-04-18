from django.conf.urls import url
from django.contrib import admin
from models import *
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django.core.urlresolvers import reverse
import django_rq
from task_queue.tasks import force_parse_source_by_url


class CodeListAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'count', 'fields', 'date_updated']


import requests
import datetime
from api.export.views import IATIActivityList
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

    from django.core.files.base import File, ContentFile
    from django.conf import settings
    import uuid

    file_name = "{}.xml".format(uuid.uuid4())
    path = "{}/{}".format(settings.MEDIA_ROOT, file_name)

    xml_file = File(open(path, mode='w'))
    xml_file.write(etree.tostring(final_xml, pretty_print=True))
    xml_file.close()

    return file_name
    

class IATIXMLSourceAdmin(admin.ModelAdmin):
    actions = ['really_delete_selected']
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
        return format_html('<a target="_blank" href="{url}">Open file in new window</a>', url=obj.source_url)
    show_source_url.allow_tags = True
    show_source_url.short_description = "Source URL"

    def export_btn(self, obj):
        return format_html(
            '<a data-ref="{ref}" class="admin-btn export-btn" target="_blank">Export</a>',
            url='export-xml/' + obj.ref,
            ref=obj.ref)
    export_btn.short_description = 'Export XML'
    export_btn.allow_tags = True

    def get_urls(self):
        urls = super(IATIXMLSourceAdmin, self).get_urls()
        extra_urls = [
            url(
                r'^parse-source/$',
                self.admin_site.admin_view(self.parse_source)),
            url(
                r'^add-to-parse-queue/$',
                self.admin_site.admin_view(self.add_to_parse_queue)),
            url(
                r'^parse-xml/(?P<activity_id>[^@$&+,/:;=?]+)$', 
                self.admin_site.admin_view(self.parse_activity_view)),
            url(
                r'^export-xml/(?P<xml_source_ref>[^@$&+,/:;=?]+)$', 
                self.admin_site.admin_view(self.export_xml),
                name='export-xml'),
        ]
        return extra_urls + urls

    def parse_source(self, request):
        xml_id = request.GET.get('xml_id')
        obj = get_object_or_404(IatiXmlSource, id=xml_id)
        obj.process(force_reparse=True)
        return HttpResponse('Success')

    def add_to_parse_queue(self, request):
        xml_id = request.GET.get('xml_id')
        obj = get_object_or_404(IatiXmlSource, id=xml_id)
        queue = django_rq.get_queue("parser")
        queue.enqueue(force_parse_source_by_url, args=(obj.source_url,), timeout=7200)
        return HttpResponse('Success')

    def parse_activity_view(self, request, activity_id):
        xml_id = request.GET.get('xml_id')

        obj = get_object_or_404(IatiXmlSource, id=xml_id)
        obj.process_activity(activity_id)
        return HttpResponse('Success')

    def export_xml(self, request, xml_source_ref):
        xml_response = export_xml_by_source(request, xml_source_ref)
        return HttpResponse(xml_response, content_type='application/xml')

    def get_actions(self, request):
        actions = super(IATIXMLSourceAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        if queryset.count() == 1:
            message_bit = "1 IATI data source was"
        else:
            message_bit = "%s IATI data sources were" % queryset.count()
        self.message_user(request, "%s successfully deleted." % message_bit)
    really_delete_selected.short_description = "Delete selected IATI data sources"


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
