from __future__ import unicode_literals
from django.utils import six
from django.utils.six.moves import StringIO
from rest_framework.renderers import BaseRenderer
from lxml import etree
from lxml.builder import E
from django.conf import settings
from collections import OrderedDict

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
    version = '2.02'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """

        if data is None:
            return ''

        if 'results' in data:
            data = data['results']

        xml = E(self.root_tag_name)
        xml.set('version', self.version)

        if hasattr(settings, 'EXPORT_COMMENT'):
            xml.append(etree.Comment(getattr(settings, 'EXPORT_COMMENT')))

        self._to_xml(xml, data, parent_name=self.item_tag_name)

        return etree.tostring(xml, encoding=self.charset, pretty_print=True)

    def _to_xml(self, xml, data, parent_name=None):
        if isinstance(data, (list, tuple)):
            for item in data:
                self._to_xml(etree.SubElement(xml, parent_name.replace('_', '-')), item)

        elif isinstance(data, dict):
            attributes = []

            if hasattr(data, 'xml_meta'):
                attributes = list(set(data.xml_meta.get('attributes', list())) & set(data.keys()))

                for attr in attributes:

                    renamed_attr = attr.replace(
                        'xml_lang', '{http://www.w3.org/XML/1998/namespace}lang').replace('_', '-')

                    value = data[attr]
                    if value is not None:
                        xml.set(
                            renamed_attr, six.text_type(value).lower() if isinstance(
                                value, bool) else six.text_type(value))

            for key, value in six.iteritems(data):

                if key in attributes:
                    continue

                if key == 'text':
                    self._to_xml(xml, value)
                elif isinstance(value, list):
                    self._to_xml(xml, value, parent_name=key)
                else:
                    # TODO remove this ugly hack by adjusting the resultindicatorperiod actual / target models. 30-08-16
                    # currently actuals are stored on the resultindicatorperiod, hence we need
                    # to remove empty actuals here.
                    if key in ['actual', 'target']:
                        if value.items()[0][0] != 'value':
                            continue

                    self._to_xml(etree.SubElement(xml, key.replace('_', '-')), value)

        elif data is None:
            pass

        else:
            xml.text = six.text_type(data)
            pass


import csv
from rest_framework_csv.renderers import CSVRenderer


class PaginatedCSVRenderer(CSVRenderer):
    results_field = 'results'
    header = []

    def __init__(self, *args, **kwargs):
        super(PaginatedCSVRenderer, self).__init__(*args, **kwargs)
        self.writer_opts = {
            'quoting': csv.QUOTE_ALL,
            'quotechar': '"'.encode('utf-8'),
            'delimiter': ';'.encode('utf-8')
        }

    def render(self, data, *args, **kwargs):
        # TODO: this is probably a bug in DRF, might get fixed later then need to
        # update this - 2017-04-03
        actual_kwargs = args[1].get('kwargs', {})

        # this is a list view
        if 'pk' not in actual_kwargs:
            data = data.get(self.results_field, [])

        return super(PaginatedCSVRenderer, self).render(data, *args, **kwargs)


class OrganisationXMLRenderer(XMLRenderer):
    root_tag_name = 'iati-organisations'
    item_tag_name = 'iati-organisation'
