from geodata.models import Country, Region, City, Adm1Region
import ujson
import os
import os.path
from django.contrib.gis.geos import fromstr
import sys
import xml.etree.cElementTree as etree


class CountryUpdater():

        def update_regions(self):
            base = os.path.dirname(os.path.abspath(__file__))
            location = base + "/data_backup/country_regions.json"
    
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


        def update_center_longlat(self):
            base = os.path.dirname(os.path.abspath(__file__))
            location = base + "/data_backup/country_center.json"

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

        def update_alt_names(self):
            base = os.path.dirname(os.path.abspath(__file__))
            location = base + "/data_backup/urbnnrs_alt_country_name.json"

            json_data = open(location)
            alt_names = ujson.load(json_data)
            for c in alt_names:
                if Country.objects.filter(code=c).exists():
                    current_country = Country.objects.get(code=c)
                    current_country.alt_name = alt_names[c]["alt_name"]
                    current_country.save()

            json_data.close()


        def update_identifiers(self):
            base = os.path.dirname(os.path.abspath(__file__))
            location = base + "/data_backup/un_numerical_country_codes.json"

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


        def update_polygon_set(self):
            base = os.path.dirname(os.path.abspath(__file__))
            location = base + "/data_backup/country_data.json"

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


class RegionUpdater():

    def update_un_regions(self):
        from geodata.models import Country, Region
        import ujson
        import os
        import os.path
        from iati_vocabulary.models import RegionVocabulary

        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/data_backup/un_region_codes.json"

        json_data = open(location)
        un_region_codes = ujson.load(json_data)

        times = 0
        while times < 2:
            times += 1
            for cr in un_region_codes["territorycontainment"]["group"]:
                try:
                    type = cr['type']
                    contains = cr['contains']
                    region_un_name = cr['name']

                    the_region = None

                    if Region.objects.filter(code=type).exists():
                        the_region = Region.objects.get(code=type)
                        the_region.name = region_un_name
                    else:
                        the_region_voc = RegionVocabulary.objects.get(code=2)
                        the_region = Region(code=type, name=region_un_name, region_vocabulary=the_region_voc, parental_region=None)

                    the_region.save()

                    countries_or_regions = contains.split(" ")
                    try:
                        int(countries_or_regions[0])

                        for cur_region in countries_or_regions:
                            if Region.objects.filter(code=cur_region).exists():
                                cur_region_obj = Region.objects.get(code=cur_region)
                                cur_region_obj.parental_region = the_region
                                cur_region_obj.save()

                    except:
                        for cur_country in countries_or_regions:
                            if Country.objects.filter(code=cur_country).exists():
                                the_country = Country.objects.get(code=cur_country)
                                the_country.un_region = the_region
                                the_country.save()

                except Exception as e:
                    print "error in update_country_regions" + str(type)
                    print e.args
        json_data.close()

    def update_unesco_regions(self):
        """
        This code will create/update unesco regions and update the country -> region mapping
        """
        import os
        import ujson
        from geodata.models import Region
        from iati_vocabulary.models import RegionVocabulary

        base = os.path.dirname(os.path.abspath(__file__))

        location = base + '/data_backup/unesco_regions.json'
        json_data = open(location)
        unesco_regions = ujson.load(json_data)
        json_data.close()

        location_map = base + '/data_backup/unesco_country_region_mapping.json'
        json_data_map = open(location_map)
        unesco_mapping = ujson.load(json_data_map)
        json_data_map.close()

        #save regions and put in list
        regions = []
        region_vocabulary = RegionVocabulary.objects.get_or_create(
            code=999,
            name='UNESCO')[0]

        for region_id, info in unesco_regions.iteritems():

            center_location_string = 'POINT(' + info['longitude'] + ' ' + info['latitude'] + ')'
            center_location = fromstr(
                center_location_string,
                srid=4326)
            region = Region.objects.get_or_create(
                code=region_id,
                defaults={
                    'name': info['name'],
                    'region_vocabulary': region_vocabulary,
                    'parental_region': None,
                    'center_longlat': center_location})[0]
            regions.append(region)

        # save country -> region mapping
        for line in unesco_mapping:

            region_id = line["UNESCO Region Code"]
            country_id = line["Country ID"]
            country = Country.objects.get(code=country_id)
            for region in regions:
                if region.code == region_id:
                    country.unesco_region = region
                    country.save()

    def update_center_longlat(self):
            base = os.path.dirname(os.path.abspath(__file__))
            location = base + "/data_backup/region_center_locations.json"

            json_data = open(location)
            region_centers = ujson.load(json_data)
            for r in region_centers:
                if Region.objects.filter(code=r).exists():
                    current_region = Region.objects.get(code=r)

                    point_loc_str = 'POINT(' + str(region_centers[r]["longitude"]) + ' ' + str(region_centers[r]["latitude"]) + ')'
                    longlat = fromstr(point_loc_str, srid=4326)
                    current_region.center_longlat = longlat
                    current_region.save()

            json_data.close()


