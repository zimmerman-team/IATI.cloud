import sys
from django.contrib.gis.geos import fromstr

from geodata.importer.common import get_json_data
from geodata.models import City
from geodata.models import Country


class CityImport():
    """
    Wrapper class for all import methods used on the City model
    """
    def __init__(self):
        self.get_json_data = get_json_data

    def update_cities(self):

        city_locations = self.get_json_data("/../data_backup/cities.json")

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