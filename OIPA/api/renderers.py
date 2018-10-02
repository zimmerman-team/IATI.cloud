#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import csv
import io
from collections import OrderedDict

import xlsxwriter
from django.conf import settings
from django.utils import six
from lxml import etree
from lxml.builder import E
from rest_framework.renderers import BaseRenderer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from rest_framework_csv.renderers import CSVRenderer

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
                self._to_xml(etree.SubElement(
                    xml, parent_name.replace('_', '-')), item)

        elif isinstance(data, dict):
            attributes = []

            if hasattr(data, 'xml_meta'):
                attributes = list(set(data.xml_meta.get(
                    'attributes', list())) & set(data.keys()))

                for attr in attributes:

                    renamed_attr = attr.replace(
                        'xml_lang',
                        '{http://www.w3.org/XML/1998/namespace}lang'
                    ).replace('_', '-')

                    value = data[attr]
                    if value is not None:
                        xml.set(
                            renamed_attr,
                            six.text_type(value).lower() if isinstance(
                                value, bool
                            ) else six.text_type(value))

            for key, value in six.iteritems(data):

                if key in attributes:
                    continue

                if key == 'text':
                    self._to_xml(xml, value)
                elif isinstance(value, list):
                    self._to_xml(xml, value, parent_name=key)
                else:
                    # TODO remove this ugly hack by adjusting the
                    # resultindicatorperiod actual / target models. 30-08-16
                    # currently actuals are stored on the
                    # resultindicatorperiod, hence we need to remove empty
                    # actuals here.
                    if key in ['actual', 'target']:
                        if list(value.items())[0][0] != 'value':
                            continue

                    self._to_xml(etree.SubElement(
                        xml, key.replace('_', '-')), value)

        elif data is None:
            pass

        else:
            xml.text = six.text_type(data)
            pass


class PaginatedCSVRenderer(CSVRenderer):
    results_field = 'results'
    header = []

    def __init__(self, *args, **kwargs):
        super(PaginatedCSVRenderer, self).__init__(*args, **kwargs)
        self.writer_opts = {
            'quoting': csv.QUOTE_ALL,
            'quotechar': '"',
            'delimiter': ';'
        }

    def render(self, data, *args, **kwargs):
        # TODO: this is probably a bug in DRF, might get fixed later then
        # need to update this - 2017-04-03
        actual_kwargs = args[1].get('kwargs', {})

        # this is a list view
        if 'pk' not in actual_kwargs:
            data = data.get(self.results_field, [])

        return super(PaginatedCSVRenderer, self).render(data, *args, **kwargs)


class OrganisationXMLRenderer(XMLRenderer):
    root_tag_name = 'iati-organisations'
    item_tag_name = 'iati-organisation'


# All of this was done in the same way that the csv is formed
# Which was okay for them peeps

# XXX: file name is always 'download' and it should probably be set per-view
class XlsRenderer(BaseRenderer):
    media_type = 'application/vnd.ms-excel'
    results_field = 'results'
    format = 'xls'

    def __init__(self):
        self.wb = None
        self.ws = None
        self.header_style = None
        self.cell_style = None
        self.column_width = 0
        # We have the column number here,
        # because it's a much easier and tidier way
        # To have it as a class variable,
        # because of the way the columns need to be formed
        # and because of recursiveness
        self.column_number = 0
        # Cause each column might have different widths,
        # and we need to store each columns widths
        # In an array to make checks if a longer values has not entered
        self.col_widths = []

    def render(self, data, *args, **kwargs):

        actual_kwargs = args[1].get('kwargs', {})

        # this is a list view
        if 'pk' not in actual_kwargs:
            data = data.get(self.results_field, [])

        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()

        # Even though the final file will be in memory the module uses temp
        # files during assembly for efficiency. To avoid this on servers that
        # don't allow temp files, for example the Google APP Engine, set the
        # 'in_memory' Workbook() constructor option as shown in the docs.
        self.wb = xlsxwriter.Workbook(output)

        self.header_style = self.wb.add_format({
            'bold': True,
        })

        self.ws = self.wb.add_worksheet('Data Sheet')

        self._write_to_excel(data)

        # Close the workbook before sending the data.
        self.wb.close()

        # Rewind the buffer.
        output.seek(0)

        return output

    def _write_to_excel(self, data):
        if type(data) is ReturnList or type(data) is list \
                or type(data) is OrderedDict:
            # So if the initial data, is a list, that means that
            # We can create a seperate row for each item
            for i, item in enumerate(data):
                # + 1 cause first row is reserved for the header
                row_numb = i + 1
                # Need to reset the column_number
                # each time a new row is being written
                self.column_number = 0
                self._write_this(item, '', row_numb)
        elif type(data) is ReturnDict or type(data) is dict:
            # Otherwise, it doesn't make sense to create rows
            self._write_this(data)

    def _write_this(self, data, col_name='', row_numb=1):

        divider = '.' if col_name != '' else ''
        if type(data) is ReturnList or type(data) is list:
            for i, item in enumerate(data):
                column_name = col_name + divider + str(i)
                self._write_this(item, column_name, row_numb)
        elif type(data) is ReturnDict or type(data) is dict \
                or type(data) is OrderedDict:
            for key, value in data.items():
                column_name = col_name + divider + key
                self._write_this(value, column_name, row_numb)
        else:
            # If it goes in here that means that it is an actual value
            # with a column name, so we right the actual thing here
            if row_numb > 1:
                # And if the row number is more
                # then one, that means that we don't need
                # to add the header anymore
                # And tis the cell, data is the value of the actual item
                self.ws.write(row_numb, self.column_number,
                              data, self.cell_style)
            else:
                # Here we write the header, in the first row(row == 0)
                # col_name is the properly formed col_name
                # after recursively going
                # through each item thats why we don't modify it
                self.ws.write(0, self.column_number, col_name,
                              self.header_style)
                # And tis the cell, data is the value of the actual item
                self.ws.write(row_numb, self.column_number,
                              data, self.cell_style)

            # We set the column width according to the
            # length of the data/value or the header if its longer
            width = len(str(data)) if len(str(data)) > len(col_name) \
                else len(col_name)
            # And we check here if the previously set
            # width for the is bigger than this
            try:
                if width > self.col_widths[self.column_number]:
                    self.col_widths[self.column_number] = width
                width = self.col_widths[self.column_number]
            except IndexError:
                self.col_widths.append(width)

            self.ws.set_column(self.column_number, self.column_number, width)
            # Everytime we add a value we increase the column number
            self.column_number += 1
