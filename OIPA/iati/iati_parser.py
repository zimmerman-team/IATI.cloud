from IATI_2_01 import Parse as IATI_201_Parser
from IATI_1_05 import Parse as IATI_105_Parser
from IATI_1_03 import Parse as IATI_103_Parser
from iati_organisation.organisation_2_01 import Parse as Org_2_01_Parser
from iati_organisation.organisation_1_05 import Parse as Org_1_05_Parser
from iati.filegrabber import FileGrabber
from lxml import etree
from iati_synchroniser.exception_handler import exception_handler
from django.conf import settings


class ParseIATI():


    def prepare_parser(self, root, source):
        """
            Prepares the parser, given the lxml activity file root
        """

        iati_version = root.xpath('@version')

        if len(iati_version) > 0:
            iati_version = iati_version[0]
        if source.type == 1:
            if iati_version == '2.01':
                parser = IATI_201_Parser()
            elif iati_version == '1.03':
                parser = IATI_103_Parser()
                parser.VERSION = iati_version
            else:
                parser = IATI_105_Parser()
                parser.VERSION = '1.05'
        elif source.type == 2:
            #organisation file
            if iati_version == '2.01':
                parser = Org_2_01_Parser()
                parser.VERSION = iati_version
            else:
                parser = Org_1_05_Parser()
        
        parser.iati_source = source

        return parser

    def parse_url(self, source):
        """
        Parses the source with url
        """
        url = source.source_url
        xml_source_ref = source.ref
        # last_hash = source.last_hash
        
        try:
            file_grabber = FileGrabber()
            iati_file = file_grabber.get_the_file(url)

            if iati_file:

                # delete old activities
                # TODO: determine this in the parser based on last-updated-datetime
                # TODO: also, throw away all narratives
                # try:
                #     deleter = Deleter()
                #     deleter.delete_by_source(xml_source_ref)
                # except Exception as e:
                #     exception_handler(e, "parse url", "delete by source")

                data = iati_file.read()
                root = etree.fromstring(str(data))

                parser = self.prepare_parser(root, source)
                parser.load_and_parse(root)

                # Throw away query logs when in debug mode to prevent memory from overflowing
                if settings.DEBUG:
                    from django import db
                    db.reset_queries()

        except Exception as e:
            exception_handler(e, "parse url", "parse_url")
