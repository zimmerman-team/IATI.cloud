import datetime

from django.test import TestCase as DjangoTestCase
from lxml.builder import E

from iati.factory import iati_factory
from iati.parser.exceptions import (
    FieldValidationError, ParserError, RequiredFieldError
)
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


class OrganisationsOrganisationReportingOrganisationTestCase(DjangoTestCase):
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
        self.organisation_type = codelist_factory.OrganisationTypeFactory()
        self.organisation = iati_factory.OrganisationFactory()
        self.organisation_parser_203.register_model(
            "Organisation", self.organisation)

    def test_iati_organisations__iati_organisation__reporting_org(self):
        # case 1 : child element 'narrative' is missing.
        reporting_org_attribute = {"ref": "AA-AAA-123",
                                   "type": "40",
                                   "secondary-reporter": "1"}
        reporting_org_XML_element = E("reporting-org",
                                      # E("narrative", "text"),
                                      **reporting_org_attribute)
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__reporting_org(
                    reporting_org_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("narrative", inst.field)
            self.assertEqual("must occur at least once.", inst.message)

        # case 2: when "ref" is missing.
        reporting_org_attribute = {  # "ref": "AA-AAA-123",
                                   "type": "40",
                                   "secondary-reporter": "1"}
        reporting_org_XML_element = E("reporting-org",
                                      E("narrative", "text"),
                                      **reporting_org_attribute)
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__reporting_org(
                    reporting_org_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("ref", inst.field)
            self.assertEqual("required field missing.", inst.message)

        # case 3: when "type" is missing.
        reporting_org_attribute = {"ref": "AA-AAA-123",
                                   # "type": "40",
                                   "secondary-reporter": "1"}
        reporting_org_XML_element = E("reporting-org",
                                      E("narrative", "text"),
                                      **reporting_org_attribute)
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__reporting_org(
                    reporting_org_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("type", inst.field)
            self.assertEqual("required field missing.", inst.message)

        # case 4: when "type" is not in the codelist.
        reporting_org_attribute = {"ref": "AA-AAA-123",
                                   "type": "409999",
                                   "secondary-reporter": "1"}
        reporting_org_XML_element = E("reporting-org",
                                      E("narrative", "text"),
                                      **reporting_org_attribute)
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__reporting_org(
                    reporting_org_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("type", inst.field)
            self.assertEqual("not found on the accompanying codelist.",
                             inst.message)

        # case 5: when all is ok.
        reporting_org_attribute = {"ref": "AA-AAA-123",
                                   "type": "10",
                                   "secondary-reporter": "1"}
        reporting_org_XML_element = E("reporting-org",
                                      E("narrative", "text"),
                                      **reporting_org_attribute)

        self.organisation_parser_203\
            .iati_organisations__iati_organisation__reporting_org(
                reporting_org_XML_element)

        # get the "reporting_org" object to check its related fields.
        reporting_org = self.organisation_parser_203.get_model(
            "OrganisationReportingOrganisation")

        self.assertEqual(reporting_org_XML_element.attrib.get("ref"),
                         reporting_org.reporting_org_identifier)
        self.assertEqual(self.organisation, reporting_org.organisation)
        self.assertEqual(self.organisation_type, reporting_org.org_type)
        self.assertTrue(reporting_org.secondary_reporter)

        # case 6: when 'reporting-org' element occurs more than once in its
        # parent element, which is 'organisation'.
        reporting_org_XML_element = E("reporting-org",
                                      E("narrative", "text"),
                                      **reporting_org_attribute)
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__reporting_org(
                    reporting_org_XML_element)
        except ParserError as inst:
            self.assertEqual("OrganisationReportingOrganisation", inst.field)
            self.assertEqual("must occur no more than once.", inst.message)


class OrganisationsOrganisationTotalBudgetTestCase(DjangoTestCase):
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
        self.budget_status = codelist_factory.BudgetStatusFactory()
        self.currency = codelist_factory.CurrencyFactory()

    def test_organisations_organisation_total_budget(self):
        # case 1: "status" is not in the codelist.
        total_budget_attrib = {
            "status": "2000",
        }
        total_budget_XML_element = E(
            "total-budget",
            E("period-start", {"iso-date": "2014-04-06"}),
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "3000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **total_budget_attrib
        )
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__total_budget(
                    total_budget_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("status", inst.field)
            self.assertEqual("not found on the accompanying codelist.",
                             inst.message)

        # case 2: when "period-start" element is missing.
        total_budget_attrib = {
            "status": "1",
        }
        total_budget_XML_element = E(
            "total-budget",
            # E("period-start", {"iso-date": "2014-04-06"}),
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "2000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **total_budget_attrib
        )
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__total_budget(
                    total_budget_XML_element)
        except ParserError as inst:
            self.assertEqual("period-start", inst.field)
            self.assertEqual("must occur once and only once.", inst.message)

        # case 3: when "period-start" element is present but "iso-date"
        # attribute is absent.
        total_budget_attrib = {
            "status": "1",
        }
        total_budget_XML_element = E(
            "total-budget",
            E("period-start", {}),  # iso-date is missing.
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "4000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **total_budget_attrib
        )
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__total_budget(
                    total_budget_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("iso-date", inst.field)
            self.assertEqual("required field missing.", inst.message)

        # case 4: "iso-date"in "period-start"element is not in the correct
        # range.
        total_budget_attrib = {
            "status": "1",
        }
        total_budget_XML_element = E(
            "total-budget",
            E("period-start", {"iso-date": "1000-03-05"}),  # not in range.
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "4999", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **total_budget_attrib
        )
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__total_budget(
                    total_budget_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("iso-date", inst.field)
            self.assertEqual("is not in correct range.", inst.message)

        # case 5: when "period-end" element is missing.
        total_budget_attrib = {
            "status": "1",
        }
        total_budget_XML_element = E(
            "total-budget",
            E("period-start", {"iso-date": "2014-04-06"}),
            # E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "3000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **total_budget_attrib
        )
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__total_budget(
                    total_budget_XML_element)
        except ParserError as inst:
            self.assertEqual("period-end", inst.field)
            self.assertEqual("must occur once and only once.", inst.message)

        # case 6: when "period-end" element is present but "iso-date"attrib
        # is missing.
        total_budget_attrib = {
            "status": "1",
        }
        total_budget_XML_element = E(
            "total-budget",
            E("period-start", {"iso-date": "2013-04-02"}),
            E("period-end", {}),  # iso-date is missing.
            E("value", "3999", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **total_budget_attrib
        )
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__total_budget(
                    total_budget_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("iso-date", inst.field)
            self.assertEqual("required field missing.", inst.message)

        # case 7: when "iso-date"is not in the correct range.
        total_budget_attrib = {
            "status": "1",
        }
        total_budget_XML_element = E(
            "total-budget",
            E("period-start", {"iso-date": "2013-03-05"}),
            E("period-end", {"iso-date": "1000-03-05"}),  # not in range.
            E("value", "3000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **total_budget_attrib
        )
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__total_budget(
                    total_budget_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("iso-date", inst.field)
            self.assertEqual("is not in correct range.", inst.message)

        # case 8: "value"element occurs more than once.
        total_budget_attrib = {
            "status": "1",
        }
        total_budget_XML_element = E(
            "total-budget",
            E("period-start", {"iso-date": "2013-04-02"}),
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "3999", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            E("value", "2000", {"currency": "EUR", "value-date":
                                "2013-03-04"}),
            **total_budget_attrib
        )

        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__total_budget(
                    total_budget_XML_element)
        except ParserError as inst:
            self.assertEqual("value", inst.field)
            self.assertEqual("must occur once and only once.", inst.message)

        # case 9: when "currency" is not in the codelist.
        total_budget_attrib = {
            "status": "1",
        }
        total_budget_XML_element = E(
            "total-budget",
            E("period-start", {"iso-date": "2013-04-02"}),
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "3999", {"currency": "MMK", "value-date":
                                "2013-03-04"}),
            **total_budget_attrib
        )

        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__total_budget(
                    total_budget_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("currency", inst.field)
            self.assertEqual("not found on the accompanying codelist.",
                             inst.message)

        # case 10: "value-date"attirbute is absent.
        total_budget_attrib = {
            "status": "1",
        }
        total_budget_XML_element = E(
            "total-budget",
            E("period-start", {"iso-date": "2013-04-02"}),
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "3999", {"currency": "USD", }),  # value-date is
            # absent.
            **total_budget_attrib
        )

        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__total_budget(
                    total_budget_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("value-date", inst.field)
            self.assertEqual("required field missing.",
                             inst.message)

        # case 11: "value-date"is not in the correct range.
        total_budget_attrib = {
            "status": "1",
        }
        total_budget_XML_element = E(
            "total-budget",
            E("period-start", {"iso-date": "2013-03-05"}),
            E("period-end", {"iso-date": "2012-03-05"}),
            E("value", "3000", {"currency": "USD", "value-date":
                                "5000-03-04"}),  # is not in correct range.
            **total_budget_attrib
        )
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__total_budget(
                    total_budget_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("value-date", inst.field)
            self.assertEqual("not in the correct range.", inst.message)

        # case 12: when all is good.
        total_budget_attrib = {
            "status": "1",
        }
        total_budget_XML_element = E(
            "total-budget",
            E("period-start", {"iso-date": "2013-03-05"}),
            E("period-end", {"iso-date": "2012-03-05"}),
            E("value", "3000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **total_budget_attrib
        )
        self.organisation_parser_203\
            .iati_organisations__iati_organisation__total_budget(
                total_budget_XML_element)

        # get "TotalBudget" object to check its fields.

        total_budget = self.organisation_parser_203.get_model("TotalBudget")
        period_start_date = self.organisation_parser_203.validate_date(
            "2013-03-05")
        period_end_date = self.organisation_parser_203.validate_date(
            "2012-03-05")
        value = 3000
        value_date = self.organisation_parser_203.validate_date("2013-03-04")

        # checking.

        self.assertEqual(self.organisation, total_budget.organisation)
        self.assertEqual(self.budget_status, total_budget.status)
        self.assertEqual(period_start_date, total_budget.period_start)
        self.assertEqual(period_end_date, total_budget.period_end)
        self.assertEqual(value, total_budget.value)
        self.assertEqual(self.currency, total_budget.currency)
        self.assertEqual(value_date, total_budget.value_date)


class OrganisationsOrganisationTotalBudgetBudgetLineTestCase(DjangoTestCase):

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
        self.total_budget = iati_factory.OrganisationTotalBudgetFactory()
        self.organisation_parser_203.register_model(
            "TotalBudget", self.total_budget)
        self.currency = codelist_factory.CurrencyFactory()

    def test_organisations__organisation__total_budget__budget_line(self):
        # case 1: when "narrative"element is missing.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line",
                                    E("value", "3000", {"currency": "USD",
                                                        "value-date":
                                                            "2015-04-06"}),
                                    # E("narrative", "text"),
                                    **budget_line_attrib)
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__total_budget__budget_line(  # NOQA: E501
                    budget_line_XML_element)
        except ParserError as inst:
            self.assertEqual("narrative", inst.field)
            self.assertEqual("must occur at least once.", inst.message)

        # case 2: when "value"element occurs more than once.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line",
                                    E("value", "2000", {"currency": "USD",
                                                        "value-date":
                                                        "2015-04-06"}),
                                    E("value", "2400", {"currency": "EUR",
                                                        "value-date":
                                                            "2013-10-06"}),
                                    E("narrative", "text"),
                                    **budget_line_attrib)

        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__total_budget__budget_line(  # NOQA: E501
                    budget_line_XML_element)
        except ParserError as inst:
            self.assertEqual("value", inst.field)
            self.assertEqual("must occur once and only once.", inst.message)

        # case 3: when "currency" is not in the codelist.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line",
                                    E("value", "6000", {"currency": "MMK",
                                                        "value-date":
                                                            "2015-04-06"}),
                                    E("narrative", "text"),
                                    **budget_line_attrib)

        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__total_budget__budget_line(  # NOQA: E501
                    budget_line_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("currency", inst.field)
            self.assertEqual("not found on the accompanying codelist.",
                             inst.message)

        # case 4: "value-date"attirbute is absent.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line",
                                    E("value", "8000", {"currency": "USD", }),
                                    E("narrative", "text"),
                                    **budget_line_attrib)

        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__total_budget__budget_line(  # NOQA: E501
                    budget_line_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("value-date", inst.field)
            self.assertEqual("required field missing.",
                             inst.message)

        # case 5: "value-date"is not in the correct range.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line",
                                    E("value", "3000",  {"currency": "USD",
                                                         "value-date":
                                                             "1000-04-06"}),
                                    E("narrative", "text"),
                                    **budget_line_attrib)

        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__total_budget__budget_line(  # NOQA: E501
                    budget_line_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("value-date", inst.field)
            self.assertEqual("not in the correct range.", inst.message)

        # case 6: when all is ok.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line",
                                    E("value", "3000", {"currency": "USD",
                                                        "value-date":
                                                            "2013-04-06"}),
                                    E("narrative", "text"),
                                    **budget_line_attrib)
        self.organisation_parser_203\
            .iati_organisations__iati_organisation__total_budget__budget_line(
                budget_line_XML_element)

        # get "BudgetLine" object to test.
        budget_line = self.organisation_parser_203.get_model("TotalBudgetLine")
        value = 3000
        value_date = self.organisation_parser_203.validate_date("2013-04-06")
        self.assertEqual(self.total_budget, budget_line.total_budget)
        self.assertEqual(budget_line_XML_element.attrib.get("ref"),
                         budget_line.ref)
        self.assertEqual(self.currency, budget_line.currency)
        self.assertEqual(value, budget_line.value)
        self.assertEqual(value_date, budget_line.value_date)


class OrganisationsOrganisationRecipientOrgBudgetTestCase(DjangoTestCase):
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
        self.budget_status = codelist_factory.BudgetStatusFactory()
        self.currency = codelist_factory.CurrencyFactory()

    def test_organisations_organisation_recipient_org_budget(self):
        # case 1: "status" is not in the codelist.
        recipient_org_budget_attrib = {
            "status": "2000",
        }
        recipient_org_budget_XML_element = E(
            "recipient_org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            E("period-start", {"iso-date": "2014-04-06"}),
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "3000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **recipient_org_budget_attrib
        )
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__recipient_org_budget(
                    recipient_org_budget_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("status", inst.field)
            self.assertEqual("not found on the accompanying codelist.",
                             inst.message)

        # case 2: when "period-start" element is missing.
        recipient_org_budget_attrib = {
            "status": "1",
        }
        recipient_org_budget_XML_element = E(
            "recipient-org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            # E("period-start", {"iso-date": "2014-04-06"}),
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "2000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **recipient_org_budget_attrib
        )
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__recipient_org_budget(
                    recipient_org_budget_XML_element)
        except ParserError as inst:
            self.assertEqual("period-start", inst.field)
            self.assertEqual("must occur once and only once.", inst.message)

        # case 3: when "period-start" element is present but "iso-date"
        # attribute is absent.
        recipient_org_budget_attrib = {
            "status": "1",
        }
        recipient_org_budget_XML_element = E(
            "recipient-org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            E("period-start", {}),  # iso-date is missing.
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "4000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **recipient_org_budget_attrib
        )
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__recipient_org_budget(
                    recipient_org_budget_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("iso-date", inst.field)
            self.assertEqual("required field missing.", inst.message)

        # case 4: "iso-date"in "period-start"element is not in the correct
        # range.
        recipient_org_budget_attrib = {
            "status": "1",
        }
        recipient_org_budget_XML_element = E(
            "recipient-org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            E("period-start", {"iso-date": "1000-03-05"}),  # not in range.
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "4999", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **recipient_org_budget_attrib
        )
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__recipient_org_budget(
                    recipient_org_budget_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("iso-date", inst.field)
            self.assertEqual("is not in correct range.", inst.message)

        # case 5: when "period-end" element is missing.
        recipient_org_budget_attrib = {
            "status": "1",
        }
        recipient_org_budget_XML_element = E(
            "recipient-org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            E("period-start", {"iso-date": "2014-04-06"}),
            # E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "3000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **recipient_org_budget_attrib
        )
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__recipient_org_budget(
                    recipient_org_budget_XML_element)
        except ParserError as inst:
            self.assertEqual("period-end", inst.field)
            self.assertEqual("must occur once and only once.", inst.message)

        # case 6: when "period-end" element is present but "iso-date"attrib
        # is missing.
        recipient_org_budget_attrib = {
            "status": "1",
        }
        recipient_org_budget_XML_element = E(
            "recipient-org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            E("period-start", {"iso-date": "2013-04-02"}),
            E("period-end", {}),  # iso-date is missing.
            E("value", "3999", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **recipient_org_budget_attrib
        )
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__recipient_org_budget(
                    recipient_org_budget_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("iso-date", inst.field)
            self.assertEqual("required field missing.", inst.message)

        # case 7: when "iso-date"is not in the correct range.
        recipient_org_budget_attrib = {
            "status": "1",
        }
        recipient_org_budget_XML_element = E(
            "recipient-org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            E("period-start", {"iso-date": "2013-03-05"}),
            E("period-end", {"iso-date": "1000-03-05"}),  # not in range.
            E("value", "3000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **recipient_org_budget_attrib
        )
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__recipient_org_budget(
                    recipient_org_budget_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("iso-date", inst.field)
            self.assertEqual("is not in correct range.", inst.message)

        # case 8: "value"element occurs more than once.
        recipient_org_budget_attrib = {
            "status": "1",
        }
        recipient_org_budget_XML_element = E(
            "recipient-org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            E("period-start", {"iso-date": "2013-04-02"}),
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "3999", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            E("value", "2000", {"currency": "EUR", "value-date":
                                "2013-03-04"}),
            **recipient_org_budget_attrib
        )

        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__recipient_org_budget(
                    recipient_org_budget_XML_element)
        except ParserError as inst:
            self.assertEqual("value", inst.field)
            self.assertEqual("must occur once and only once.", inst.message)

        # case 9: when "currency" is not in the codelist.
        recipient_org_budget_attrib = {
            "status": "1",
        }
        recipient_org_budget_XML_element = E(
            "recipient-org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            E("period-start", {"iso-date": "2013-04-02"}),
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "3999", {"currency": "MMK", "value-date":
                                "2013-03-04"}),
            **recipient_org_budget_attrib
        )

        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__recipient_org_budget(
                    recipient_org_budget_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("currency", inst.field)
            self.assertEqual("not found on the accompanying codelist.",
                             inst.message)

        # case 10: "value-date"attirbute is absent.
        recipient_org_budget_attrib = {
            "status": "1",
        }
        recipient_org_budget_XML_element = E(
            "recipient-org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            E("period-start", {"iso-date": "2013-04-02"}),
            E("period-end", {"iso-date": "2015-03-05"}),
            E("value", "3999", {"currency": "USD", }),  # value-date is
            # absent.
            **recipient_org_budget_attrib
        )

        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__recipient_org_budget(
                    recipient_org_budget_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("value-date", inst.field)
            self.assertEqual("required field missing.",
                             inst.message)

        # case 11: "value-date"is not in the correct range.
        recipient_org_budget_attrib = {
            "status": "1",
        }
        recipient_org_budget_XML_element = E(
            "recipient-org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            E("period-start", {"iso-date": "2013-03-05"}),
            E("period-end", {"iso-date": "2012-03-05"}),
            E("value", "3000", {"currency": "USD", "value-date":
                                "5000-03-04"}),  # is not in correct range.
            **recipient_org_budget_attrib
        )
        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__recipient_org_budget(
                    recipient_org_budget_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("value-date", inst.field)
            self.assertEqual("not in the correct range.", inst.message)

        # case 12: when all is good.
        recipient_org_budget_attrib = {
            "status": "1",
        }
        recipient_org_budget_XML_element = E(
            "recipient-org-budget",
            E("recipient-org", E("narrative", "text"), {"ref": "123"}),
            E("period-start", {"iso-date": "2013-03-05"}),
            E("period-end", {"iso-date": "2012-03-05"}),
            E("value", "3000", {"currency": "USD", "value-date":
                                "2013-03-04"}),
            **recipient_org_budget_attrib
        )
        self.organisation_parser_203\
            .iati_organisations__iati_organisation__recipient_org_budget(
                recipient_org_budget_XML_element)

        # get "TotalBudget" object to check its fields.

        recipient_org_budget = self.organisation_parser_203.get_model(
            "RecipientOrgBudget")
        period_start_date = self.organisation_parser_203.validate_date(
            "2013-03-05")
        period_end_date = self.organisation_parser_203.validate_date(
            "2012-03-05")
        value = 3000
        value_date = self.organisation_parser_203.validate_date("2013-03-04")

        # checking.

        self.assertEqual(self.organisation, recipient_org_budget.organisation)
        self.assertEqual(self.budget_status, recipient_org_budget.status)
        self.assertEqual(period_start_date, recipient_org_budget.period_start)
        self.assertEqual(period_end_date, recipient_org_budget.period_end)
        self.assertEqual(value, recipient_org_budget.value)
        self.assertEqual(self.currency, recipient_org_budget.currency)
        self.assertEqual(value_date, recipient_org_budget.value_date)


class OrganisationsOrganisationRecipientOrgBudgetBudgetLineTestCase(
        DjangoTestCase):

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
        self.recipient_org_budget = \
            iati_factory.OrganisationRecipientOrgBudgetFactory()
        self.organisation_parser_203.register_model(
            "RecipientOrgBudget", self.recipient_org_budget)
        self.currency = codelist_factory.CurrencyFactory()

    def test_organisations__organisation__recipient_org_budget__budget_line(
            self):
        # case 1: when "narrative"element is missing.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line", E("value", "3000",
                                                     {"currency": "USD",
                                                      "value-date":
                                                          "2015-04-06"}),
                                    # E("narrative", "text"),
                                    **budget_line_attrib)
        try:
            self.organisation_parser_203\
                .iati_organisations__iati_organisation__recipient_org_budget__budget_line(  # NOQA: E501
                    budget_line_XML_element)
        except ParserError as inst:
            self.assertEqual("narrative", inst.field)
            self.assertEqual("must occur at least once.", inst.message)

        # case 2: when "value"element occurs more than once.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line",
                                    E("value", "2000", {"currency": "USD",
                                                        "value-date":
                                                        "2015-04-06"}),
                                    E("value", "2400", {"currency": "EUR",
                                                        "value-date":
                                                            "2013-10-06"}),
                                    E("narrative", "text"),
                                    **budget_line_attrib)

        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__recipient_org_budget__budget_line(  # NOQA: E501
                    budget_line_XML_element)
        except ParserError as inst:
            self.assertEqual("value", inst.field)
            self.assertEqual("must occur once and only once.", inst.message)

        # case 3: when "currency" is not in the codelist.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line",
                                    E("value", "6000", {"currency": "MMK",
                                                        "value-date":
                                                            "2015-04-06"}),
                                    E("narrative", "text"),
                                    **budget_line_attrib)

        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__recipient_org_budget__budget_line(  # NOQA: E501
                    budget_line_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("currency", inst.field)
            self.assertEqual("not found on the accompanying codelist.",
                             inst.message)

        # case 4: "value-date"attirbute is absent.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line",
                                    E("value", "8000", {"currency": "USD", }),
                                    E("narrative", "text"),
                                    **budget_line_attrib)

        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__recipient_org_budget__budget_line(  # NOQA: E501
                    budget_line_XML_element)
        except RequiredFieldError as inst:
            self.assertEqual("value-date", inst.field)
            self.assertEqual("required field missing.",
                             inst.message)

        # case 5: "value-date"is not in the correct range.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line",
                                    E("value", "3000",  {"currency": "USD",
                                                         "value-date":
                                                             "1000-04-06"}),
                                    E("narrative", "text"),
                                    **budget_line_attrib)

        try:
            self.organisation_parser_203 \
                .iati_organisations__iati_organisation__recipient_org_budget__budget_line(  # NOQA: E501
                    budget_line_XML_element)
        except FieldValidationError as inst:
            self.assertEqual("value-date", inst.field)
            self.assertEqual("not in the correct range.", inst.message)

        # case 6: when all is ok.
        budget_line_attrib = {
            "ref": "123"
        }
        budget_line_XML_element = E("budget-line",
                                    E("value", "3000", {"currency": "USD",
                                                        "value-date":
                                                            "2013-04-06"}),
                                    E("narrative", "text"),
                                    **budget_line_attrib)
        self.organisation_parser_203\
            .iati_organisations__iati_organisation__recipient_org_budget__budget_line(  # NOQA: E501
                budget_line_XML_element)

        # get "BudgetLine" object to test.
        budget_line = self.organisation_parser_203.get_model(
            "RecipientOrgBudgetLine")
        value = 3000
        value_date = self.organisation_parser_203.validate_date("2013-04-06")
        self.assertEqual(self.recipient_org_budget,
                         budget_line.recipient_org_budget)
        self.assertEqual(budget_line_XML_element.attrib.get("ref"),
                         budget_line.ref)
        self.assertEqual(self.currency, budget_line.currency)
        self.assertEqual(value, budget_line.value)
        self.assertEqual(value_date, budget_line.value_date)
