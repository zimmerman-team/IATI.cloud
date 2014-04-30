# Django specific
from django.core.management.base import BaseCommand
from geodata.updaters import CityUpdater

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        cu = CityUpdater()
        cu.update_cities()