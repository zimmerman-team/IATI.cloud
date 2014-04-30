from django.core.management.base import BaseCommand
from iati_synchroniser.parse_admin import ParseAdmin


class Command(BaseCommand):
    option_list = BaseCommand.option_list
    counter = 0

    def handle(self, *args, **options):
        parser = ParseAdmin()
        parser.parseAll()

