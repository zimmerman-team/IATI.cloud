import ujson
import os
import os.path

from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.gis.geos import fromstr

from geodata.models import Country
from geodata.models import Region
from iati_vocabulary.models import RegionVocabulary


class RegionAdmin(admin.ModelAdmin):

    search_fields = ['name']
    list_display = [
        '__unicode__',
        'code',
        'parental_region'
    ]

    def get_urls(self):
        urls = super(RegionAdmin, self).get_urls()

        my_urls = [
            url(r'^update-region-center/$', self.admin_site.admin_view(self.update_region_center))
        ]
        return my_urls + urls

    def update_region_center(self, request):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/../data_backup/region_center_locations.json"

        json_data = open(location)
        region_centers = ujson.load(json_data)
        for r in region_centers:
            if Region.objects.filter(code=r).exists():
                current_region = Region.objects.get(code=r)

                point_loc_str = ''.join([
                    'POINT(',
                    str(region_centers[r]["longitude"]),
                    ' ',
                    str(region_centers[r]["latitude"]),
                    ')'])

                longlat = fromstr(point_loc_str, srid=4326)
                current_region.center_longlat = longlat
                current_region.save()

        json_data.close()
        return HttpResponse('Success')


