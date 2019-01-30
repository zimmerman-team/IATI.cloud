from django.conf import settings

from iati.parser.exceptions import ParserError, RequiredFieldError
from iati.parser.iati_parser import IatiParser
from iati_codelists import models as codelist_models
from iati_organisation.models import (
    Organisation, OrganisationDocumentLink, OrganisationName,
    OrganisationNarrative, OrganisationReportingOrganisation,
    RecipientCountryBudget, RecipientOrgBudget, RecipientRegionBudget,
    TotalBudget, TotalExpenditure
)
from iati_organisation.parser import post_save


class Parse(IatiParser):
    """
    # TODO: Cover elements as The IATI Organisation File Standard.
    http://reference.iatistandard.org/203/organisation-standard/overview
    /organisation-file/
    """

    organisation_identifier = ''

    def __init__(self, *args, **kwargs):
        super(Parse, self).__init__(*args, **kwargs)
        self.VERSION = '2.03'

        # default currency
        self.default_currency = None

        # We need a current index to put the current model
        # on the process parse
        self.organisation_document_link_current_index = 0
        self.document_link_title_current_index = 0
        self.document_link_language_current_index = 0
        self.total_budget_current_index = 0
        self.total_budget_line_current_index = 0
        self.total_expenditure_current_index = 0
        self.total_expenditure_line_current_index = 0

    def add_narrative(self, element, parent):
        default_lang = self.default_lang  # set on activity (if set)
        lang = element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang')
        text = element.text

        language = self.get_or_none(codelist_models.Language, code=lang)

        if not language:
            language = default_lang

        if not parent:
            raise ParserError(
                "Unknown",
                "Narrative",
                "parent object must be passed")

        register_name = parent.__class__.__name__ + "Narrative"

        if not language:
            raise RequiredFieldError(
                register_name,
                "xml:lang",
                "must specify xml:lang on iati-organisation or xml:lang on \
                        the element itself")
        if not text:
            raise RequiredFieldError(
                register_name,
                "text",
                "empty narrative")

        narrative = OrganisationNarrative()
        narrative.language = language
        narrative.content = element.text
        # This (instead of narrative.related_object) is required, otherwise
        # related object doesn't get passed to the model_store (memory) and
        # 'update_related()' fails.
        # It should probably be passed to the __init__() ?
        setattr(narrative, '_related_object', parent)

        narrative.organisation = self.get_model('Organisation')

        # TODO: handle this differently (also: breaks tests)
        self.register_model(register_name, narrative)

    def _get_currency_or_raise(self, model_name, currency):
        """
        get default currency if not available for currency-related fields
        """
        if not currency:
            currency = getattr(self.get_model(
                'Organisation'), 'default_currency')
            if not currency:
                raise RequiredFieldError(
                    model_name,
                    "currency",
                    "must specify default-currency on iati-organisation or \
                        as currency on the element itself")

    def iati_organisations__iati_organisation(self, element):
        organisation_identifier = element.xpath('organisation-identifier')
        if len(organisation_identifier) is not 1:
            raise ParserError("Organisation", "organisation-identifier",
                              "must occur once and only once.")
        # Here organisation_identifier is a string.
        organisation_identifier = organisation_identifier[0].text

        if organisation_identifier is None:
            raise RequiredFieldError("Organisation",
                                     "organisation-identifier", "required "
                                                                "field "
                                                                "missing.")
        # Here normalized_organisation_identifier is a string.
        normalized_organisation_identifier = self._normalize(
            organisation_identifier)

        last_updated_datetime = self.validate_date(element.attrib.get(
            "last-updated-datetime"))
        default_lang_code = element.attrib.get(
            '{http://www.w3.org/XML/1998/namespace}lang',
            settings.DEFAULT_LANG)
        if default_lang_code:
            default_lang_code = default_lang_code.lower()

        default_lang = self.get_or_none(
            codelist_models.Language,
            code=default_lang_code
        )
        default_currency = self.get_or_none(
            codelist_models.Currency,
            code=element.attrib.get('default-currency'))

        old_organisation = self.get_or_none(
            Organisation, organisation_identifier=organisation_identifier)
        if old_organisation:
            if old_organisation.last_updated_datetime < last_updated_datetime:

                OrganisationName.objects.filter(
                    organisation=old_organisation).delete()
                OrganisationReportingOrganisation.objects.filter(
                    organisation=old_organisation).delete()
                TotalBudget.objects.filter(
                    organisation=old_organisation).delete()
                RecipientOrgBudget.objects.filter(
                    organisation=old_organisation).delete()
                RecipientCountryBudget.objects.filter(
                    organisation=old_organisation).delete()
                RecipientRegionBudget.objects.filter(
                    organisation=old_organisation).delete()
                TotalExpenditure.objects.filter(
                    organisation=old_organisation).delete()
                OrganisationDocumentLink.objects.filter(
                    organisation=old_organisation).delete()

                organisation = old_organisation
                organisation.organisation_identifier = organisation_identifier
                organisation.normalized_organisation_identifier = \
                    normalized_organisation_identifier
                organisation.last_updated_datetime = last_updated_datetime
                organisation.default_lang = default_lang
                organisation.iati_standard_version_id = self.VERSION
                organisation.default_currency = default_currency

                organisation.published = True
                organisation.ready_to_publish = True
                organisation.modified = True

                self.organisation_identifier = \
                    organisation.organisation_identifier
                self.default_currency = default_currency

                # for later reference
                self.default_lang = default_lang

                self.register_model('Organisation', organisation)

                return element
            else:  # if the current element's date is later than or equal to
                # the existing element's date, do nothing and return.
                return element
        else:
            organisation = Organisation()

            organisation.organisation_identifier = organisation_identifier
            organisation.normalized_organisation_identifier = \
                normalized_organisation_identifier
            organisation.last_updated_datetime = last_updated_datetime
            organisation.default_lang = default_lang
            organisation.iati_standard_version_id = self.VERSION
            organisation.default_currency = default_currency

            organisation.published = True
            organisation.ready_to_publish = True
            organisation.modified = False

            self.organisation_identifier = organisation.organisation_identifier
            self.default_currency = default_currency

            # for later reference
            self.default_lang = default_lang

            self.register_model('Organisation', organisation)

            return element

    def post_save_models(self):
        """Perform all actions that need to happen after a single
        organisation's been parsed."""
        organisation = self.get_model('Organisation')

        if not organisation:
            return False

        post_save.set_activity_reporting_organisation(organisation)
        post_save.set_publisher_fk(organisation)

    def post_save_file(self, xml_source):
        pass

    def post_save_validators(self, dataset):
        pass
