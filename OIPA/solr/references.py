from xml.etree import ElementTree

from lxml.builder import E

from api.iati.elements import ElementReference


class ConvertElementReference(ElementReference):
    root_element = 'root'

    def to_string(self, ):
        # To make XML we need root element
        self.parent_element = E(self.root_element)

        # Build XML
        self.create()

        # Convert to string
        xml_str = ElementTree.tostring(self.parent_element).decode()

        # We don't need only transaction element
        xml_str = xml_str.replace('<root>', '').replace('</root>', '')

        return xml_str
