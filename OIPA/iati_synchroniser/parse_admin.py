from iati.models import Activity
import logging
from iati_synchroniser.models import IatiXmlSource, Publisher
import datetime
import gc
from iati.filegrabber import FileGrabber

logger = logging.getLogger(__name__)

class ParseAdmin():

    def parseAll(self):

        def parse(source):

            source.save()
        [parse(source) for source in IatiXmlSource.objects.all()]

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

        [parse(source) for source in IatiXmlSource.objects.all()]


    def parseXDays(self, days):

        def parse(source):
            curdate = float(datetime.datetime.now().strftime('%s'))
            last_updated = float(source.date_updated.strftime('%s'))

            update_interval_time = 24 * 60 * 60 * int(days)

            if ((curdate - update_interval_time) > last_updated):
                print "Now updating " + source.source_url
                source.save()

        [parse(source) for source in IatiXmlSource.objects.all()]



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
            print("ERROR IN UPDATE_PUBLISHER_ACTIVITY_COUNT, ORG ID " + pub.org_id)

    def get_xml_activity_amount(self, url):
        try:
            file_grabber = FileGrabber()
            xml_file = file_grabber.get_the_file(url)
            occurences = 0

            for line in xml_file:

                if "</iati-identifier>" in line:
                    amount = line.count("</iati-identifier>")
                    occurences += amount

            del xml_file
            gc.collect()
            return occurences

        except Exception as e:
            if e.args:
                print(e.args[0])
            print("ERROR IN GET_XML_ACTIVITY_AMOUNT, FILE URL " + url)


    def get_oipa_activity_amount(self, source_ref):
        return Activity.objects.filter(xml_source_ref=source_ref).count()

    # def set_xml_source_meta(self):
    #     iati_standard_version = self.return_first_exist(elem.xpath('@version'))

