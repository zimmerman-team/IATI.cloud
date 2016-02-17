import sys
import ujson
import os
import os.path

from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.gis.geos import fromstr

from geodata.models import City
from geodata.models import Country


class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['geoname_id', '__unicode__', 'ascii_name', 'alt_name', 'namepar']

    def get_urls(self):
        urls = super(CityAdmin, self).get_urls()

        my_urls = [
            url(r'^update-cities/$', self.admin_site.admin_view(self.update_cities))
        ]
        return my_urls + urls

    def get_cities_json_data(self):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/../data_backup/cities.json"
        json_data = open(location)
        city_locations = ujson.load(json_data)
        json_data.close()
        return city_locations

    def update_cities(self, request):

        city_locations = self.get_cities_json_data()

        for c in city_locations.get('features'):
            try:
                geoid = int(c['properties']['GEONAMEID'])
                if City.objects.filter(geoname_id=geoid).exists():
                    continue

                name = c['properties']['NAME']
                the_country = None
                latitude = c['properties']['LATITUDE']
                longitude = c['properties']['LONGITUDE']
                ascii_name = c['properties']['NAMEASCII']
                alt_name = c['properties']['NAMEALT']
                country_iso2 = c['properties']['ISO_A2']
                namepar = c['properties']['NAMEPAR']

                point_loc_str = 'POINT(' + str(longitude) + ' ' + str(latitude) + ')'
                longlat = fromstr(point_loc_str, srid=4326)

                if Country.objects.filter(code=country_iso2).exists():
                    the_country = Country.objects.get(code=country_iso2)

                new_city = City(
                    geoname_id=geoid,
                    name=name,
                    country=the_country,
                    location=longlat,
                    ascii_name=ascii_name,
                    alt_name=alt_name,
                    namepar=namepar)

                new_city.save()

                if c['properties']['FEATURECLA'] == "Admin-0 capital":
                    if the_country:
                        the_country.capital_city = new_city
                        the_country.save()

            except AttributeError, e:
                print "error in update_cities ", sys.exc_info()[0]
                print e.message

        return HttpResponse('Success')
