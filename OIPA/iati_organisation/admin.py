import ujson
import os
import os.path

from django.contrib import admin
from django.conf.urls import url
from django.http import HttpResponse

from iati_organisation.models import Organisation


class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['id', ]
    list_display = ('id',)

    def get_urls(self):
        urls = super(OrganisationAdmin, self).get_urls()

        my_urls = [
            url(r'^update-primary-names/$', self.admin_site.admin_view(self.update_primary_names)),
        ]
        return my_urls + urls

    def get_json_data(self, location_from_here):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + location_from_here
        json_data = open(location)
        data = ujson.load(json_data)
        json_data.close()
        return data

    def update_primary_names(self, request):
        org_names = self.get_json_data("/data/organisation_name_mapping.json")

        for o in org_names:
            if Organisation.objects.filter(organisation_identifier=o).exists():
                org = Organisation.objects.get(organisation_identifier=o)
                org.primary_name = org_names[o]
                org.save()

        return HttpResponse('<html><body>Success</body></html>', content_type='text/html')


admin.site.register(Organisation, OrganisationAdmin)
