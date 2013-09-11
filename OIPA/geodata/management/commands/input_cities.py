# Django specific
from django.core.management.base import BaseCommand
from IATI.models import country, city
from geodata.data_backup.city_locations import CITY_LOCATIONS


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        for city in city.objects.all():
            for location in CITY_LOCATIONS['features']:
                if location['properties']['nameascii'] == city.name or location['properties']['namealt'] == city.name or location['properties']['namepar'] == city.name or location['properties']['name'] == city.name:
                    if city.country.iso2 == location['properties']['iso_a2']:
                        city.longitude = location['properties']['longitude']
                        city.latitude = location['properties']['latitude']
                        city.save()
                        print '%s has been updated' % location['properties']['nameascii']



