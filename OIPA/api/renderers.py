#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ast
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

        return super(PaginatedCSVRenderer, self).render(data, *args, **kwargs)


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


class ElementReference(object):
    """
    http://reference.iatistandard.org/203/activity-standard/elements/
    """
    element = None
    parent_element = None
    data = None

    def __init__(self, parent_element, data, element=None):
        self.parent_element = parent_element
        self.data = data

        if element:
            self.element = element

    def create(self):
        pass


class NarrativeReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/title/narrative/
    """
    element = 'narrative'
    text_key = 'text'
    lang_key = 'en'
    language_key = 'language'
    language_code_key = 'code'
    default_language_code = 'en'

    def create(self):
        narrative_element = etree.SubElement(self.parent_element, self.element)
        narrative_element.text = self.data.get(self.text_key)

        language = self.data.get('language')
        if language:
            language_code = language.get(self.language_code_key)
            if language_code not in [self.default_language_code, None]:
                narrative_element.set(
                    '{http://www.w3.org/XML/1998/namespace}lang',
                    language_code
                )


class ElementWithNarrativeReference(ElementReference):
    narrative_element = 'narrative'
    narratives_key = 'narratives'

    def create_narrative(self, parent_element):
        if self.narratives_key in self.data:
            for narrative in self.data.get(self.narratives_key):
                narrative_reference = NarrativeReference(
                    parent_element=parent_element,
                    data=narrative
                )
                narrative_reference.create()

    def create(self):
        self.create_narrative(
            etree.SubElement(self.parent_element, self.element)
        )


class TitleReference(ElementWithNarrativeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/title/
    """
    element = 'title'


