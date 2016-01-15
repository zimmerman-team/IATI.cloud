from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse

from geodata.models import Adm1Region
from django.contrib.gis.geos import fromstr
from geodata.models import Country
import ujson
import os
import os.path


class Adm1RegionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['__unicode__', 'adm1_code', 'country', 'type', 'admin']

    def get_urls(self):
        urls = super(Adm1RegionAdmin, self).get_urls()

        my_urls = [
            url(r'^update-adm1-regions/$', self.admin_site.admin_view(self.update_adm1_regions))
        ]
        return my_urls + urls

    def get_json_data(self, location_from_here):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + location_from_here
        json_data = open(location)
        data = ujson.load(json_data)
        json_data.close()
        return data

    def update_adm1_regions(self, request):
        adm1_regions = self.get_json_data("/../data_backup/admin_1_regions.json")

        for r in adm1_regions['features']:

            the_adm1_region = Adm1Region()

            p = r["properties"]

            field_list = [
                'adm1_code',
                'OBJECTID_1',
                'diss_me',
                'adm1_cod_1',
                'wikipedia',
                'adm0_sr',
                'name',
                'name_alt',
                'name_local',
                'type',
                'type_en',
                'code_local',
                'code_hasc',
                'note',
                'hasc_maybe',
                'region',
                'region_cod',
                'provnum_ne',
                'gadm_level',
                'check_me',
                'scalerank',
                'datarank',
                'abbrev',
                'postal',
                'area_sqkm',
                'sameascity',
                'labelrank',
                'featurecla',
                'name_len',
                'mapcolor9',
                'mapcolor13',
                'fips',
                'fips_alt',
                'woe_id',
                'woe_label',
                'woe_name',
                'sov_a3',
                'adm0_a3',
                'adm0_label',
                'admin',
                'geonunit',
                'gu_a3',
                'gn_id',
                'gn_name',
                'gns_id',
                'gns_name',
                'gn_level',
                'gn_region',
                'gn_a1_code',
                'region_sub',
                'sub_code',
                'gns_level',
                'gns_lang',
                'gns_adm1',
                'gns_region',]

            for field in field_list:
                if p.get(field):
                    setattr(the_adm1_region, field, p.get(field))

            if p.get('iso_a2'):
                if Country.objects.filter(code=p.get('iso_a2')).exists():
                    the_country = Country.objects.get(code=p.get('iso_a2'))
                    the_adm1_region.country = the_country
                elif p.get('admin') and p.get('admin') == "Kosovo":
                    the_country = Country.objects.get(code="XK")
                    the_adm1_region.country = the_country

            if p.get('longitude') and p.get('latitude'):
                try:
                    longitude = str(p.get('longitude'))
                    latitude = str(p.get('latitude'))
                    point_loc_str = 'POINT(' + longitude + ' ' + latitude + ')'
                    the_adm1_region.center_location = fromstr(point_loc_str, srid=4326)
                except KeyError:
                    print "Admin 1 region with code %s has an illegal center location..." % the_adm1_region.adm1_code

            the_adm1_region.polygon = r["geometry"].get('coordinates')
            the_adm1_region.geometry_type = r["geometry"].get('type')

            the_adm1_region.save()

        return HttpResponse('Success')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.exclude = ('polygon', 'center_location', )
        return super(Adm1RegionAdmin, self).change_view(request, object_id, form_url, extra_context)

