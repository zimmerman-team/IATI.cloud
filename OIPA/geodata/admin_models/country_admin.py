import ujson
import os
import os.path

from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.gis.geos import fromstr

from geodata.models import Country
from geodata.models import Region


class CountryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = [
        '__unicode__',
        'alt_name',
        'capital_city',
        'region',
        'un_region',
        'unesco_region',
        'dac_country_code',
        'iso3',
        'alpha3',
        'fips10',
        'data_source']

    def get_urls(self):
        urls = super(CountryAdmin, self).get_urls()

        my_urls = [
            url(r'^update-polygon/$', self.admin_site.admin_view(self.update_polygon)),
            url(r'^update-country-center/$', self.admin_site.admin_view(self.update_country_center)),
            url(r'^update-regions/$', self.admin_site.admin_view(self.update_regions)),
            url(r'^update-country-identifiers/$', self.admin_site.admin_view(self.update_country_identifiers)),
            url(r'^update-alt-names/$', self.admin_site.admin_view(self.update_alt_names))
        ]
        return my_urls + urls

    def get_json_data(self, location_from_here):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + location_from_here
        json_data = open(location)
        data = ujson.load(json_data)
        json_data.close()
        return data

    def update_polygon(self, request):
        admin_countries = self.get_json_data("/../data_backup/country_data.json")

        for k in admin_countries.get('features'):
            country_iso2 = k.get('properties').get('iso2')
            if not country_iso2:
                continue
            the_country = Country.objects.get(code=country_iso2)
            the_country.polygon = ujson.dumps(k.get('geometry'))
            the_country.save()

        return HttpResponse('Success')

    def update_country_center(self, request):
        country_centers = self.get_json_data("/../data_backup/country_center.json")

        for c in country_centers:
            if Country.objects.filter(code=c).exists():
                current_country = Country.objects.get(code=c)

                point_loc_str = ''.join([
                    'POINT(',
                    str(country_centers[c]["longitude"]),
                    ' ',
                    str(country_centers[c]["latitude"]),
                    ')'])
                longlat = fromstr(point_loc_str, srid=4326)
                current_country.center_longlat = longlat
                current_country.save()

        return HttpResponse('Success')

    def update_regions(self, request):
        country_regions = self.get_json_data("/../data_backup/country_regions.json")

        for cr in country_regions:
            country_iso2 = cr['iso2']
            region_dac_code = cr['dac_region_code']

            if Country.objects.filter(code=country_iso2).exists():
                the_country = Country.objects.get(code=country_iso2)

            if Region.objects.filter(code=region_dac_code).exists():
                the_region = Region.objects.get(code=region_dac_code)

            if the_country.region is None and the_country is not None and the_region is not None:
                the_country.region = the_region
                the_country.save()

        return HttpResponse('Success')

    def update_country_identifiers(self, request):
        un_numerical_country_codes = self.get_json_data("/../data_backup/un_numerical_country_codes.json")

        for c in un_numerical_country_codes.get('codemappings').get('territorycodes'):
            iso2 = c.get('type')

            if Country.objects.filter(code=iso2).exists():
                the_country = Country.objects.get(code=iso2)

                the_country.numerical_code_un = c.get('numeric')
                the_country.alpha3 = c.get('alpha3')
                the_country.iso3 = c.get('alpha3')
                the_country.fips10 = c.get('fips10')

                the_country.save()

        return HttpResponse('Success')

    def update_alt_names(self, request):
        alt_names = self.get_json_data("/../data_backup/urbnnrs_alt_country_name.json")

        for c in alt_names:
            if Country.objects.filter(code=c).exists():
                current_country = Country.objects.get(code=c)
                current_country.alt_name = alt_names.get(c).get('alt_name')
                current_country.save()

        return HttpResponse('Success')

