from IATI_2_01 import Parse as IATI_201_Parser
from IATI_1_05 import Parse as IATI_105_Parser
from IATI_1_03 import Parse as IATI_103_Parser
from iati_organisation.parser.organisation_2_01 import Parse as Org_2_01_Parser
from iati_organisation.parser.organisation_1_05 import Parse as Org_1_05_Parser
from iati.filegrabber import FileGrabber
from lxml import etree
from django import db
from django.conf import settings
import hashlib


class ParserDisabledError(Exception):
    def __init__(self, message):
        super(ParserDisabledError, self).__init__(message)


class ParseManager():
    def __init__(self, source, root=None, force_reparse=False):
        """
        Given a source IATI file, prepare an IATI parser
        """

        if settings.IATI_PARSER_DISABLED:
            raise ParserDisabledError("The parser is disabled on this instance of OIPA")

        self.source = source
        self.url = source.source_url
        self.xml_source_ref = source.ref
        self.force_reparse = force_reparse
        self.hash_changed = True
        self.valid_source = True
        
        if root is not None:
            self.root = root
            self.parser = self._prepare_parser(self.root, source)
            return

        file_grabber = FileGrabber()
        response = file_grabber.get_the_file(self.url)

        if not response or response.code != 200:
            self.valid_source = False
            self.source.parse_notes = 'URL down or does not exist'
            self.source.save()
            return

        iati_file = response.read()
        iati_file_str = str(iati_file)

        hasher = hashlib.sha1()
        hasher.update(iati_file_str)
        sha1 = hasher.hexdigest()

        if source.sha1 == sha1:
            # source did not change, no need to reparse normally
            self.hash_changed = False
        else:
            source.sha1 = sha1

        try:
            self.root = etree.fromstring(iati_file_str)
            self.parser = self._prepare_parser(self.root, source)
        except etree.XMLSyntaxError as e:
            self.valid_source = False
            self.source.parse_notes = 'XMLSyntaxError: ' + e.message
            self.source.save()
            return

    def _prepare_parser(self, root, source):
        """
            Prepares the parser, given the lxml activity file root
        """

        iati_version = root.xpath('@version')

        if len(iati_version) > 0:
            iati_version = iati_version[0]
        # activity file
        if source.type == 1:
            if iati_version == '2.02':
                parser = IATI_201_Parser(root)
            elif iati_version == '2.01':
                parser = IATI_201_Parser(root)
            elif iati_version == '1.03':
                parser = IATI_103_Parser(root)
                parser.VERSION = iati_version
            else:
                parser = IATI_105_Parser(root)
                parser.VERSION = '1.05'

        #organisation file
        elif source.type == 2:
            if iati_version == '2.02':
                parser = Org_2_01_Parser(root)
                parser.VERSION = iati_version
            elif iati_version == '2.01':
                parser = Org_2_01_Parser(root)
                parser.VERSION = iati_version
            else:
                parser = Org_1_05_Parser(root)

        parser.force_reparse = self.force_reparse
        parser.iati_source = source

        return parser

    def get_parser(self):
        return self.parser

    def parse_all(self):
        """
        Parse all activities 
        """
        # only start parsing when the file changed (or on force)
        if (self.force_reparse or self.hash_changed) and self.valid_source:
            self.parser.load_and_parse(self.root)

        # Throw away query logs when in debug mode to prevent memory from overflowing
        if settings.DEBUG:
            db.reset_queries()

    def parse_activity(self, activity_id):
        """
        Parse only one activity with {activity_id}
        """

        try:
            (activity,) = self.root.xpath('//iati-activity/iati-identifier[text()="{}"]'.format(activity_id))
        except ValueError:
            raise ValueError("Activity {} doesn't exist in {}".format(activity_id, self.url))

        self.parser.parse(activity.getparent())
        self.parser.save_all_models()

