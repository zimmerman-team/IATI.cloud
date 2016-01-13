# from rest_framework.renderers import BaseRenderer
# from django.utils import six
# from lxml import etree
# from lxml.builder import E


# class XMLRenderer(BaseRenderer):

#     """Renderer which serializes to XML using properties"""

#     media_type = 'application/xml'
#     format = 'xml'
#     charset = 'utf-8'
#     item_tag_name = 'list-item'
#     root_tag_name = 'root'

#     def __init__(self):
#         BaseRenderer.__init__(self)

#     def render(self, data, accepted_media_type=None, renderer_context=None):
#         """
#         """

#         xml = etree.Element(self.root_tag_name)
#         self._to_xml(xml, data)

#     def _to_xml(self, xml, data):
#         if isinstance(data, (list, tuple)):
#             for item in data:
#                 self._to_xml(xml, item)

        
#         if isinstance(data, dict): # orderedDict with properties
#             if hasattr(data, 'xml_properties'):
#                 # these items are attributes, set them as attributes on parent
#                 for attr in getattr(data, 'xml_properties'):
#                     xml.set(attr, data[attr])




                

#             for key, value in six.iteritems(data):
#                 self._to_xml(xml.append(E(key, )), )


# """
# Provides XML rendering support.
# """
from __future__ import unicode_literals

from django.utils import six
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.six.moves import StringIO
from django.utils.encoding import smart_text
from rest_framework.renderers import BaseRenderer


class XMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = 'application/xml'
    format = 'xml'
    charset = 'utf-8'
    item_tag_name = 'list-item'
    root_tag_name = 'root'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ''

        stream = StringIO()
        
        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        xml.startElement(self.root_tag_name, {})

        self._to_xml(xml, data)

        xml.endElement(self.root_tag_name)
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                xml.startElement(self.item_tag_name, {})
                self._to_xml(xml, item)
                xml.endElement(self.item_tag_name)

        elif isinstance(data, dict):
            attributes = []
            if hasattr(data, 'xml_attributes'):
                attributes = getattr(data, 'xml_attributes')

            for attr in attributes:
                xml.set(attr, data[attr])

            for key, value in six.iteritems(data):
                if key in attributes: continue

                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key)

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(smart_text(data))
