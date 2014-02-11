# Django specific
from django.core.management.base import BaseCommand

# App specific
from iati_synchroniserp.models import IatiXmlSource, Publisher
import datetime


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        parser = PublisherUpdater()
        parser.update_publisher_activity_count()


class PublisherUpdater():

    def update_publisher_activity_count(self):
        try:

            for pub in Publisher.objects.all():

                pub_xml_count = 0
                pub_oipa_count = 0

                for source in IatiXmlSource.objects.filter(publisher=pub):
                    if source.xml_activity_count and source.oipa_activity_count:
                        pub_xml_count = pub_xml_count + source.xml_activity_count
                        pub_oipa_count = pub_oipa_count + source.oipa_activity_count

                pub.XML_total_activity_count = pub_xml_count
                pub.OIPA_activity_count = pub_oipa_count
                pub.save()

        except Exception as e:
            if e.args:
                print(e.args[0])
            print("ERROR IN UPDATE_PUBLISHER_ACTIVITY_COUNT, FILE URL " + url)

