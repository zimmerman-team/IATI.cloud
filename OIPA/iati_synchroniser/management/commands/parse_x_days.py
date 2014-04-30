from django.core.management.base import BaseCommand
from iati_synchroniser.parse_admin import ParseAdmin

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        days = args['days']
        parser = ParseAdmin()
        parser.parseXDays(days)

