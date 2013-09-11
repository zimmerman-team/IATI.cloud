import datetime

# Django specific
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

# App specific
from utils.models import IATIXMLSource


class Command(BaseCommand):
    option_list = BaseCommand.option_list
    counter = 0

    def handle(self, *args, **options):
        def parse(source):
            self.counter += 1
            print u"[", self.counter, u"]", _(u"parsing"), source.source_url
            source.process(verbosity=2)
            source.date_updated = datetime.datetime.now()
            source.save()
        [parse(source) for source in IATIXMLSource.objects.all()]