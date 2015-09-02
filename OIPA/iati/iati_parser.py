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

    def parse_url(self, source ):
        url = source.source_url
        xml_source_ref = source.ref
        last_hash = source.last_hash
        
        try:
            #iterate through iati-activity tree
            file_grabber = FileGrabber()
            iati_file = file_grabber.get_the_file(url)
            #get the hash
            #hash  = self.hashfile(iati_file,hashlib.md5())
            #if hash == last_hash:
                #return
            if iati_file:

                # delete old activities
                try:
                    deleter = Deleter()
                    deleter.delete_by_source(xml_source_ref)
                except Exception as e:
                    exception_handler(e, "parse url", "delete by source")
                print 'activities deleted'
                # parse the new file     
                self.xml_source_ref = source
                data = iati_file.read()
                print 'test does it go here?'
                #print data
                print 'iati data is'
                root = etree.fromstring(str(data))
                parser = None
                print root.xpath('@version')
                print self.return_first_exist(root.xpath('@version'))
                iati_version = root.xpath('@version')[0]
                iati_identifier = root.xpath('iati-activity/iati-identifier/text()')

                if iati_version == '2.01':
                    parser = IATI_201_Parser()
                elif iati_version == '1.03':
                    parser = IATI_103_Parser()
                    parser.VERSION = iati_version
                else:
                    parser = IATI_105_Parser()
                    parser.VERSION = iati_version
                print 'before parsing'
                parser.iati_identifier = iati_identifier
                parser.iati_source = source
                parser.load_and_parse(root)

                del iati_file
                gc.collect()

                # Throw away query logs when in debug mode to prevent memory from overflowing
                if settings.DEBUG:
                    from django import db
                    db.reset_queries()

        except Exception as e:
            exception_handler(e, "parse url", "parse_url")