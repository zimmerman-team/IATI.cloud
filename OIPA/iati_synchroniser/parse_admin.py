from iati_synchroniser.models import Dataset
import datetime


class ParseAdmin():

    def parseAll(self):

        def parse(source):
            source.save()

        [parse(source) for source in Dataset.objects.all()]

    def parseXDays(self, days):

        def parse(source):
            curdate = float(datetime.datetime.now().strftime('%s'))
            last_updated = float(source.date_updated.strftime('%s'))

            update_interval_time = 24 * 60 * 60 * int(days)

            if ((curdate - update_interval_time) > last_updated):
                print "Now updating " + source.source_url
                source.save()

        [parse(source) for source in Dataset.objects.all()]



