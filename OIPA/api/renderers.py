from __future__ import unicode_literals
from django.utils import six
from django.utils.six.moves import StringIO
from rest_framework.renderers import BaseRenderer
from lxml import etree
from lxml.builder import E


# TODO: Make this more generic - 2016-01-21
class XMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = 'application/xml'
    format = 'xml'
    charset = 'UTF-8'
    root_tag_name = 'iati-activities'
    item_tag_name = 'iati-activity'
    version = '2.01'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """

        if data is None:
            return ''

        if 'results' in data: # list of items
            xml = E(self.root_tag_name)
            xml.set('version', self.version)
            self._to_xml(xml, data['results'], parent_name=self.item_tag_name)
        else: # one item
            xml = E(self.root_tag_name)
            xml.set('version', self.version)
            self._to_xml(xml, data, parent_name=self.item_tag_name)

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

                    renamed_attr = attr.replace('xml_lang', '{http://www.w3.org/XML/1998/namespace}lang').replace('_', '-')

                    value = data[attr]
                    if value is not None:
                        xml.set(renamed_attr, six.text_type(value).lower() if type(value) == bool else six.text_type(value))


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
            xml.text = six.text_type(data)
            pass

