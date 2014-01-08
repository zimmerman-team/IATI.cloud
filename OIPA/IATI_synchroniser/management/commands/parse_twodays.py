__author__ = 'vincentvantwestende'



# Django specific
from django.core.management.base import BaseCommand

# App specific
from IATI_synchroniser.models import iati_xml_source
import datetime


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        parser = ParseTwoDays()
        parser.parseTwoDays()


class ParseTwoDays():

    def parseTwoDays(self):

        def parse(source):
            curdate = float(datetime.datetime.now().strftime('%s'))
            last_updated = float(source.date_updated.strftime('%s'))

            update_interval_time = 24 * 60 * 60 * 2

            if ((curdate - update_interval_time) > last_updated):
                print "Now updating " + source.source_url
                source.save()

        [parse(source) for source in iati_xml_source.objects.all()]


