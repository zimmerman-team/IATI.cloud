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

    def __init__(self, parent_element, data):
        self.parent_element = parent_element
        self.data = data

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
        'contact_info': ContactInfoReference
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