class CityUpdater():

    def update_cities(self):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/data_backup/cities.json"

        json_data = open(location)
        city_locations = ujson.load(json_data)

        for c in city_locations['features']:
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

                new_city = City(geoname_id=geoid, name=name, country=the_country, location=longlat, ascii_name=ascii_name, alt_name=alt_name, namepar=namepar)
                new_city.save()

                if c['properties']['FEATURECLA'] == "Admin-0 capital":
                    if the_country:
                        the_country.capital_city = new_city
                        the_country.save()

            except AttributeError, e:
                print "error in update_cities ", sys.exc_info()[0]
                print e.message

            except Exception as e:
                print "error in update_cities"

        json_data.close()





class Admin1RegionUpdater():

    def update_all(self):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/data_backup/admin_1_regions.json"

        json_data = open(location)
        adm1_regions = ujson.load(json_data)

        for r in adm1_regions['features']:

            the_adm1_region = Adm1Region()
            the_adm1_region.adm1_code = r["properties"]["adm1_code"]

            p = r["properties"]

            if "OBJECTID_1" in p:
                the_adm1_region.OBJECTID_1 = p["OBJECTID_1"]
            if "diss_me" in p:
                the_adm1_region.diss_me = p["diss_me"]
            if "adm1_cod_1" in p:
                the_adm1_region.adm1_cod_1 = p["adm1_cod_1"]
            if "iso_3166_2" in p:
                the_adm1_region.iso_3166_2 = str(p["iso_3166_2"])[:2]
            if "wikipedia" in p:
                the_adm1_region.wikipedia = p["wikipedia"]
            if "iso_a2" in p:
                if Country.objects.filter(code=p["iso_a2"]).exists():
                    the_country = Country.objects.get(code=p["iso_a2"])
                    the_adm1_region.country = the_country
                else:
                    if "admin" in p:
                        if p["admin"] == "Kosovo":
                            if Country.objects.filter(code="XK").exists():
                                the_country = Country.objects.get(code="XK")
                                the_adm1_region.country = the_country
            if "adm0_sr" in p:
                the_adm1_region.adm0_sr = p["adm0_sr"]
            if "name" in p:
                the_adm1_region.name = p["name"]
            if "name_alt" in p:
                the_adm1_region.name_alt = p["name_alt"]
            if "name_local" in p:
                the_adm1_region.name_local = p["name_local"]
            if "type" in p:
                the_adm1_region.type = p["type"]
            if "type_en" in p:
                the_adm1_region.type_en = p["type_en"]
            if "code_local" in p:
                the_adm1_region.code_local = p["code_local"]
            if "code_hasc" in p:
                the_adm1_region.code_hasc = p["code_hasc"]
            if "note" in p:
                the_adm1_region.note = p["note"]
            if "hasc_maybe" in p:
                the_adm1_region.hasc_maybe = p["hasc_maybe"]
            if "region" in p:
                the_adm1_region.region = p["region"]
            if "region_cod" in p:
                the_adm1_region.region_cod = p["region_cod"]
            if "provnum_ne" in p:
                the_adm1_region.provnum_ne = p["provnum_ne"]
            if "gadm_level" in p:
                the_adm1_region.gadm_level = p["gadm_level"]
            if "check_me" in p:
                the_adm1_region.check_me = p["check_me"]
            if "scalerank" in p:
                the_adm1_region.scalerank = p["scalerank"]
            if "datarank" in p:
                the_adm1_region.datarank = p["datarank"]
            if "abbrev" in p:
                the_adm1_region.abbrev = p["abbrev"]
            if "postal" in p:
                the_adm1_region.postal = p["postal"]
            if "area_sqkm" in p:
                the_adm1_region.area_sqkm = p["area_sqkm"]
            if "sameascity" in p:
                the_adm1_region.sameascity = p["sameascity"]
            if "labelrank" in p:
                the_adm1_region.labelrank = p["labelrank"]
            if "featurecla" in p:
                the_adm1_region.featurecla = p["featurecla"]
            if "name_len" in p:
                the_adm1_region.name_len = p["name_len"]
            if "mapcolor9" in p:
                the_adm1_region.mapcolor9 = p["mapcolor9"]
            if "mapcolor13" in p:
                the_adm1_region.mapcolor13 = p["mapcolor13"]
            if "fips" in p:
                the_adm1_region.fips = p["fips"]
            if "fips_alt" in p:
                the_adm1_region.fips_alt = p["fips_alt"]
            if "woe_id" in p:
                the_adm1_region.woe_id = p["woe_id"]
            if "woe_label" in p:
                the_adm1_region.woe_label = p["woe_label"]
            if "woe_name" in p:
                the_adm1_region.woe_name = p["woe_name"]
            if "longitude" in p and "latitude" in p:
                try:
                    longitude = str(p["longitude"])
                    latitude = str(p["latitude"])
                    point_loc_str = 'POINT(' + longitude + ' ' + latitude + ')'
                    the_adm1_region.center_location = fromstr(point_loc_str, srid=4326)
                except KeyError:
                    print "Admin 1 region with code %s has an illegal center location..." % the_adm1_region.adm1_code
            if "sov_a3" in p:
                the_adm1_region.sov_a3 = p["sov_a3"]
            if "adm0_a3" in p:
                the_adm1_region.adm0_a3 = p["adm0_a3"]
            if "adm0_label" in p:
                the_adm1_region.adm0_label = p["adm0_label"]
            if "admin" in p:
                the_adm1_region.admin = p["admin"]
            if "geonunit" in p:
                the_adm1_region.geonunit = p["geonunit"]
            if "gu_a3" in p:
                the_adm1_region.gu_a3 = p["gu_a3"]
            if "gn_id" in p:
                the_adm1_region.gn_id = p["gn_id"]
            if "gn_name" in p:
                the_adm1_region.gn_name = p["gn_name"]
            if "gns_id" in p:
                the_adm1_region.gns_id = p["gns_id"]
            if "gns_name" in p:
                the_adm1_region.gns_name = p["gns_name"]
            if "gn_level" in p:
                the_adm1_region.gn_level = p["gn_level"]
            if "gn_region" in p:
                the_adm1_region.gn_region = p["gn_region"]
            if "gn_a1_code" in p:
                the_adm1_region.gn_a1_code = p["gn_a1_code"]
            if "region_sub" in p:
                the_adm1_region.region_sub = p["region_sub"]
            if "sub_code" in p:
                the_adm1_region.sub_code = p["sub_code"]
            if "gns_level" in p:
                the_adm1_region.gns_level = p["gns_level"]
            if "gns_lang" in p:
                the_adm1_region.gns_lang = p["gns_lang"]
            if "gns_adm1" in p:
                the_adm1_region.gns_adm1 = p["gns_adm1"]
            if "gns_region" in p:
                the_adm1_region.gns_region = p["gns_region"]

            if "coordinates" in r["geometry"]:
                the_adm1_region.polygon = r["geometry"]["coordinates"]
            if "type" in r["geometry"]:
                the_adm1_region.geometry_type = r["geometry"]["type"]

            the_adm1_region.save()

        json_data.close()
