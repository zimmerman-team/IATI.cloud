from IATI_2_01 import Parse as IATI_201_Parser
from IATI_1_05 import Parse as IATI_105_Parser
from IATI_1_03 import Parse as IATI_103_Parser
from deleter import Deleter
import gc
from iati.filegrabber import FileGrabber
from lxml import etree
from iati_synchroniser.exception_handler import exception_handler
import hashlib


class ParseIATI():

    # class wide functions
    def return_first_exist(self, xpath_find):

        if not xpath_find:
             xpath_find = None
        else:
            try:
                xpath_find = unicode(xpath_find[0], errors='ignore')
            except:
                xpath_find = xpath_find[0]

            xpath_find = xpath_find.encode('utf-8', 'ignore')
        return xpath_find

    def hashfile(self,afile, hasher, blocksize=65536):
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        return hasher.hexdigest()

    def prepare_parser(self, root, source):
        """
            Prepares the parser, given the lxml activity file root
        """

        iati_version = root.xpath('@version')[0]

        if iati_version == '2.01':
            parser = IATI_201_Parser()
        elif iati_version == '1.03':
            parser = IATI_103_Parser()
            parser.VERSION = iati_version
        else:
            parser = IATI_105_Parser()
            parser.VERSION = iati_version
        
        print 'before parsing'
        parser.iati_source = source

        return parser

    def parse_url(self, source):
        url = source.source_url
        xml_source_ref = source.ref
        last_hash = source.last_hash
        
        try:
            file_grabber = FileGrabber()
            iati_file = file_grabber.get_the_file(url)
            #get the hash
            #hash  = self.hashfile(iati_file,hashlib.md5())
            # if hash == last_hash:
            #     pass
            #     #return
            # else:
            #     source.last_hash = hash
            #     source.save()

            if iati_file:

                # delete old activities
                try:
                    deleter = Deleter()
                    deleter.delete_by_source(xml_source_ref)
                except Exception as e:
                    exception_handler(e, "parse url", "delete by source")

                data = iati_file.read()
                root = etree.fromstring(str(data))

                parser = self.prepare_parser(root, source)
                parser.load_and_parse(root)

                # del iati_file
                # gc.collect()

                # Throw away query logs when in debug mode to prevent memory from overflowing
                if settings.DEBUG:
                    from django import db
                    db.reset_queries()

        except Exception as e:
            exception_handler(e, "parse url", "parse_url")