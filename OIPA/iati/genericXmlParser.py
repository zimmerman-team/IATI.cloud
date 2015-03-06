from lxml import etree
from parse_logger import *

class XMLParser():

    def testWithExampleFile(self):
        with open ("activity-standard-example-annotated.xml", "r") as myfile:
            data=myfile.read().replace('\n', '')
        self.load(data);
    



    def load_and_parse(self,xml,parse_helper):
        root = etree.fromstring(xml)
        self.root = root
        self.parse_helper = parse_helper
        self.parse(root)

    def parse(self,Element):

        for e in Element:
            function_name =  self.generate_function_name(self.root.getroottree().getpath(e))

            if(hasattr(self, function_name) and callable(getattr(self, function_name))):
                elementMethod = getattr(self,function_name);
                try:
                    self.parse(elementMethod(e))
                except exceptException as e:


            else:
                self.handle_function_not_found(x_path,function_name);
                print function_name
                
                self.parse(e)


    def generate_function_name(self,xpath):
        function_name = xpath.replace('/','_')
        function_name = function_name.replace('-','_')
        return function_name[1:]

    def iati_activities_iati_activity_crs_add_loan_status_interest_received(self,element):
        print 'function found'
        print element.tag 
        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    def handle_function_not_found(self,xpath,function_name):
        hint = """
     def """+function_name+"""(self,element):
        print 'function found'
        print element.tag 
        #store element 
        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element"""
        print hint

        log_entry = ParseLog()
        log_entry.hint = hint
        log_entry.error_message='Function '+function_name+'not found'
        log_entry.file = 'test'
        log_entry.location = xpath
        log_entry.save()

    def handle_exception(self,xpath,function_name,exception):
        hint = """look at XML document"""

        log_entry = ParseLog()
        log_entry.hint = hint
        log_entry.error_message = str(exception)
        log_entry.file = 'test'
        log_entry.location = xpath
        log_entry.save()


