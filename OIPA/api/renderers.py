#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ast
import unicodecsv as csv
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

from api.iati.references import (
    ActivityDateReference, ActivityScopeReference, ActivityStatusReference,
    BudgetReference, CapitalSpendReference, CollaborationTypeReference,
    ConditionsReference, ContactInfoReference, CountryBudgetItemsReference,
    CrsAddReference, DefaultFinanceTypeReference, DefaultFlowTypeReference,
    DefaultTiedStatusReference, DescriptionReference, DocumentLinkReference,
    FssReference, HumanitarianScopeReference, LegacyDataReference,
    LocationReference, OtherIdentifierReference, ParticipatingOrgReference,
    PlannedDisbursementReference, PolicyMarkerReference,
    RecipientCountryReference, RecipientRegionReference,
    RelatedActivityReference, ReportingOrgReference, ResultReference,
    SectorReference, TagReference, TitleReference, TransactionReference
)

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


# TODO: test this, see: #958
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
        #
        self.rows = []
        self.row = []
        self.paths = {}
        self.headers = {}
        self.break_down_by = None
        self.exceptional_fields = None

    def render(self, data, *args, **kwargs):
        # TODO: this is probably a bug in DRF, might get fixed later then
        # need to update this - 2017-04-03
        actual_kwargs = args[1].get('kwargs', {})

        # So basically when exporting a list view we need to only
        # parse what we get from the 'results' field of the response
        # otherwise what we see in the file, will not make much sense
        # so we do a check here to determine if the response is a list
        # response or a detail response, by checking if there's a
        # 'pk' or a 'iati_identifier'
        # one of the exceptions is for the 'activity/{id}/transactions'
        # because it returns a list so we have a check for it here as well
        if 'pk' not in actual_kwargs \
            and 'iati_identifier' not in actual_kwargs or \
            'pk' in actual_kwargs and \
                'transactions' in args[1]['request']._request.path:
            data = data.get(self.results_field, [])

        # these lines is just for internal testing purposes
        # to transforms current json object
        # into format suitable for testing majority of cases.
        # data[0]['transaction_types'].append({'transaction_type':'12', 'dsum': 300000.00}) # NOQA: E501
        # data[0]['recipient_countries'].append({'id': 5, 'country': {'url': 'test url', 'code': 'IQ', 'name': 'test name'}, 'percentage': 50}) # NOQA: E501

        # Get the reference view
        view = args[1].get('view', {})

        # Check if it's the instance of view type
        if not isinstance(view, dict):

            # for exceptional fields we should perform different logic
            # then for other selectable fields
            self.exceptional_fields = view.exceptional_fields

            # Get headers with their paths
            self.headers = self._get_headers(view.csv_headers, view.fields)

            # Break down Activity by defined column in ActivityList class
            self.break_down_by = view.break_down_by

            # iterate trough all Activities
            for item in data:

                # Get a number of repeated rows caused by breaking down
                # activity with the defined column.
                repeated_rows = len(item[self.break_down_by])

                self.paths = {}
                # recursive function to get all json paths
                # together with the corresponded values
                self.paths = self._go_deeper(item, '', self.paths)

                self.adjust_paths()

                # iterate trough activity data and make appropriate row values
                # with the respect to the headers and breaking down column
                for i in range(repeated_rows):
                    self.row = []
                    for header_key, header_value in self.headers.items():
                        # in case that we did not find the value
                        # for the particular json path, set empty string
                        # for the column value.
                        if header_value not in list(self.paths.keys()):
                            self.row.append('')
                            continue
                        else:
                            value = self.paths[header_value]
                            if isinstance(value, list):
                                if self.break_down_by in header_value:
                                    self.row.append(value[i])
                                else:
                                    self.row.append(';'. join(value))

                            # In case we did find the value for the particular
                            # json path and this property value has not related
                            # to breaking down column.
                            else:
                                self.row.append(value)
                    self.rows.append(self.row)

        # writing to the csv file using unicodecsv library
        output = io.BytesIO()
        writer = csv.writer(output, delimiter=';', encoding=settings.DEFAULT_CHARSET)  # NOQA: E501
        writer.writerow(list(self.headers.keys()))
        writer.writerows(self.rows)
        return output.getvalue()
        # this is old render call.
        # return super(PaginatedCSVRenderer, self).render(rows, renderer_context={'header':['aaaa','sssss','ddddd','fffff','gggggg']}, **kwargs) # NOQA: E501

    def _go_deeper(self, node, path='', paths={}):

        if isinstance(node, dict):
            for key, value in node.items():
                current_path = path + key + '.'
                paths = self._go_deeper(value, current_path, paths)

        elif isinstance(node, list):
            for value in node:
                paths = self._go_deeper(value, path, paths)
        else:
            path = path[:-1]
            if path in paths:
                if not isinstance(paths[path], list):
                    paths[path] = [paths[path]]
                    paths[path].append(0 if node is None else node)
            else:
                paths[path] = 0 if node is None else node

        return paths

    def _get_headers(self, available_headers, fields):

        headers = {}
        for field in fields:
            for header, path in available_headers.items():
                # field name should be first term in path string
                if field in path.split('.')[0]:
                    headers[header] = path

        # adjust headers with the possibility of having exceptional fields
        for exceptional_field in self.exceptional_fields:
            for key, value in exceptional_field.items():
                field_name = key.split('.')[0]
                if field_name in list(headers.keys()):
                    path = headers[field_name]
                    headers.pop(field_name, None)
                    for exceptional_header_suffix in value:
                        headers[field_name + '_' + str(exceptional_header_suffix)] = path + '_' + str(exceptional_header_suffix)  # NOQA: E501

        return headers

    def adjust_paths(self):

        for exceptional_field in self.exceptional_fields:
            tmp_paths = {}
            for key, value in exceptional_field.items():
                if key in self.paths:
                    field_name = key.split('.')[0]
                    if not isinstance(self.paths[key], list):

                        field_value = self.paths[key]
                        tmp_paths = self._make_column_value(tmp_paths, field_name, field_value, None)  # NOQA: E501

                    else:
                        for index, item in enumerate(self.paths[key]):
                            field_value = item
                            tmp_paths = self._make_column_value(tmp_paths, field_name, field_value, index)  # NOQA: E501

            self.paths = tmp_paths

    def _make_column_value(self, data, field_name, field_value, index=None):
        for path, path_value in self.paths.items():
            if field_name in path.split('.')[0]:
                data[path + '_' + str(field_value)] = \
                    path_value[index] if index is not None else path_value
            else:
                data[path] = path_value
        return data


