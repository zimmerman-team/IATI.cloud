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
from lxml import etree
from lxml.builder import E


class XMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = 'application/xml'
    format = 'xml'
    charset = 'UTF-8'
    root_tag_name = 'iati-activities'
    item_tag_name = 'iati-activity'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ''

        if 'results' in data: # list of items
            xml = E(self.root_tag_name)
            self._to_xml(xml, data['results'], parent_name=self.item_tag_name)
        else: # one item
            xml = E(self.item_tag_name)
            self._to_xml(xml, data)

        return etree.tostring(xml, encoding=self.charset)

    def _to_xml(self, xml, data, parent_name=None):
        if isinstance(data, (list, tuple)):
            for item in data:
                self._to_xml(etree.SubElement(xml, parent_name.replace('_', '-')), item)

        elif isinstance(data, dict):
            attributes = []

            if hasattr(data, 'xml_meta'):
                attributes = list(set(data.xml_meta.get('attributes', list())) & set(data.keys()))

                for attr in attributes:

                    if hasattr(data[attr], 'xml_meta'):
                        only = data[attr].xml_meta.get('only', None)
                    else:
                        only = None

                    renamed_attr = data.xml_meta.get('rename', {}).get(attr, attr)
                    renamed_attr = renamed_attr.replace('_', '-')

                    if only:
                        xml.set(renamed_attr, unicode(data[attr][only]))
                    else:
                        xml.set(renamed_attr, unicode(data[attr]))


            for key, value in six.iteritems(data):
                if key in attributes: continue

                if key == 'text':
                    self._to_xml(xml, value)
                elif isinstance(value, list):
                    self._to_xml(xml, value, parent_name=key)
                else:
                    self._to_xml(etree.SubElement(xml, key.replace('_', '-')), value)

        elif data is None:
            pass

        else:
            xml.text = unicode(data)
            pass

