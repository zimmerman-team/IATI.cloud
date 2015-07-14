from IATI_2_01 import Parse as IATI_201_Parser
from IATI_1_05 import Parse as IATI_105_Parser
from deleter import Deleter
import gc
from iati.filegrabber import FileGrabber
from lxml import etree
from iati_synchroniser.exception_handler import exception_handler
import hashlib




class ParseIATI():

    def hashfile(self,afile, hasher, blocksize=65536):
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        return hasher.hexdigest()

    def parse_url(self, source ):
        url = source.source_url
        xml_source_ref = source.ref
        last_hash = source.last_hash
        
        try:
            #iterate through iati-activity tree
            file_grabber = FileGrabber()
            iati_file = file_grabber.get_the_file(url)
            #get the hash
            hash  = self.hashfile(iati_file,hashlib.MD5())
            if hash == last_hash:
                return
            if iati_file:

                # delete old activities
                try:
                    deleter = Deleter()
                    deleter.delete_by_source(xml_source_ref)
                except Exception as e:
                    exception_handler(e, "parse url", "delete by source")
                print 'activities deleted'
                # parse the new file
                self.xml_source_ref = xml_source_ref
                data = iati_file.read()
                print data
                print 'iati data is'
                root = etree.fromstring(str(data))
                parser = None
                print root.xpath('@version')
                if root.xpath('@version')[0] == '2.01':
                    parser = IATI_201_Parser()
                else:
                    parser = IATI_105_Parser()
                    parser.VERSION = root.xpath('@version')[0]
                print 'before parsing'
                parser.load_and_parse(root)

                del iati_file
                gc.collect()

                # Throw away query logs when in debug mode to prevent memory from overflowing
                if settings.DEBUG:
                    from django import db
                    db.reset_queries()

        except Exception as e:
            exception_handler(e, "parse url", "parse_url")