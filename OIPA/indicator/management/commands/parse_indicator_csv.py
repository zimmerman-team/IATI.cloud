import os
import csv
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from geodata.models import Country
from geodata.models import City

from indicator.models import Indicator
from indicator.upload_indicators_helper import find_country
from indicator.upload_indicators_helper import find_city
from indicator.upload_indicators_helper import save_city_data
from indicator.upload_indicators_helper import save_country_data



class Command(BaseCommand):
    option_list = BaseCommand.option_list
    
    def __init__(self, *args, **kwargs):
        """
        Set up initial data such as indicators, countries and cities cache 
        """
        super(Command, self).__init__(*args, **kwargs)
        self.indicators = dict([(i.pk, i) for i in Indicator.objects.all()])
        self.countries = Country.objects.all()
        self.cities = City.objects.all()

        self.keys = [
            'city',
            'deprivation_type',
            'description',
            'selection_type',
            'country',
            'region_csv',
            'friendly_name',
            'value',
            'year_range',
            'indicator_id',
            'year',
            'type_data',
            'category'
        ]

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("Please provide path to file or directory with indicators csv data")

        path = args[0]

        if os.path.isdir(path):
            self.parse_dir(path)
        else:
            self.parse_file(path)

    def parse_dir(self, directory):
        for root, dirs, files in os.walk(directory, topdown=False):
            for file in files:
                self.parse_file(os.path.join(root, file))

    def parse_file(self, filename):
        """
        Parse CSV file and save data into DB
        """
        self.stdout.write("Parsing file: '{filename}'".format(filename=filename))


        with open(filename) as csv_file:
            try:
                dialect = csv.Sniffer().sniff(csv_file.read(4048))
                # Reset file cursor
                csv_file.seek(0)
            except csv.Error:
                dialect = csv.excel

            csv_data = csv.DictReader(csv_file, dialect=dialect, delimiter=';')

            for line in csv_data:
                line['value'] = str(line.get('value', '').replace('.', ','))

                indicator = self.get_indicator(line)
                country_id = self.get_country_id(line)
                city_id = self.get_city_id(line)

                if city_id:
                    save_city_data(
                        city_from_db=city_id,
                        country_from_db=country_id,
                        selection_type_csv=line.get('selection_type', None),
                        indicator_from_db=indicator,
                        year_csv=line.get('year', None),
                        value_csv=line.get('value', '')
                    )

    def get_indicator(self, data):
        """
        Get or create indicator from db
        """
        id = data.get('indicator_id', None)
        try:
            return self.indicators[id]
        except KeyError:
            self.stdout.write("* Creating indicator: '{id}'".format(id=id))
            self.indicators[id] = Indicator(id=id,
                **dict([(key, data.get(key, '')) for key in [
                        'description',
                        'friendly_label',
                        'type_data',
                        'deprivation_type',
                        'category'
                    ]
                ]))
            return self.indicators[id]

    def get_country_id(self, data):
        """
        Try to get country id by name from data
        """
        country = find_country(data.get('country', None), self.countries)

        try:
            return country.code
        except AttributeError:
            try:
                self.stderr.write("Can not find country '{country}'".format(
                    country=data.get('country', None)))
            except UnicodeDecodeError:
                pass
            return None

    def get_city_id(self, data, country_id=None):
        """
        Try to get city id by name from data
        """
        return find_city(
            city_name=data.get('city', None),
            cities=self.cities,
            country_id=country_id
        )
