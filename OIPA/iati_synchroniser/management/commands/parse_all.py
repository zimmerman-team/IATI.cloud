import datetime

# Django specific
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

# App specific
from iati_synchroniser.models import IatiXmlSource


class Command(BaseCommand):
    option_list = BaseCommand.option_list
    counter = 0

    def handle(self, *args, **options):
        parser = ParseAll()
        parser.parseAll()


class ParseAll():

    def parseAll(self):

        def parse(source):
            source.save()
        [parse(source) for source in IatiXmlSource.objects.all()]

