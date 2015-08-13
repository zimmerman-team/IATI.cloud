import datetime

# Django specific
from django.core.management.base import BaseCommand
from cache.validator import Validator


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        v = Validator()
        v.update_response_times_and_add_to_cache()