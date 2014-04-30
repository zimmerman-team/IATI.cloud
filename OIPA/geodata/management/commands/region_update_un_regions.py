# Django specific
from django.core.management.base import BaseCommand
from geodata.updaters import RegionUpdater

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        ru = RegionUpdater()
        ru.update_un_regions()