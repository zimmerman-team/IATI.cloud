# Django specific
from django.core.management.base import BaseCommand

# App specific
from IATI_synchroniser.models import iati_xml_source
import datetime


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        parser = ParseSchedule()
        parser.parseSchedule()


class ParseSchedule():

    def parseSchedule(self):

        def parse(source):
            curdate = float(datetime.datetime.now().strftime('%s'))
            last_updated = float(source.date_updated.strftime('%s'))
            update_interval = source.update_interval

            if update_interval == "day":
                update_interval_time = 24 * 60 * 60
            if update_interval == "week":
                update_interval_time = 24 * 60 * 60 * 7
            if update_interval == "month":
                update_interval_time = 24 * 60 * 60 * 7 * 4.34
            if update_interval == "year":
                update_interval_time = 24 * 60 * 60 * 365


            if ((curdate - update_interval_time) > last_updated):
                print "Now updating " + source.source_url
                source.save()

        [parse(source) for source in iati_xml_source.objects.all()]


