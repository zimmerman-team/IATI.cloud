# Django specific
from django.core.management.base import BaseCommand
from geodata.updaters import Admin1RegionUpdater

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        adm1ru = Admin1RegionUpdater()
        adm1ru.update_all()