class OrganisationXMLRenderer(XMLRenderer):
    root_tag_name = 'iati-organisations'
    item_tag_name = 'iati-organisation'


# XXX: file name is always 'download' and it should probably be set per-view
# TODO: test this, see: #958
class XlsRenderer(BaseRenderer):
    media_type = 'application/vnd.ms-excel'
    results_field = 'results'
    render_style = 'xls'
    format = 'xls'

    def __init__(self):
        self.wb = None
        self.ws = None
        self.header_style = None
        self.cell_style = None
        self.column_width = 0
        self.requested_fields = None

        # So we gonna store the columns seperately
        # Index is the column number, value the column name
        self.columns = []

        # Then we gonna store the cells seperately,
        # in a weird dictionary matrix thingy
        self.cells = {}

        # Cause each column might have different widths,
        # and we need to store each columns widths
        # In an array to make checks if a longer values has not entered
        self.col_widths = []

        # Saves the previous column name
        # This is used for aditional column values that might not be found
        # in the first item of the results
        self.prev_col_name = False

    def render(self, data, media_type=None, renderer_context=None):
        try:
            self.requested_fields = ast.literal_eval(
                renderer_context['request'].query_params['export_fields'])
        except KeyError:
            pass

        actual_kwargs = renderer_context.get('kwargs', {})

        # So basically when exporting a list view we need to only
        # parse what we get from the 'results' field of the response
        # otherwise what we see in the file, will not make much sense
        # so we do a check here to determine if the response is a list
        # response or a detail response, by checking if there's a
        # 'pk' or a 'iati_identifier'
        # one of the exceptions is for the 'activity/{id}/transactions'
        # because it returns a list so we have a check for it here as well
        if 'pk' not in actual_kwargs \
                and 'iati_identifier' not in actual_kwargs or\
                'pk' in actual_kwargs and \
                'transactions' in renderer_context['request']._request.path:
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
            # We can create a seperate row for each item.
            #
            # So first we write the columns,
            # cause we need to form the appropriate columns
            # for all the possible values,
            # for each result item
            # this is needed to be done seperatly for results,
            # because some results
            # might have more values than others == more values
            # in their arrays and etc.
            for item in data:
                self._store_columns(item)

            # And here we form the cell matrix according to the saved columns
            # and the row number
            for i, item in enumerate(data):
                # + 1 cause first row is reserved for the header
                row_numb = i + 1
                self._store_cells(item, '', row_numb)
        elif type(data) is ReturnDict or type(data) is dict:
            # Here we do the same as above just without for loops
            # cause if it goes in here, it is most likely detail data
            self._store_columns(data)
            self._store_cells(data)

        self._write_data(data)

    def _store_columns(self, data, col_name=''):
        divider = '.' if col_name != '' else ''
        if type(data) is ReturnList or type(data) is list:
            for i, item in enumerate(data):
                column_name = col_name + divider + str(i)
                self._store_columns(item, column_name)
        elif type(data) is ReturnDict or type(data) is dict \
                or type(data) is OrderedDict:
            for key, value in data.items():
                column_name = col_name + divider + key
                self._store_columns(value, column_name)
        else:
            try:
                # this is here just as a check,
                # to make this try except work as expected
                self.columns.index(col_name)
                self.prev_col_name = col_name
            except ValueError:

                if self.requested_fields:
                    # We check if the formed column
                    # is one of the requested fields
                    try:
                        self.requested_fields[col_name]
                        # if it is we continue with the storing of the column
                    except KeyError:
                        # if it isn't we return the this recursive method
                        # thus skipping the below code,
                        # where the column header is stored
                        return

                if self.prev_col_name:
                    # So this part of the if is mainly
                    # used to store column header names,
                    # that were not available in the previous result items,
                    # into there appropriate place
                    index = self.columns.index(self.prev_col_name) + 1
                    self.columns.insert(index, col_name)
                    self.prev_col_name = col_name
                else:
                    # This is used only to store the column header names
                    # formed from the initial result item
                    self.columns.append(col_name)

    def _store_cells(self, data, col_name='', row_numb=1):
        divider = '.' if col_name != '' else ''
        if type(data) is ReturnList or type(data) is list:
            for i, item in enumerate(data):
                column_name = col_name + divider + str(i)
                self._store_cells(item, column_name, row_numb)
        elif type(data) is ReturnDict or type(data) is dict \
                or type(data) is OrderedDict:
            for key, value in data.items():
                column_name = col_name + divider + key
                self._store_cells(value, column_name, row_numb)
        else:
            # So if we go in here the data is the actual value of the cell
            # and so here we store the actual cell
            # and we give this cell matrix/dictionary appropriate
            # indexes according to the row_number
            # and its appropriate column name
            try:
                self.cells[(row_numb, self.columns.index(col_name))] = data
            except ValueError:
                # so if the index for the columns does not exist it means that
                # it is not a requested field and thus we skip it
                pass

    def _write_data(self, data):
        # write column headers
        for ind, header in enumerate(self.columns):
            if self.requested_fields:
                self.ws.write(0, ind, self.requested_fields[header],
                              self.header_style)
            else:
                self.ws.write(0, ind, header, self.header_style)

        # write cells
        for i in range(len(data)):
            # Cause we already wrote the column headers
            row_numb = i + 1
            for col_numb, header in enumerate(self.columns):
                # so as described in some comments above
                # sometimes some cells
                # will not have some values for some columns
                # so we just pass these cell values and dont write them
                try:
                    cell_value = self.cells[(row_numb, col_numb)]
                    self.ws.write(row_numb, col_numb, cell_value,
                                  self.cell_style)

                    # We set the column width according to the
                    # length of the data/value or the header if its longer
                    width = len(str(cell_value)) if \
                        len(str(cell_value)) > len(header) \
                        else len(header)
                    # And we check here if the previously set
                    # width for the is bigger than this
                    try:
                        if width > self.col_widths[col_numb]:
                            self.col_widths[col_numb] = width
                        width = self.col_widths[col_numb]
                    except IndexError:
                        self.col_widths.append(width)

                    self.ws.set_column(col_numb, col_numb, width)

                except KeyError:
                    pass


class IATIXMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = 'application/xml'
    format = 'xml'
    charset = 'UTF-8'
    root_tag_name = 'iati-activities'
    item_tag_name = 'iati-activity'
    version = '2.03'

    default_references = {
        'iati_identifier': None,
    }

    element_references = {
        'title': TitleReference,
        'descriptions': DescriptionReference,
        'activity_dates': ActivityDateReference,
        'reporting_organisation': ReportingOrgReference,
        'participating_organisations': ParticipatingOrgReference,
        'contact_info': ContactInfoReference,
        'activity_scope': ActivityScopeReference,
        'related_transactions': TransactionReference,
        'sectors': SectorReference,
        'budgets': BudgetReference,
        'other_identifier': OtherIdentifierReference,
        'activity_status': ActivityStatusReference,
        'recipient_countries': RecipientCountryReference,
        'recipient_regions': RecipientRegionReference,
        'locations': LocationReference,
        'policy_markers': PolicyMarkerReference,
        'collaboration_type': CollaborationTypeReference,
        'default_flow_type': DefaultFlowTypeReference,
        'default_finance_type': DefaultFinanceTypeReference,
        'default_tied_status': DefaultTiedStatusReference,
        'planned_disbursements': PlannedDisbursementReference,
        'capital_spend': CapitalSpendReference,
        'document_links': DocumentLinkReference,
        'legacy_data': LegacyDataReference,
        'crs_add': CrsAddReference,
        'results': ResultReference,
        'fss': FssReference,
        'humanitarian_scope': HumanitarianScopeReference,
        'related_activities': RelatedActivityReference,
        'conditions': ConditionsReference,
        'country_budget_items': CountryBudgetItemsReference,
        'tags': TagReference
    }

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
                # Tag references
                if parent_name in self.element_references:
                    element = self.element_references[parent_name](
                        parent_element=xml,
                        data=item
                    )
                    element.create()
                else:
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

                if key in attributes or key not in {**self.element_references, **self.default_references}:  # NOQA: E501
                    # TODO: we have some bugs data here,
                    # I don't know where they come from please check them.
                    # How to produce it:
                    # - run debugging
                    # - stop debug line on below "continue"
                    # - check key and value you should get some OrderDict
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

                    # Tag references
                    if key in self.element_references:
                        element = self.element_references[key](
                            parent_element=xml,
                            data=value
                        )
                        element.create()
                    else:
                        self._to_xml(etree.SubElement(
                            xml, key.replace('_', '-')), value)

        elif data is None:
            pass

        else:
            xml.text = six.text_type(data)
            pass
