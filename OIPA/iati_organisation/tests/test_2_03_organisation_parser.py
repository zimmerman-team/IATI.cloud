
import datetime

from django.test import TestCase as DjangoTestCase
from lxml.builder import E

from iati.factory import iati_factory
from iati.parser.exceptions import ParserError, RequiredFieldError
from iati.parser.parse_manager import ParseManager
from iati_codelists.factory import codelist_factory
from iati_synchroniser.factory import synchroniser_factory


class OrganisationsOrganisationTestCase(DjangoTestCase):
    def setUp(self):
        # 'Main' XML file for instantiating parser:
        xml_file_attrs = {
            "generated-datetime": datetime.datetime.now().isoformat(),
            "version": '2.03',
        }
        self.iati_203_XML_file = E("iati-organisations", **xml_file_attrs)

        dummy_source = synchroniser_factory.DatasetFactory(filetype=2)

        self.organisation_parser_203 = ParseManager(
            dataset=dummy_source,
            root=self.iati_203_XML_file,
        ).get_parser()

        # related orbjects.

        self.default_currency = codelist_factory.CurrencyFactory()
        self.default_language = codelist_factory.LanguageFactory()

    def test_iati_organisations__iati_organisation(self):

        # case 1: organisation-identifier is missing.
        organisation_attribute = {"last-updated-datetime": "2014-09-10",
                                  "{http://www.w3.org/XML/1998/namespace}lang":
                                      "en",
                                  "default-currency": "USD"}
        organisation_XML_element = E("iati-organisation",
                                     # E("organisation-identifier",
                                     # "AA-AAA_123"),
                                     E("name", E("narrative", "text")),
                                     E("reporting-org", E("narrative",
                                                          "text")),
                                     **organisation_attribute)
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation(
                    organisation_XML_element)
        except ParserError as inst:
            self.assertEqual("organisation-identifier", inst.field)
            self.assertEqual("must occur once and only once.", inst.message)

        # case 2: when child element 'name' and 'reporting-org' is missing.
        organisation_XML_element = E("iati-organisation",
                                     E("organisation-identifier",
                                       "AA-AAA_123"),
                                     # E("name", E("narrative", "text")),
                                     # E("reporting-org", E("narrative",
                                     # "text")),
                                     **organisation_attribute)

        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation(
                    organisation_XML_element)
        except ParserError as inst:
            self.assertEqual("name and reporting-org", inst.field)
            self.assertEqual("must occur at least once.", inst.message)

        # case 3: organisation-identifier occurs more than once.
        organisation_XML_element = E("iati_organisation",
                                     E("organisation-identifier",
                                       "AA-AAA-123"),
                                     E("organisation-identifier",
                                       "AA-ABC-123"),
                                     E("name", E("narrative", "text")),
                                     E("reporting-org", E("narrative",
                                                          "text")),
                                     **organisation_attribute)
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation(
                    organisation_XML_element)
        except ParserError as inst:
            self.assertEqual("organisation-identifier", inst.field)
            self.assertEqual("must occur once and only once.", inst.message)

        # case 4: when text in organisation-identifier element is missing.
        organisation_XML_element = E("iati-organisation",
                                     E("organisation-identifier"),  # no text
                                     E("name", E("narrative", "text")),
                                     E("reporting-org", E("narrative",
                                                          "text")),
                                     **organisation_attribute)
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation(
                    organisation_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("organisation-identifier", inst.field)
            self.assertEqual("required field missing.", inst.message)

        # case 5: when all is well.
        organisation_XML_element = E("iati-organisation",
                                     E("organisation-identifier",
                                       "AA-AAA_123"),
                                     E("name", E("narrative", "text")),
                                     E("reporting-org", E("narrative",
                                                          "text")),
                                     **organisation_attribute)
        self.organisation_parser_203.iati_organisations__iati_organisation(
            organisation_XML_element)

        # get organisation back to check related fields are correctly assigned.
        organisation = self.organisation_parser_203.get_model("Organisation")
        organisation_identifier = organisation_XML_element.xpath(
            "organisation-identifier")[0].text
        last_updated_datetime = self.organisation_parser_203.validate_date(
            organisation_XML_element.attrib.get("last-updated-datetime"))

        self.assertEqual(last_updated_datetime,
                         organisation.last_updated_datetime)
        self.assertEqual(self.default_language, organisation.default_lang)
        self.assertEqual(self.default_currency, organisation.default_currency)
        self.assertEqual(organisation_identifier,
                         organisation.organisation_identifier)

        # case 5: when there are more than one organisation.
        organisation.save()

        # case 5.1: when "last-updated-datetime" is earlier than old
        # element's last_updated_datetime.
        new_organisation_attribute = {"last-updated-datetime": "2012-09-10",
                                      "{"
                                      "http://www.w3.org/XML/1998/namespace}lang": "en",  # NOQA: E501
                                      "default-currency": "USD"}
        new_organisation_XML_element = E("iati-organisation",
                                         E("organisation-identifier",
                                           "AA-AAA_123"),
                                         E("name", E("narrative", "text")),
                                         E("reporting-org", E("narrative",
                                                              "text")),
                                         **new_organisation_attribute)
        try:
            self.organisation_parser_203.iati_organisations__iati_organisation(
                new_organisation_XML_element)
        except ParserError as inst:
            self.assertEqual("last-updated-datetime is earlier than old " 
                             "element's last_updated_datetime.", inst.message)

        # case 5.2: when "last-updated-datetime" is more recent than old
        # element's last_updated_datetime.
        new_organisation_attribute = {"last-updated-datetime": "2015-09-10",
                                      "{http://www.w3.org/XML/1998/namespace}lang":  # NOQA: E501
                                          "en",
                                      "default-currency": "USD"}
        new_organisation_XML_element = E("iati-organisation",
                                         E("organisation-identifier",
                                           "AA-AAA_123"),
                                         E("name", E("narrative", "text")),
                                         E("reporting-org", E("narrative",
                                                              "text")),
                                         **new_organisation_attribute)
        self.organisation_parser_203.iati_organisations__iati_organisation(
            new_organisation_XML_element)

        # get the organisation again.
        organisation = self.organisation_parser_203.get_model("Organisation")

        # the parser update the organisation so the last_updated_datetime is
        # the new one.
        last_updated_datetime = self.organisation_parser_203.validate_date(
            new_organisation_XML_element.attrib.get("last-updated-datetime"))

        self.assertEqual(last_updated_datetime,
                         organisation.last_updated_datetime)


class OrganisationsOrganisationNameTestCase(DjangoTestCase):

    def setUp(self):
        # 'Main' XML file for instantiating parser:
        xml_file_attrs = {
            "generated-datetime": datetime.datetime.now().isoformat(),
            "version": '2.03',
        }
        self.iati_203_XML_file = E("iati-organisations", **xml_file_attrs)

        dummy_source = synchroniser_factory.DatasetFactory(filetype=2)

        self.organisation_parser_203 = ParseManager(
            dataset=dummy_source,
            root=self.iati_203_XML_file,
        ).get_parser()

        # related objects.
        self.organisation = iati_factory.OrganisationFactory()
        self.organisation_parser_203.register_model(
            "Organisation", self.organisation)

    def test_iati_organisations__iati_organisation__name(self):
        # case 1 : child element 'narrative' is missing.
        name_attribute = {}
        name_XML_element = E("name",
                             # E("narrative", "text"),
                             **name_attribute)
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__name(name_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("narrative", inst.field)
            self.assertEqual("must occur at least once.", inst.message)

        # case 2: when all is ok.
        name_XML_element = E("name",
                             E("narrative", "text"),
                             **name_attribute)
        self.organisation_parser_203\
            .iati_organisations__iati_organisation__name(name_XML_element)

        # get 'name' back.
        name = self.organisation_parser_203.get_model("OrganisationName")
        self.assertEqual(self.organisation, name.organisation)

        # case 3: when 'name' element occurs more than once in its parent
        # element, which is 'organisation'.
        name_XML_element = E("name",
                             E("narrative", "text"),
                             **name_attribute)
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__name(name_XML_element)
        except ParserError as inst:
            self.assertEqual("OrganisationName", inst.field)
            self.assertEqual("must occur no more than once.", inst.message)
