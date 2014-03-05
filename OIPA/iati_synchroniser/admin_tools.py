from iati.models import Activity
import logging
import gc
from iati.filegrabber import FileGrabber

logger = logging.getLogger(__name__)

class AdminTools():

    curfile = None

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