class DescriptionReference(ElementWithNarrativeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/description/
    """
    element = 'description'
    description_type_key = 'type'
    attribute_type_name = 'type'

    def create(self):
        description_element = etree.SubElement(
            self.parent_element, self.element
        )

        # Set attribute type
        description_type = self.data.get(self.description_type_key)
        if description_type:
            description_element.set(self.attribute_type_name, description_type)

        self.create_narrative(description_element)


class ActivityDateReference(ElementReference):
    element = 'activity-date'
    iso_date_key = 'iso_date'
    type_key = 'type'
    iso_date_attr = 'iso-date'
    type_attr = 'type'
    type_value_key = 'code'

    def create(self):
        # Only has iso date
        iso_date = self.data.get(self.iso_date_key)
        if iso_date:
            iso_date_element = etree.SubElement(
                self.parent_element, self.element
            )

            # Set attribute iso date
            iso_date_element.set(self.iso_date_attr, iso_date)

            # Set attribute type date
            type_date = self.data.get(self.type_key)
            if type_date:
                # type date is dictionary
                # Reference: ActivityDateSerializer
                type_value = type_date.get(self.type_value_key)
                if type_value:
                    iso_date_element.set(self.type_attr, type_value)


class ReportingOrgReference(ElementWithNarrativeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/reporting-org/
    """
    element = 'reporting-org'
    ref_key = 'ref'
    ref_attr = 'ref'
    type_dict_key = 'type'
    type_value_key = 'code'
    type_attr = 'type'
    secondary_reporter_key = 'secondary_reporter'
    secondary_reporter_attr = 'secondary-reporter'

    def create(self):
        reporting_org_element = etree.SubElement(
            self.parent_element, self.element
        )
        ref_value = self.data.get(self.ref_key)
        if ref_value:
            reporting_org_element.set(self.ref_attr, ref_value)

        type_dict = self.data.get(self.type_dict_key)
        if type_dict:
            type_value = type_dict.get(self.type_value_key)
            if type_value:
                reporting_org_element.set(self.type_attr, type_value)

        secondary_reporter_value = self.data.get(self.secondary_reporter_key)
        if secondary_reporter_value is not None:
            reporting_org_element.set(
                self.secondary_reporter_attr, '1'
                if secondary_reporter_value else '0'
            )

        self.create_narrative(reporting_org_element)


class ParticipatingOrgReference(ElementWithNarrativeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/participating-org/
    """
    element = 'participating-org'
    ref_key = 'ref'
    ref_attr = 'ref'
    type_dict_key = 'type'
    type_value_key = 'code'
    type_attr = 'type'
    role_dict_key = 'role'
    role_key = 'code'
    role_attr = 'role'

    def create(self):
        participating_org_element = etree.SubElement(
            self.parent_element, self.element
        )
        ref_value = self.data.get(self.ref_key)
        if ref_value:
            participating_org_element.set(self.ref_attr, ref_value)

        type_dict = self.data.get(self.type_dict_key)
        if type_dict:
            type_value = type_dict.get(self.type_value_key)
            if type_value:
                participating_org_element.set(self.type_attr, type_value)

        role_dict = self.data.get(self.role_dict_key)
        if role_dict:
            role_value = role_dict.get(self.role_key)
            if role_value:
                participating_org_element.set(self.role_attr, role_value)

        self.create_narrative(participating_org_element)


class ContactInfoReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/contact-info/
    """
    element = 'contact-info'
    # Type attribute
    type_dict_key = 'type'
    type_key = 'code'
    type_attr = 'type'
    # Organisation element
    organisation_dict_key = 'organisation'
    organisation_element = 'organisation'
    # Email element
    email_key = 'email'
    email_element = 'email'
    # Mailing address element
    mailing_address_dict_key = 'mailing_address'
    mailing_address_element = 'mailing-address'
    # Telephone element
    telephone_key = 'telephone'
    telephone_element = 'telephone'
    # Website element
    website_key = 'website'
    website_element = 'website'
    # Department element
    department_dict_key = 'department'
    department_element = 'department'
    # Person name element
    person_name_dict_key = 'person_name'
    person_name_element = 'person-name'
    # Job title element
    job_title_dict_key = 'job_title'
    job_title_element = 'job-title'

    def create(self):
        contact_info_element = etree.SubElement(
            self.parent_element, self.element
        )

        # Type attribute
        type_dict = self.data.get(self.type_dict_key)
        if type_dict:
            type_value = type_dict.get(self.type_key)
            contact_info_element.set(self.type_attr, type_value)

        # Organisation element
        organisation_dict = self.data.get(self.organisation_dict_key)
        if organisation_dict:
            organisation_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=organisation_dict
            )
            organisation_narrative.element = self.organisation_element
            organisation_narrative.create()

        # Email element
        email_value = self.data.get(self.email_key)
        if email_value:
            email_element = etree.SubElement(
                contact_info_element, self.email_element
            )
            email_element.text = email_value

        # Mailing address element
        mailing_address_dict = self.data.get(self.mailing_address_dict_key)
        if mailing_address_dict:
            mailing_address_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=mailing_address_dict
            )
            mailing_address_narrative.element = self.mailing_address_element
            mailing_address_narrative.create()

        # Telephone element
        telephone_value = self.data.get(self.telephone_key)
        if telephone_value:
            telephone_element = etree.SubElement(
                contact_info_element, self.telephone_element
            )
            telephone_element.text = telephone_value

        # Website element
        website_value = self.data.get(self.website_key)
        if website_value:
            website_element = etree.SubElement(
                contact_info_element, self.website_element
            )
            website_element.text = website_value

        # Department element
        department_dict = self.data.get(self.department_dict_key)
        if department_dict:
            department_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=department_dict
            )
            department_narrative.element = self.mailing_address_element
            department_narrative.create()

        # Person name element
        person_name_dict = self.data.get(self.person_name_dict_key)
        if person_name_dict:
            person_name_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=person_name_dict
            )
            person_name_narrative.element = self.person_name_element
            person_name_narrative.create()

        # Job title element
        job_title_dict = self.data.get(self.job_title_dict_key)
        if job_title_dict:
            job_title_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=job_title_dict
            )
            job_title_narrative.element = self.job_title_element
            job_title_narrative.create()


