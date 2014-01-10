from os.path import isfile, getsize
import json
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.conf.urls import url, patterns
from django.http import HttpResponse, Http404
from logviewer.models import Log
from logviewer import app_settings

from django.template.response import TemplateResponse

class HttpUnauthorized(HttpResponse):
    status_code = 401


class LogAdmin(admin.ModelAdmin):

    class Media:
        js = (
            'admin/js/jquery.min.js', 'admin/js/jquery.init.js',
            'logtail/js/logtail.js',
        )
        css = {
            'all': ('logtail/css/logtail.css',)
        }

    def has_add_permission(self, request):
        return False

    def log_view(self, request, logfile='', seek_to='0'):
        context = self.log_context(logfile, seek_to)
        return HttpResponse(
            self.iter_json(context),
            content_type='application/json'
        )

    def log_context(self, logfile, seek_to):
        context = {}
        seek_to = int(seek_to)
        try:
            log_file = app_settings.LOGTAIL_FILES[logfile]
        except KeyError:
            raise Http404('No such log file')

        try:
            file_length = getsize(log_file)
        except OSError:
            raise Http404('Cannot access file')

        if seek_to > file_length:
            seek_to = file_length

        try:
            context['log'] = file(log_file, 'r')
            context['log'].seek(seek_to)
            context['starts'] = seek_to
        except IOError:
            raise Http404('Cannot access file')

        return context

    def iter_json(self, context):
        yield '{"starts": "%d",' \
               '"data": "' % context['starts']

        while True:
            line = context['log'].readline()
            if line:
                yield json.dumps(line).strip(u'"')
            else:
                yield '", "ends": "%d"}' % context['log'].tell()
                context['log'].close()
                return

    def changelist_view(self, request, extra_context=None):
        context = dict(
            title='Logtail',
            app_label=self.model._meta.app_label,
            cl=None,
            media=self.media,
            has_add_permission=self.has_add_permission(request),
            update_interval=app_settings.LOGTAIL_UPDATE_INTERVAL,
            logfiles=((l, f) for l, f
                in app_settings.LOGTAIL_FILES.iteritems()
                if isfile(f)
            ),
        )

        return TemplateResponse(
            request,
            'logtail/logtail_list.html',
            context,
        )

    def get_urls(self):
        urls = super(LogAdmin, self).get_urls()
        urls.insert(0,
            url(
                r'^(?P<logfile>[-\w\.]+)/(?P<seek_to>\d+)/$',
                self.admin_site.admin_view(self.log_view),
            ),
        )
        return urls

admin.site.register(Log, LogAdmin)
