# Django specific
from django.core.management.base import BaseCommand
from iati.models import country
from geodata.models import city

from geodata

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        for indivcity in city.objects.all():
            for location in CITY_LOCATIONS['features']:
                if location['properties']['nameascii'] == indivcity.name or location['properties']['namealt'] == indivcity.name or location['properties']['namepar'] == indivcity.name or location['properties']['name'] == indivcity.name:
                    if indivcity.country.iso2 == location['properties']['iso_a2']:
                        indivcity.longitude = location['properties']['longitude']
                        indivcity.latitude = location['properties']['latitude']
                        indivcity.save()
                        print '%s has been updated' % location['properties']['nameascii']



