#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ast
import io
from collections import OrderedDict

import unicodecsv as csv
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

        # self.rows = []
        # self.row = []
        # self.paths = {}
        # self.headers = {}
        # self.break_down_by = None
        # self.exceptional_fields = None
        # self.selectable_fields = ()
        # self.default_fields = ()

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

            # Get a view's class name
            view_class_name = type(view).__name__

            # for exceptional fields we should perform different logic
            # then for other selectable fields
            self.exceptional_fields = view.exceptional_fields
            # Get headers with their paths

            # Break down Activity by defined column in ActivityList class
            self.break_down_by = view.break_down_by

            self.selectable_fields = view.selectable_fields

            self.default_fields = list(set(view.fields) - set(self.selectable_fields))

            if view_class_name in ['ActivityList']:

                activity_data = self._adjust_transaction_types(data, 'transaction_types')
                data = activity_data['data']
                selectable_headers = activity_data['selectable_headers']
                if 'selectable_headers' in activity_data:
                    activity_data.pop('selectable_headers', None)

                self._create_rows_headers(data, view.csv_headers, selectable_headers, view.fields, False)

            elif view_class_name in ['TransactionList']:

                transactions_data = self._group_data(data, view, 'iati_identifier', 'transactions')
                if 'selectable_headers' in transactions_data:
                    selectable_headers = transactions_data['selectable_headers']
                    transactions_data.pop('selectable_headers', None)
                self._create_rows_headers(transactions_data.values(), view.csv_headers, selectable_headers, view.fields, True)

            elif view_class_name in ['LocationList']:

                location_data = self._group_data(data, view, 'iati_identifier', 'locations')
                if 'selectable_headers' in location_data:
                    selectable_headers = location_data['selectable_headers']
                    location_data.pop('selectable_headers', None)

                self._create_rows_headers(location_data.values(), view.csv_headers, selectable_headers, view.fields, True)

            elif view_class_name in ['BudgetList']:

                budget_data = self._group_data(data,view, 'iati_identifier', 'budgets')
                if 'selectable_headers' in budget_data:
                    selectable_headers = budget_data['selectable_headers']
                    budget_data.pop('selectable_headers', None)
                self._create_rows_headers(budget_data.values(), view.csv_headers, selectable_headers, view.fields, True)

            elif view_class_name in ['ResultList']:

                result_data = self._group_data(data, view, 'iati_identifier', 'results')
                if 'selectable_headers' in result_data:
                    selectable_headers = result_data['selectable_headers']
                    result_data.pop('selectable_headers', None)
                self._create_rows_headers(result_data.values(), view.csv_headers,selectable_headers, view.fields, True)

        # writing to the csv file using unicodecsv library
        output = io.BytesIO()
        writer = csv.writer(output, delimiter=';', encoding=settings.DEFAULT_CHARSET)  # NOQA: E501
        writer.writerow(list(self.headers.keys()))
        writer.writerows(self.rows)
        return output.getvalue()
        # this is old render call.
        # return super(PaginatedCSVRenderer, self).render(rows, renderer_context={'header':['aaaa','sssss','ddddd','fffff','gggggg']}, **kwargs) # NOQA: E501




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

        self.rows = []
        self.row = []
        self.paths = {}
        self.headers = {}
        self.break_down_by = None
        self.exceptional_fields = None
        self.selectable_fields = ()
        self.default_fields = ()

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

        bold = self.wb.add_format({'bold': 1})

        # Get the reference view
        view = renderer_context.get('view', {})

        # Check if it's the instance of view type
        if not isinstance(view, dict):

            # Get a view's class name
            view_class_name = type(view).__name__

            # for exceptional fields we should perform different logic
            # then for other selectable fields
            self.exceptional_fields = view.exceptional_fields
            # Break down Activity by defined column in ActivityList class
            self.break_down_by = view.break_down_by

            self.selectable_fields = view.selectable_fields

            self.default_fields = list(set(view.fields) - set(self.selectable_fields))

            if view_class_name in ['ActivityList']:

                activity_data = self._adjust_transaction_types(data, 'transaction_types')
                data = activity_data['data']
                selectable_headers = activity_data['selectable_headers']
                activity_data.pop('selectable_headers', None)
                self._create_rows_headers(data, view.csv_headers, selectable_headers, view.fields, False)

            elif view_class_name in ['TransactionList']:

                transactions_data = self._group_data(data, view, 'iati_identifier', 'transactions')
                selectable_headers = transactions_data['selectable_headers']
                transactions_data.pop('selectable_headers', None)
                self._create_rows_headers(transactions_data.values(), view.csv_headers, selectable_headers, view.fields, True)

            elif view_class_name in ['LocationList']:

                location_data = self._group_data(data, view, 'iati_identifier', 'locations')
                selectable_headers = location_data['selectable_headers']
                location_data.pop('selectable_headers', None)
                self._create_rows_headers(location_data.values(), view.csv_headers, selectable_headers, view.fields, True)

            elif view_class_name in ['BudgetList']:

                budget_data = self._group_data(data,view, 'iati_identifier', 'budgets')
                selectable_headers = budget_data['selectable_headers']
                budget_data.pop('selectable_headers', None)
                self._create_rows_headers(budget_data.values(), view.csv_headers, selectable_headers, view.fields, True)

            elif view_class_name in ['ResultList']:

                result_data = self._group_data(data, view, 'iati_identifier', 'results')
                selectable_headers = result_data['selectable_headers']
                result_data.pop('selectable_headers', None)
                self._create_rows_headers(result_data.values(), view.csv_headers,selectable_headers, view.fields, True)

        row_index = 0
        column_width = {}

        for index, header in enumerate(self.headers.keys()):
            self.ws.write(row_index, index, header, bold)
            if index not in column_width:
                column_width[index] = len(header)

        for row in self.rows:
            row_index += 1
            for column_index, header in enumerate(self.headers):
                self.ws.write(row_index, column_index, row[column_index])
                if column_width[column_index] < len(row[column_index]):
                    column_width[column_index] = len(row[column_index])

        for index, width in column_width.items():
            # Adjust the column width.
            self.ws.set_column(index, index, width)

        # self._write_to_excel(data)

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
