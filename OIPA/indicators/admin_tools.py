
from indicators.data_backup.indicator_names import mapping_names
from indicators.models import indicator, indicator_data
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from indicators.data_backup.indicator_data import IndicatorData
from indicators.data_backup.indicator_city_data import IndicatorCityData
from indicators.data_backup.city_ids import IndicatorCityInfo
from geodata.models import country, city

class IndicatorAdminTools():

    def update_indicators(self):

        for key, value in mapping_names.items():

            try:
                new_indicator = indicator(id=key, friendly_label=value["name"], type_data=value["type_data"])
                new_indicator.save()

            except IntegrityError, e:
                print e.message

            except ValueError, e:
                print e.message

            except ValidationError, e:
                print e.message


    def update_indicator_data(self):
        id = IndicatorData()
        indicator_data_set = id.get_indicator_data()
        for d in indicator_data_set:
            try:
                indicator_name = d['indicator_name']
                country_iso = d['country_iso']

                value = d['value']
                year = d['year']


                if value == None or value == "NULL":
                    continue

                found_country = None
                if country.objects.filter(code=country_iso).exists():
                        found_country = country.objects.get(code=country_iso)
                else:
                    print "indicator not found for " + str(country_iso)
                    continue

                found_indicator = None
                if indicator.objects.filter(id=indicator_name).exists():
                        found_indicator = indicator.objects.get(id=indicator_name)
                else:
                    print "indicator not found for " + str(indicator_name)
                    continue

                if indicator_data.objects.filter(indicator=found_indicator, country=found_country, year=year).exists():
                    continue

                new_indicator_data = indicator_data(indicator=found_indicator, country=found_country, value=value, year=year)
                new_indicator_data.save()

            except:
                print "error in update_indicator_data"

        print "ready"


    def update_indicator_city_data(self):

         icd = IndicatorCityData()
         indicator_data_set = icd.get_indicator_city_data()
         ici = IndicatorCityInfo()
         city_info_set = ici.get_indicator_city_info()

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

                        if city.objects.filter(name=city_name, country_id=country_id).exists():
                            found_city = city.objects.get(name=city_name, country_id=country_id)
                        elif city.objects.filter(ascii_name=city_name, country_id=country_id).exists():
                                found_city = city.objects.get(ascii_name=city_name, country_id=country_id)
                        elif city.objects.filter(alt_name=city_name, country_id=country_id).exists():
                                found_city = city.objects.get(alt_name=city_name, country_id=country_id)
                        elif city.objects.filter(namepar=city_name, country_id=country_id).exists():
                                found_city = city.objects.get(namepar=city_name, country_id=country_id)

                if not found_city:
                    print "city not found for " + str(city_id)
                    continue

                found_indicator = None
                if indicator.objects.filter(name=indicator_id).exists():
                        found_indicator = indicator.objects.get(name=indicator_id)
                else:
                    print "indicator not found for " + str(indicator_id)
                    continue

                if indicator_data.objects.filter(indicator=found_indicator, city=found_city, year=year).exists():
                    continue

                new_indicator_data = indicator_data(indicator=found_indicator, city=found_city, value=value, year=year)
                new_indicator_data.save()

            except:
                print "error in update_indicator_data"

         print "ready"