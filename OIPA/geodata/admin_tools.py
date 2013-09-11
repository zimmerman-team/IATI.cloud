__author__ = 'vincentvantwestende'
from geodata.data_backup.country_data import countryData
from geodata.data_backup.country_location import COUNTRY_LOCATION
from geodata.models import country, city, region
from django.contrib.gis.geos import fromstr
from geodata.data_backup.city_data import CityLocations
from geodata.data_backup.country_regions import country_regions
import sys

class AdminTools():


    def update_polygon_set(self):
        print "update_polygon_set not implemented yet: need postgis"
        for k in countryData['features']:
            try:
                country_iso2 = k['properties']['iso2']
                if country.objects.filter(code=country_iso2).exists():
                        the_country = country.objects.get(code=country_iso2)
                else:
                    continue

                geometry = k['geometry']
                the_country.polygon = geometry

                # pol_string = geojson_to_wkt.dumps(geometry)
                # pol = GEOSGeometry(pol_string)
                # the_country.polygon = pol
                the_country.save()

            except ValueError, e:
                print "valueerror update polygon set" + e.message
            except TypeError, e:
                print "Typeerror update polygon set " + e.message
            except:
                print "error in update_polygon_set", sys.exc_info()[0]


    def update_country_center(self):
         for c in country.objects.all():
            try:

                longitude = str(COUNTRY_LOCATION[c.code]['longitude'])
                latitude = str(COUNTRY_LOCATION[c.code]['latitude'])
                point_loc_str = 'POINT(' + longitude + ' ' + latitude + ')'
                c.center_longlat = fromstr(point_loc_str, srid=4326)
                c.save()
                print "Country %s has been updated" % c.name
            except KeyError:
                print "Country with iso %s not found..." % c.name


    def update_country_regions(self):
        for cr in country_regions:
            try:
                country_iso2 = cr['iso2']
                region_dac_code = cr['dac_region_code']


                if country.objects.filter(code=country_iso2).exists():
                            the_country = country.objects.get(code=country_iso2)
                else:
                    continue

                if region.objects.filter(code=region_dac_code).exists():
                            the_region = region.objects.get(code=region_dac_code)
                else:
                    continue

                if (the_country.region == None):
                    the_country.region = the_region
                    the_country.save()

            except:
                print "error in update_country_regions"



    def update_cities(self):

        cl = CityLocations()
        city_locations = cl.get_city_locations()

        for c in city_locations['features']:
            try:
                geoid = int(c['properties']['geonameid'])
                if city.objects.filter(geoname_id=geoid).exists():
                        continue

                name = c['properties']['name']
                the_country = None
                latitude = c['properties']['latitude']
                longitude = c['properties']['longitude']
                ascii_name = c['properties']['nameascii']
                alt_name = c['properties']['namealt']
                country_iso2 = c['properties']['iso_a2']
                namepar = c['properties']['namepar']

                point_loc_str = 'POINT(' + str(longitude) + ' ' + str(latitude) + ')'
                longlat = fromstr(point_loc_str, srid=4326)

                if country.objects.filter(code=country_iso2).exists():
                    the_country = country.objects.get(code=country_iso2)

                new_city = city(geoname_id=geoid, name=name, country=the_country, location=longlat, ascii_name=ascii_name, alt_name=alt_name, namepar=namepar)
                new_city.save()

                if c['properties']['featurecla'] == "Admin-0 capital":
                    if the_country:
                        the_country.capital_city = new_city
                        the_country.save()

            except AttributeError, e:
                print "error in update_cities ", sys.exc_info()[0]
                print e.message

            except:
                print "error in update_cities"




