# Django specific
from django.core.management.base import BaseCommand
from geodata.updaters import CountryUpdater

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        cu = CountryUpdater()
        cu.update_country_regions()