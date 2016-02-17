import uuid
import csv

from geodata.models import Country
from geodata.models import City
from indicator.models import Indicator
from indicator.models import IndicatorData
from indicator.models import IndicatorDataValue
from indicator.models import CsvUploadLog

class IndicatorParser:

    def __init__(self):
        self.total_items_saved = 0
        self.city_found = []
        self.city_not_found = []
        self.country_found = []
        self.country_not_found = []

    def parse(self, uploaded, object, request, **kwargs):

        try:
            dialect = csv.Sniffer().sniff(uploaded.read(4048))
        except csv.Error:
            dialect = csv.excel

        csv_file = csv.DictReader(uploaded, dialect=dialect)
        indicator_from_db = None
        city_name_dict = self.get_city_name_dict()
        country_name_dict = self.get_country_name_dict()

        for i, line in enumerate(csv_file):
            if i == 0:
                indicator_from_db = self.get_or_create_indicator(line)

            city_csv = line.get('city')
            selection_type_csv = line.get('selection_type')
            country_csv = line.get('country')
            value_csv = line.get('value')
            year_csv = line.get('year')

            value_csv = self.get_value(value_csv=value_csv)
            if not value_csv:
                continue

            country_from_db = self.find_country(
                country_name=country_csv,
                country_name_dict=country_name_dict)

            city_from_db = self.find_city(
                city_name=city_csv,
                city_name_dict=city_name_dict,
                country=country_from_db)

            if city_from_db:
                if self.save_city_data(
                    city_from_db=city_from_db,
                    selection_type_csv=selection_type_csv,
                    indicator_from_db=indicator_from_db,
                    year_csv=year_csv,
                    value_csv=value_csv
                ):
                    self.total_items_saved += 1
            elif country_from_db:
                if self.save_country_data(
                    country_from_db=country_from_db,
                    city_csv=city_csv,
                    selection_type_csv=selection_type_csv,
                    year_csv=year_csv,
                    indicator_from_db=indicator_from_db,
                    value_csv=value_csv
                ):
                    self.total_items_saved += 1

            if city_from_db:
                self.city_found.append(city_csv)
            elif city_csv:
                self.city_not_found.append(city_csv)
            if country_from_db:
                self.country_found.append(country_csv)
            elif country_csv:
                self.country_not_found.append(country_csv)

        title = kwargs.get('title', [''])[0] or uploaded.name

        log = self.save_log(
            file=uploaded,
            uploaded_by_user=request.user,
            cities_not_found=self.city_not_found,
            countries_not_found=self.country_not_found,
            total_cities_found=self.city_found,
            total_countries_found=self.country_found,
            total_items_saved=self.total_items_saved
        )

        return {
            'url': '/admin/indicator/csvuploadlog/%s/' % str(log.id),
            'thumbnail_url': '',
            'id': str(log.id),
            'name': title,
            'country_not_found': log.countries_not_found,
            'total_countries_not_found': self.country_not_found.__len__(),
            'city_not_found': log.cities_not_found,
            'total_cities_not_found': self.city_not_found.__len__(),
            'total_items_saved': str(self.total_items_saved),
        }

    def get_or_create_indicator(self, line):

        return Indicator.objects.get_or_create(
                    id=line.get('indicator_id'),
                    defaults={
                        'description': line.get('description'),
                        'friendly_label': line.get('friendly_name'),
                        'type_data': line.get('type_data'),
                        'deprivation_type': line.get('deprivation_type'),
                        'category': line.get('category')})[0]

    def get_country_name_dict(self):
        """
        prefetch all country names (iso2, name, alt_name) and put in dict for easy matching
        """
        country_name_list = list()
        country_name_list.extend(Country.objects.values_list('code', 'code'))
        country_name_list.extend(Country.objects.values_list('name', 'code'))
        country_name_list.extend(Country.objects.values_list('alt_name', 'code'))

        country_name_dict = {}
        for item in country_name_list:
            if item[0]:
                country_name_dict[item[0].lower()] = item[1]

        return country_name_dict

    def get_city_name_dict(self):
        """
        prefetch all city names (iso2, name, alt_name) and put in dict for easy matching
        group them under the countries they are in
        """

        cities = City.objects.all()

        def add_to_city_dict(city_name_dict, cities, key):
            for city in cities:
                if city.country_id:
                    country_id = city.country_id.lower()
                    if not country_id in city_name_dict:
                        city_name_dict[country_id] = dict()
                    if getattr(city, key):
                        city_name_dict[country_id][getattr(city, key).lower()] = city.id
            return city_name_dict

        city_name_dict = dict()
        city_name_dict = add_to_city_dict(city_name_dict, cities, 'name')
        city_name_dict = add_to_city_dict(city_name_dict, cities, 'ascii_name')
        city_name_dict = add_to_city_dict(city_name_dict, cities, 'alt_name')
        city_name_dict = add_to_city_dict(city_name_dict, cities, 'namepar')
        return city_name_dict

    def find_country(self, country_name, country_name_dict, iso2=None):
        """
        Mapping the country string, to a country in the database
        @param country_name string from csv document:
        @return: country from database or None if it could not map a country
        """
        if iso2:
            try:
                return Country.objects.get(code=iso2)
            except:
                pass

        if country_name:

            country_name = country_name.lower().decode('utf8', errors='ignore').strip(' \t\n\r')

            if country_name in country_name_dict:
                iso2 = country_name_dict[country_name]
                return Country.objects.get(code=iso2)

        return None

    def find_city(self, city_name, city_name_dict, country):
        """
        Mapping the city string, to a city in the database
        @param city_name string from csv document:
        @return: city from database or None if it could not map a country
        """

        if city_name and country:

            city_name = city_name.lower().decode('utf8', errors='ignore').strip(' \t\n\r')
            country_id = country.code.lower()
            if city_name in city_name_dict[country_id]:
                city_id = city_name_dict[country_id][city_name]
                return City.objects.get(pk=city_id)

        return None

    def save_city_data(self, city_from_db, selection_type_csv, indicator_from_db, year_csv, value_csv):

        if city_from_db and year_csv:

            indicator_data_from_db = IndicatorData.objects.get_or_create(
                indicator=indicator_from_db,
                selection_type=selection_type_csv,
                city=city_from_db)[0]

            # can't use get_or_create since indicator_data / year combo can exist with 'old' value
            if IndicatorDataValue.objects.filter(indicator_data=indicator_data_from_db, year=year_csv).exists():
                indicator_data_value_from_db = IndicatorDataValue.objects.filter(
                    indicator_data=indicator_data_from_db,
                    year=year_csv)[0]
                indicator_data_value_from_db.value = value_csv
            else:
                indicator_data_value_from_db = IndicatorDataValue(
                    indicator_data=indicator_data_from_db,
                    year=year_csv,
                    value=value_csv)

            indicator_data_value_from_db.save()

            return True

        return False

    def save_country_data(self, country_from_db, city_csv, selection_type_csv, year_csv, indicator_from_db, value_csv):

        if country_from_db and year_csv and not city_csv:

            indicator_data_from_db = IndicatorData.objects.get_or_create(
                indicator=indicator_from_db,
                selection_type=selection_type_csv,
                country=country_from_db)[0]

            # can't use get_or_create since indicator_data / year combo can exist with different 'old' value
            if IndicatorDataValue.objects.filter(indicator_data=indicator_data_from_db, year=year_csv).exists():
                indicator_data_value_from_db = IndicatorDataValue.objects.filter(
                    indicator_data=indicator_data_from_db,
                    year=year_csv)[0]
                indicator_data_value_from_db.value = value_csv
            else:
                indicator_data_value_from_db = IndicatorDataValue(
                    indicator_data=indicator_data_from_db,
                    year=year_csv,
                    value=value_csv)

            indicator_data_value_from_db.save()

            return True

        return False

    def get_value(self, value_csv):
        value_csv = str(value_csv)\
            .replace(",", ".")\
            .replace(" ", "")\
            .replace("NULL", "")
        try:
            return float(value_csv)
        except ValueError:
            return None

    def save_log(
            self,
            file,
            uploaded_by_user,
            cities_not_found,
            countries_not_found,
            total_cities_found,
            total_countries_found,
            total_items_saved):

        log = CsvUploadLog()
        log.upload = file
        log.uploaded_by = uploaded_by_user
        log.slug = uuid.uuid4()
        try:
            log.cities_not_found = unicode(', '.join(cities_not_found), errors='ignore')
            log.countries_not_found = unicode(', '.join(countries_not_found), errors='ignore')
        except:
            log.cities_not_found = ', '.join(cities_not_found)
            log.countries_not_found = ', '.join(countries_not_found)

        log.total_cities_found = total_cities_found.__len__()
        log.total_countries_found = total_countries_found.__len__()
        log.total_countries_not_found = countries_not_found.__len__()
        log.total_cities_not_found = cities_not_found.__len__()
        log.total_items_saved = total_items_saved
        log.save()

        return log

