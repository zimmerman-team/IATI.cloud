# pylint: disable=B410
from xml.etree import ElementTree  # NOQA: B410

# pylint: disable=B410
from lxml.builder import E  # NOQA: B410

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
