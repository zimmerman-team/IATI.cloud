# Django specific
from django.core.management.base import BaseCommand

# App specific
from utils.models import ParseSchedule


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        [schedule.process(1) for schedule in ParseSchedule.objects.all()]