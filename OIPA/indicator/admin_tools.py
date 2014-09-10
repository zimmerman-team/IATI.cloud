
from indicator.models import Indicator, IndicatorData
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from geodata.models import Country, City
import os.path
import ujson

class IndicatorAdminTools():

    def old_to_new_urbnnrs(self):

        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/data_backup/indicator_city_data.json"
        location2 = base + "/data_backup/indicator_city_info.json"
        json_data = open(location)
        indicator_data_set = ujson.load(json_data)
        json_data2 = open(location2)
        city_info_set = ujson.load(json_data2)

        csv_text = "year;year_range;indicator_id;friendly_name;type_data;selection_type;deprivation_type;country;city;region;value;description;category\n"

        for d in indicator_data_set:

            indicator_id = d['indicator_id']
            city_id = d['city_id']
            city_name = "unknown"
            value = d['value']
            year = d['year']

            if value == None or value == "NULL":
                continue

            found_city = None

            for c in city_info_set:
                if (c['id'] == city_id):
                    city_name = c['name']
                    country_id = c['country_id']

                    if indicator_id == 'cpi_4_dimensions':

                        if value and value != "NULL":
                            csv_text = csv_text + year + ";;" + indicator_id + ";4 dimensions;p;;;" + country_id + ";" + city_name + ";;" + value + ";;\n"

        return csv_text












    def update_indicators(self):

        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/data_backup/indicator_names.json"

        json_data = open(location)
        indicator_names = ujson.load(json_data)

        for key, value in indicator_names.items():

            try:
                new_indicator = Indicator(id=key, friendly_label=value["name"], type_data=value["type_data"])
                new_indicator.save()

            except IntegrityError, e:
                print e.message

            except ValueError, e:
                print e.message

            except ValidationError, e:
                print e.message

        json_data.close()

    def update_indicator_data(self):

        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/data_backup/indicator_data.json"

        json_data = open(location)
        indicator_data = ujson.load(json_data)

        for d in indicator_data:
            try:
                indicator_name = d['indicator_name']
                country_iso = d['country_iso']

                value = d['value']
                year = d['year']


                if value == None or value == "NULL":
                    continue

                found_country = None
                if Country.objects.filter(code=country_iso).exists():
                        found_country = Country.objects.get(code=country_iso)
                else:
                    print "indicator not found for " + str(country_iso)
                    continue

                found_indicator = None
                if Indicator.objects.filter(id=indicator_name).exists():
                        found_indicator = Indicator.objects.get(id=indicator_name)
                else:
                    print "indicator not found for " + str(indicator_name)
                    continue

                if IndicatorData.objects.filter(indicator=found_indicator, country=found_country, year=year).exists():
                    continue

                new_indicator_data = IndicatorData(indicator=found_indicator, country=found_country, value=value, year=year, selection_type=None)
                new_indicator_data.save()

            except:
                print "error in update_indicator_data"

        print "ready"
        json_data.close()

    def update_indicator_city_data(self):

         base = os.path.dirname(os.path.abspath(__file__))
         location = base + "/data_backup/indicator_city_data.json"
         location2 = base + "/data_backup/indicator_city_info.json"
         json_data = open(location)
         indicator_data_set = ujson.load(json_data)
         json_data2 = open(location2)
         city_info_set = ujson.load(json_data2)

         for d in indicator_data_set:
            try:
                indicator_id = d['indicator_id']
                city_id = d['city_id']
                city_name = "unknown"
                value = d['value']
                year = d['year']

                if value == None or value == "NULL":
                    continue

                found_city = None

                for c in city_info_set:
                    if (c['id'] == city_id):
                        city_name = c['name']
                        country_id = c['country_id']

                        if City.objects.filter(name=city_name, country_id=country_id).exists():
                            found_city = City.objects.get(name=city_name, country_id=country_id)
                        elif City.objects.filter(ascii_name=city_name, country_id=country_id).exists():
                                found_city = City.objects.get(ascii_name=city_name, country_id=country_id)
                        elif City.objects.filter(alt_name=city_name, country_id=country_id).exists():
                                found_city = City.objects.get(alt_name=city_name, country_id=country_id)
                        elif City.objects.filter(namepar=city_name, country_id=country_id).exists():
                                found_city = City.objects.get(namepar=city_name, country_id=country_id)

                if not found_city:
                    print "city not found for " + str(city_id)
                    continue

                found_indicator = None
                if Indicator.objects.filter(id=indicator_id).exists():
                        found_indicator = Indicator.objects.get(id=indicator_id)
                else:
                    print "indicator not found for " + str(indicator_id)
                    continue

                if IndicatorData.objects.filter(indicator=found_indicator, city=found_city, year=year).exists():
                    continue

                new_indicator_data = IndicatorData(indicator=found_indicator, city=found_city, value=value, year=year, selection_type=None)
                new_indicator_data.save()

            except Exception as e:
                print "error in update_indicator_data"

         print "ready"

         json_data.close()
         json_data2.close()
