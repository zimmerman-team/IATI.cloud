import sys
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

    def update_polygon(self, request):

        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/../data_backup/country_data.json"

        json_data = open(location)
        admin_countries = ujson.load(json_data)

        for k in admin_countries['features']:
            try:
                country_iso2 = k['properties']['iso2']
                if Country.objects.filter(code=country_iso2).exists():
                        the_country = Country.objects.get(code=country_iso2)
                else:
                    continue

                geometry = k['geometry']
                geometry = ujson.dumps(geometry)
                the_country.polygon = geometry

                the_country.save()

            except ValueError, e:
                print "Value error update_polygon_set" + e.message
            except TypeError, e:
                print "Type error update_polygon_set" + e.message
            except Exception as e:
                print "Error in update_polygon_set", sys.exc_info()
        return HttpResponse('Success')

    def update_country_center(self, request):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/../data_backup/country_center.json"

        json_data = open(location)
        country_centers = ujson.load(json_data)
        for c in country_centers:
            if Country.objects.filter(code=c).exists():
                current_country = Country.objects.get(code=c)

                point_loc_str = 'POINT(' + str(country_centers[c]["longitude"]) + ' ' + str(country_centers[c]["latitude"]) + ')'
                longlat = fromstr(point_loc_str, srid=4326)
                current_country.center_longlat = longlat
                current_country.save()

        json_data.close()
        return HttpResponse('Success')

    def update_regions(self, request):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/../data_backup/country_regions.json"

        json_data = open(location)
        country_regions = ujson.load(json_data)

        for cr in country_regions:
            try:
                country_iso2 = cr['iso2']
                region_dac_code = cr['dac_region_code']

                if Country.objects.filter(code=country_iso2).exists():
                            the_country = Country.objects.get(code=country_iso2)
                else:
                    continue

                if Region.objects.filter(code=region_dac_code).exists():
                            the_region = Region.objects.get(code=region_dac_code)
                else:
                    continue

                if the_country.region == None:
                    the_country.region = the_region
                    the_country.save()

            except:
                print "error in update_country_regions"
        json_data.close()
        return HttpResponse('Success')

    def update_country_identifiers(self, request):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/../data_backup/un_numerical_country_codes.json"

        json_data = open(location)
        un_numerical_country_codes = ujson.load(json_data)

        for c in un_numerical_country_codes['codemappings']['territorycodes']:
            try:
                iso2 = c['type']


                if Country.objects.filter(code=iso2).exists():
                    the_country = Country.objects.get(code=iso2)

                    if 'numeric' in c:
                        the_country.numerical_code_un = c['numeric']
                    if 'alpha3' in c:
                        the_country.alpha3 = c['alpha3']
                        the_country.iso3 = c['alpha3']
                    if 'fips10' in c:
                        the_country.fips10 = c['fips10']

                    the_country.save()

            except Exception as e:
               print e.args

        json_data.close()

        return HttpResponse('Success')

    def update_alt_names(self, request):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/../data_backup/urbnnrs_alt_country_name.json"

        json_data = open(location)
        alt_names = ujson.load(json_data)
        for c in alt_names:
            if Country.objects.filter(code=c).exists():
                current_country = Country.objects.get(code=c)
                current_country.alt_name = alt_names[c]["alt_name"]
                current_country.save()

        json_data.close()
        return HttpResponse('Success')