class TransactionReference(ElementReference):
    """
    http://reference.iatistandard.org/202/activity-standard/iati-activities/iati-activity/transaction/
    """
    element = 'transaction'
    # Ref
    ref = {
        'key': 'ref',
        'attr': 'ref'
    }
    # Transaction type
    transaction_type = {
        'element': 'transaction-type',
        'key': 'transaction_type',
        # Attributes
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # Transaction date
    transaction_date = {
        'element': 'transaction-date',
        'key': 'transaction_date',
        'attr': 'iso-date'
    }
    # Value
    value = {
        'element': 'value',
        'key': 'value',
        # Attributes
        'currency': {
            'key': 'currency',
            'code': {
                'key': 'code',
                'attr': 'currency'
            }
        },
        'date': {
            'key': 'value_date',
            'attr': 'value-date'
        }
    }
    # Flow type
    flow_type = {
        'element': 'flow-type',
        'key': 'flow_type',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # Finance type
    finance_type = {
        'element': 'finance-type',
        'key': 'finance_type',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # Aid type
    aid_type = {
        'element': 'aid-type',
        'key': 'aid_type',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # tied_status
    tied_status = {
        'element': 'tied-status',
        'key': 'tied_status',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # Provider Organisation
    provider_organisation = {
        'element': 'provider-org',
        'key': 'provider_organisation',
        # Attributes
        'ref': {
            'key': 'ref',
            'attr': 'ref'
        },
        'provider_activity_id': {
            'key': 'provider_activity_id',
            'attr': 'provider-activity-id'
        },
        'type': {
            'key': 'type',
            'attr': 'type'
        },
        'narratives': {
            'element': 'narrative',
            'key': 'narratives',
        }
    }
    # Recipient country
    recipient_countries = {
        'element': 'recipient-country',
        'key': 'recipient_countries',
        'country': {
            'key': 'country',
            'code': {
                'key': 'code',
                'attr': 'code'
            }
        },
        'percentage': {
            'key': 'percentage',
            'attr': 'percentage'
        }
    }
    # Recipient region
    recipient_regions = {
        'element': 'recipient-region',
        'key': 'recipient_regions',
        'region': {
            'key': 'region',
            'code': {
                'key': 'code',
                'attr': 'code'
            }
        },
        'vocabulary': {
            'key': 'vocabulary',
            'attr': 'vocabulary'
        }
    }
    # Sector
    sectors = {
        'element': 'sector',
        'key': 'sectors',
        'sector': {
            'key': 'sector',
            'code': {
                'key': 'code',
                'attr': 'code'
            },
        },
        'vocabulary': {
            'key': 'vocabulary',
            'code': {
                'key': 'code',
                'attr': 'vocabulary'
            },
        }
    }

    def create(self):
        transaction_element = etree.SubElement(
            self.parent_element, self.element
        )

        # Ref
        ref_value = self.data.get(self.ref.get('key'))
        if ref_value:
            transaction_element.set(self.ref.get('attr'), ref_value)

        # Transaction type
        transaction_dict = self.data.get(
            self.transaction_type.get('key')
        )
        if transaction_dict:
            transaction_type_element = etree.SubElement(
                transaction_element, self.transaction_type.get('element')
            )

            # Transaction type element: code attribute
            code_value = transaction_dict.get(
                self.transaction_type.get('code').get('key')
            )
            if code_value:
                transaction_type_element.set(
                    self.transaction_type.get('code').get('attr'),
                    code_value
                )

        # Transaction date
        transaction_date_value = self.data.get(
            self.transaction_date.get('key')
        )
        if transaction_date_value:
            transaction_date_element = etree.SubElement(
                transaction_element, self.transaction_date.get('element')
            )
            transaction_date_element.set(
                self.transaction_date.get('attr'),
                transaction_date_value
            )

        # Value
        value = self.data.get(self.value.get('key'))
        if value:
            value_element = etree.SubElement(
                transaction_element, self.value.get('element')
            )
            value_element.text = value

            # Attributes
            # Currency
            currency_dict = self.data.get(
                self.value.get('currency').get('key')
            )
            if currency_dict:
                code_value = currency_dict.get(
                    self.value.get('currency').get('code').get('key')
                )
                if code_value:
                    value_element.set(
                        self.value.get('currency').get('code').get('attr'),
                        code_value
                    )

            # Attributes
            # Value date
            value_date = self.data.get(self.value.get('date').get('key'))
            if value_date:
                value_element.set(
                    self.value.get('date').get('attr'),
                    value_date
                )

        # Flow type
        flow_type_dict = self.data.get(
            self.flow_type.get('key')
        )
        if flow_type_dict:
            flow_type_element = etree.SubElement(
                transaction_element, self.flow_type.get('element')
            )

            # Attributes
            # Code
            code = flow_type_dict.get(self.flow_type.get('code').get('key'))
            if code:
                flow_type_element.set(
                    self.flow_type.get('code').get('attr'),
                    code
                )

        # Finance type
        finance_type_dict = self.data.get(
            self.finance_type.get('key')
        )
        if finance_type_dict:
            finance_type_element = etree.SubElement(
                transaction_element, self.finance_type.get('element')
            )

            # Attributes
            # Code
            code = finance_type_dict.get(
                self.finance_type.get('code').get('key')
            )
            if code:
                finance_type_element.set(
                    self.flow_type.get('code').get('attr'),
                    code
                )

        # Aid type
        aid_type_dict = self.data.get(
            self.aid_type.get('key')
        )
        if aid_type_dict:
            aid_type_element = etree.SubElement(
                transaction_element, self.aid_type.get('element')
            )

            # Attributes
            # Code
            code = aid_type_dict.get(
                self.aid_type.get('code').get('key')
            )
            if code:
                aid_type_element.set(
                    self.aid_type.get('code').get('attr'),
                    code
                )

        # Tied status
        tied_status_dict = self.data.get(
            self.tied_status.get('key')
        )
        if tied_status_dict:
            tied_status_element = etree.SubElement(
                transaction_element, self.tied_status.get('element')
            )

            # Attributes
            # Code
            code = tied_status_dict.get(
                self.tied_status.get('code').get('key')
            )
            if code:
                tied_status_element.set(
                    self.tied_status.get('code').get('attr'),
                    code
                )

        # Provider Organisation
        provider_organisation_dict = self.data.get(
            self.provider_organisation.get('key')
        )
        if provider_organisation_dict:
            provider_organisation_element = etree.SubElement(
                transaction_element, self.provider_organisation.get('element')
            )

            # Attributes
            # Ref
            ref_value = provider_organisation_dict.get(
                self.provider_organisation.get('ref').get('key')
            )
            if ref_value:
                provider_organisation_element.set(
                    self.provider_organisation.get('ref').get('attr'),
                    ref_value
                )

            # Attributes
            # Provider activity id
            provider_activity_id_value = provider_organisation_dict.get(
                self.provider_organisation.get(
                    'provider_activity_id'
                ).get('key')
            )
            if provider_activity_id_value:
                provider_organisation_element.set(
                    self.provider_organisation.get(
                        'provider_activity_id'
                    ).get('attr'),
                    provider_activity_id_value
                )

            # Attributes
            # Type
            type_value = provider_organisation_dict.get(
                self.provider_organisation.get('type').get('key')
            )
            if type_value:
                provider_organisation_element.set(
                    self.provider_organisation.get('type').get('attr'),
                    type_value
                )

            # Narrative
            provider_organisation_narrative = ElementWithNarrativeReference(
                parent_element=None,
                data=provider_organisation_dict
            )
            provider_organisation_narrative.create_narrative(
                parent_element=provider_organisation_element
            )

        # Recipient country
        recipient_countries_list = self.data.get(
            self.recipient_countries.get('key')
        )
        if recipient_countries_list:
            for recipient_country in recipient_countries_list:
                recipient_country_element = etree.SubElement(
                    transaction_element,
                    self.recipient_countries.get('element')
                )

                # Attribute
                # Code
                country = recipient_country.get(
                    self.recipient_countries.get('country').get('key')
                )
                if country:
                    code = country.get(
                        self.recipient_countries.get(
                            'country'
                        ).get('code').get('key')
                    )

                    if code:
                        recipient_country_element.set(
                            self.recipient_countries.get(
                                'country'
                            ).get('code').get('attr'),
                            code
                        )

                # Attribute
                # Percentage
                percentage_value = recipient_country.get(
                    self.recipient_countries.get('percentage').get('key')
                )
                if percentage_value:
                    recipient_country_element.set(
                        self.recipient_countries.get('percentage').get('attr'),
                        percentage_value
                    )

        # Recipient region
        recipient_regions_list = self.data.get(
            self.recipient_regions.get('key')
        )
        if recipient_regions_list:
            for recipient_region in recipient_regions_list:
                recipient_region_element = etree.SubElement(
                    transaction_element,
                    self.recipient_regions.get('element')
                )

                # Attribute
                # Code
                region = recipient_region.get(
                    self.recipient_regions.get('region').get('key')
                )
                if region:
                    code = region.get(
                        self.recipient_regions.get(
                            'region'
                        ).get('code').get('key')
                    )

                    if code:
                        recipient_region_element.set(
                            self.recipient_regions.get(
                                'region'
                            ).get('code').get('attr'),
                            code
                        )

                # Attribute
                # Vocabulary
                vocabulary_value = recipient_region.get(
                    self.recipient_countries.get('vocabulary').get('key')
                )
                if vocabulary_value:
                    recipient_region_element.set(
                        self.recipient_regions.get('vocabulary').get('attr'),
                        vocabulary_value
                    )

        # Sector
        sectors_list = self.data.get(
            self.sectors.get('key')
        )
        if sectors_list:
            for sector_dict in sectors_list:
                sector_element = etree.SubElement(
                    transaction_element,
                    self.sectors.get('element')
                )

                # Attribute
                # Code
                sector = sector_dict.get(
                    self.sectors.get('sector').get('key')
                )
                if sector:
                    code = sector.get(
                        self.sectors.get(
                            'sector'
                        ).get('code').get('key')
                    )

                    if code:
                        sector_element.set(
                            self.sectors.get(
                                'sector'
                            ).get('code').get('attr'),
                            code
                        )

                # Attribute
                # Vocabulary
                vocabulary = sector_dict.get(
                    self.sectors.get('vocabulary').get('key')
                )
                if vocabulary:
                    code = vocabulary.get(
                        self.sectors.get(
                            'vocabulary'
                        ).get('code').get('key')
                    )

                    if code:
                        sector_element.set(
                            self.sectors.get(
                                'vocabulary'
                            ).get('code').get('attr'),
                            code
                        )


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

    element_references = {
        'title': TitleReference,
        'descriptions': DescriptionReference,
        'activity_dates': ActivityDateReference,
        'reporting_organisation': ReportingOrgReference,
        'participating_organisations': ParticipatingOrgReference,
        'contact_info': ContactInfoReference,
        'related_transactions': TransactionReference
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
