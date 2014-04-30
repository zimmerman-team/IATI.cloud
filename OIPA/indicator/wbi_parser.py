#!/usr/bin/env python
#-*- coding:utf-8 -*-
import csv
from indicator.models import IndicatorTopic, IndicatorSource, Indicator, IndicatorData, Country, Region
import os.path

class WBI_Parser():

    def import_wbi_indicators(self):
        self.update_country_data()
        self.add_indicators()
        self.add_indicator_data()

    def get_topic_or_create(self, topic_name):
        res, created = IndicatorTopic.objects.get_or_create(name=topic_name)
        return res


    def get_source_or_create(self, source_name):
        res, created = IndicatorSource.objects.get_or_create(name=source_name)
        return res


    def get_indicator_or_create(self, indicator_id):
        res, created = Indicator.objects.get_or_create(id=indicator_id)
        return res


    def get_country(self, country_iso3):
        res = Country.objects.get(iso3=country_iso3)
        return res

    def get_region(self, iso3):
        #TO DO: add region iso3 to database
        res = Region.objects.get(iso3=iso3)
        return res


    def get_values_for_years(self, record):
        our_values = []
        for x in record:
            if record.index(x) >= 4 and x:
                tup = (record.index(x), x)
                our_values.append(tup)
        return our_values


    def decode_data(self, data):
        return data.decode("cp1252", errors='replace')


    def add_indicators(self):
        BASE = os.path.dirname(os.path.abspath(__file__))
        specific = BASE + "/data_backup/wdi_data/WDI_Series.csv"

        with open(specific, 'rb') as f:
            series_reader = csv.reader(f)
            series_header = series_reader.next()
            for row in series_reader:
                indicator_id = row[series_header.index("Series Code")]
                indicator_id = self.decode_data(indicator_id)
                new_indicator = self.get_indicator_or_create(indicator_id)
                if new_indicator.source and new_indicator.topic:
                    pass
                else:
                    source_data = row[series_header.index("Source")]
                    source_data = self.decode_data(source_data)
                    topic_data = row[series_header.index("Topic")]
                    topic_data = self.decode_data(topic_data)
                    source = self.get_source_or_create(source_data)
                    topic = self.get_topic_or_create(topic_data)
                    new_indicator.topic = topic
                    new_indicator.source = source
                    type_data = row[series_header.index("Aggregation method")]
                    new_indicator.type_data = self.decode_data(type_data)
                    description = row[series_header.index("Long definition")]
                    new_indicator.description = self.decode_data(description)
                    friendly_label = row[series_header.index("Indicator Name")]
                    new_indicator.friendly_label = self.decode_data(friendly_label)
                    new_indicator.id = indicator_id
                    new_indicator.save()


    def add_indicator_data(self):
        BASE = os.path.dirname(os.path.abspath(__file__))
        specific = BASE + "/data_backup/wdi_data/WDI_Data.csv"

        with open(specific, 'rb') as f:
            data_reader = csv.reader(f)
            data_header = data_reader.next()
            for row in data_reader:
                indicator_code = row[data_header.index("Indicator Code")]
                our_indicator = self.get_indicator_or_create(indicator_code)
                iso3 = row[data_header.index("Country Code")]
                our_country = self.get_country(iso3)
                if not our_country:
                    our_region = self.get_region(iso3)

                our_values = self.get_values_for_years(row)
                if len(our_values) >= 1:
                    for item in our_values:
                        our_data = IndicatorData()
                        our_data.indicator = our_indicator
                        our_data.year = data_header[item[0]]
                        our_data.value = item[1]
                        our_data.country = our_country
                        our_data.save()


    def update_country_data(self):
        BASE = os.path.dirname(os.path.abspath(__file__))
        specific = BASE + "/data_backup/wdi_data/WDI_Country.csv"

        with open(specific, 'rb') as f:
            data_reader = csv.reader(f)
            data_header = data_reader.next()
            for row in data_reader:
                country_iso3 = row[data_header.index("Country Code")]
                country_iso2 = row[data_header.index("2-alpha code")]
                name = row[data_header.index("Table Name")]

                if country_iso2 == "":
                    if not (Country.objects.filter(iso3=country_iso3)).exists():
                        new_country = Country()
                        new_country.code = country_iso2
                        new_country.iso3 = country_iso3
                        new_country.name = name
                        new_country.language = "en"
                        new_country.data_source = "WDI"
                        new_country.save()

                elif not (Country.objects.filter(code=country_iso2)).exists():
                    new_country = Country()
                    new_country.code = country_iso2
                    new_country.iso3 = country_iso3
                    new_country.name = name
                    new_country.language = "en"
                    new_country.data_source = "WDI"
                    new_country.save()