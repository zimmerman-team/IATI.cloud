
import datetime
import json
import logging
import re
from collections import OrderedDict
from decimal import Decimal, InvalidOperation

import dateutil.parser
import xmltodict
from django.conf import settings
from django.db.models import Model
from django.db.models.fields.related import ForeignKey, OneToOneField
from lxml import etree

from common.util import findnth_occurence_in_string, normalise_unicode_string
from iati.models import NameSpaceElement
from iati.parser.exceptions import (
    FieldValidationError, IgnoredVocabularyError, NoUpdateRequired,
    ParserError, RequiredFieldError, ValidationError
)
from iati_codelists import models as codelist_models
from iati_synchroniser.models import DatasetNote
from solr.datasetnote.tasks import DatasetNoteTaskIndexing

log = logging.getLogger(__name__)


class IatiParser(object):
    # default version
    VERSION = '2.03'

    def __init__(self, root):
        self.logged_functions = []
        self.hints = []
        self.errors = []
        self.parse_start_datetime = datetime.datetime.now()
        self.dataset = None
        self.publisher = None
        self.force_reparse = False
        self.default_lang = settings.DEFAULT_LANG
        # A cache to store codelist items in memory (for each element when
        # parsing).
        # During tests, if a new model with a same name is added to the
        # database, this has to be cleared:
        self.codelist_cache = {}

        # TODO: find a way to simply save in parser functions, and actually
        # commit to db on exit
        self.model_store = OrderedDict()
        self.root = root

    def check_registration_agency_validity(self, element_name, element, ref):
        reg_agency_found = False
        if ref and findnth_occurence_in_string(ref, '-', 1) > -1:
            index = findnth_occurence_in_string(ref, '-', 1)
            reg_agency = self.get_or_none(
                codelist_models.OrganisationRegistrationAgency,
                code=ref[:index]
            )
            if reg_agency:
                reg_agency_found = True

        if not reg_agency_found:
            self.append_error(
                'FieldValidationError',
                element_name,
                "ref",
                "Must be in the format {Registration Agency} - (Registration "
                "Number}",
                element.sourceline,
                ref)

    def get_or_none(self, model, *args, **kwargs):
        code = kwargs.get('code', None)
        if code:
            code = normalise_unicode_string(code)
            try:
                model_cache = self.codelist_cache[model.__name__]
            except KeyError:
                model_cache = model.objects.in_bulk()
                self.codelist_cache[model.__name__] = model_cache
            return model_cache.get(code)

        else:

            try:
                return model.objects.get(*args, **kwargs)
            except model.DoesNotExist:
                return None

    def _get_currency_or_raise(self, model_name, currency):
        """
        get default currency if not available for currency-related fields
        """
        # TODO: this does not invalidate the whole element (budget,
        # transaction, planned disbursement) while it should
        if not currency:
            currency = getattr(self.get_model('Activity'), 'default_currency')
            if not currency:
                raise RequiredFieldError(
                    model_name,
                    "currency",
                    "must specify default-currency on iati-activity or as "
                    "currency on the element itself")

        return currency

    # TODO: test this function! it's used everywhere
    def makeBool(self, text):
        if text == '1' or text == 'true':
            return True
        return False

    def makeBoolNone(self, text):
        if text == '1':
            return True
        elif text == '0':
            return False
        elif text == 'true':
            return True
        elif text == 'false':
            return False

        return None

    def guess_number(self, model_name, number_string):
        # first strip non numeric values, except for -.,
        decimal_string = re.sub(r'[^\d.,-]+', '', number_string)

        try:
            return Decimal(decimal_string)
        except ValueError:
            raise FieldValidationError(
                model_name,
                "value",
                "Must be decimal or integer string")
        except InvalidOperation:
            raise FieldValidationError(
                model_name,
                "value",
                "Must be decimal or integer string")

    def isInt(self, obj):
        try:
            int(obj)
            return True
        except BaseException:
            return False

    def _normalize(self, attr):
        # attr = attr.strip(' \t\n\r').replace(" ", "")
        # attr = re.sub("[/:&',.+]", "-", attr)

        # normalize for use in the API with comma-separated values
        attr = re.sub(",", "COMMA", attr)
        return attr

    def validate_date(self, unvalidated_date):

        if unvalidated_date:
            unvalidated_date = unvalidated_date.strip(' \t\n\rZ')
        else:
            return None

        # check if standard data parser works
        try:
            date = dateutil.parser.parse(unvalidated_date, ignoretz=True)
            if date.year >= 1900 and date.year <= 2100:
                return date
            else:
                return None
        except BaseException:
            raise RequiredFieldError(
                "TO DO",
                "iso-date",
                "Unspecified or invalid. Date should be of type xml:date.")

    def get_primary_name(self, element, primary_name):
        if primary_name:
            lang = element.attrib.get(
                '{http://www.w3.org/XML/1998/namespace}lang',
                self.default_lang)
            if lang == 'en':
                primary_name = element.text
        else:
            primary_name = element.text

        # FIXME: this is hardcoded!
        return primary_name[:255]

    def load_and_parse(self, root):
        self.parse_activities(root)

    def parse_activities(self, root):
        """

        """
        for e in root.getchildren():
            self.model_store = OrderedDict()
            parsed = self.parse(e)
            # only save if the activity is updated

            if parsed:
                self.save_all_models()
                self.post_save_models()

        self.post_save_file(self.dataset)

        if settings.ERROR_LOGS_ENABLED:
            self.post_save_validators(self.dataset)

            # TODO - only delete errors on activities that were updated
            self.dataset.note_count = len(self.errors)
            self.dataset.save()

            DatasetNote.objects.filter(dataset=self.dataset).delete()
            DatasetNote.objects.bulk_create(self.errors)

            DatasetNoteTaskIndexing().run_from_dataset(dataset=self.dataset)

    def post_save_models(self):
        print("override in children")

    def post_save_file(self, dataset):
        print("override in children")

    def append_error(self, error_type, model, field, message,
                     sourceline, variable='', iati_id=None):
        if not settings.ERROR_LOGS_ENABLED:
            return

        # get iati identifier
        iati_identifier = None
        if iati_id:
            iati_identifier = iati_id
        elif self.dataset.filetype == 1:
            activity = self.get_model('Activity')
            if activity and activity.iati_identifier:
                iati_identifier = activity.iati_identifier
            # elif activity:
            #     iati_identifier = activity.id
        else:
            organisation = self.get_model('Organisation')
            if organisation and organisation.organisation_identifier:
                iati_identifier = organisation.organisation_identifier
            # elif organisation:
            #     iati_identifier = organisation.id

        if not iati_identifier and hasattr(self, 'identifier'):
            iati_identifier = self.identifier
        elif not iati_identifier:
            iati_identifier = 'no-identifier'

        if variable:
            variable = str(variable)[0:255]

        note = DatasetNote(
            dataset=self.dataset,
            iati_identifier=iati_identifier,
            model=model,
            field=field,
            message=str(message)[0:255],
            exception_type=error_type,
            line_number=sourceline,
            variable=variable
        )

        self.errors.append(note)

    def parse(self, element):
        """All of the methods from specific parser file (i. e. IATI_2_03.py)
        get called in this method
        """
        if element is None:
            return
        if type(element).__name__ != '_Element':
            return
        if element.tag == etree.Comment:
            return
        if element.prefix is not None:  # checking if the element is a namespace element

            self.attach_namespace_to_model(element)
            pass

        x_path = self.root.getroottree().getpath(element)
        function_name = self.generate_function_name(x_path)

        if hasattr(self, function_name) \
                and callable(getattr(self, function_name)):
            element_method = getattr(self, function_name)

            try:
                element_method(element)
                # here we check if the element has namespaced attribute(s)
                attributes = element.attrib.items()
                dict_attrib = dict(attributes)
                for i in dict_attrib.keys():
                    for namespace_url in element.nsmap.values():
                        if namespace_url in i:
                            namesapce_dict = {i: dict_attrib[i]}
                            self.attach_namespace_to_model(element,
                                                           namesapce_dict)
            except RequiredFieldError as e:
                log.exception(e)
                self.append_error(
                    'RequiredFieldError',
                    e.model,
                    e.field,
                    e.message,
                    element.sourceline,
                    None)
                return
            except FieldValidationError as e:
                log.exception(e)
                self.append_error(
                    'FieldValidationError',
                    e.model,
                    e.field,
                    e.message,
                    element.sourceline,
                    e.variable,
                    e.iati_id)
                return
            except ValidationError as e:
                log.exception(e)
                self.append_error(
                    'FieldValidationError',
                    e.model,
                    e.field,
                    e.message,
                    element.sourceline,
                    None,
                    e.iati_id)
                return
            except IgnoredVocabularyError as e:
                # not implemented, ignore for now
                return
            except ParserError as e:
                log.exception(e)
                self.append_error(
                    'ParserError',
                    'TO DO',
                    'TO DO',
                    e.message,
                    None,
                    element.sourceline)
                return
            except NoUpdateRequired as e:
                # do nothing, go to next activity
                return
            except Exception as e:
                log.exception(e)
                return

        for e in element.getchildren():
            self.parse(e)

        return True

    def generate_function_name(self, xpath):
        function_name = xpath.replace('/', '__')
        function_name = function_name.replace('-', '_')
        function_name = self.remove_brackets(function_name)

        return function_name[2:]

    # TODO: separate these functions in their own data structure
    # - 2015-12-02
    def get_model_list(self, key):
        if key in self.model_store:
            return self.model_store[key]
        return None

    # register last seen model of this type. Is overwritten on later encounters
    def register_model(self, key, model=None):
        if isinstance(key, Model):
            model = key
            key = key.__class__.__name__

        if key in self.model_store:
            self.model_store[key].append(model)
        else:
            self.model_store[key] = [model]

        # The position of the current model on the model store
        return len(self.model_store[key]) - 1

    def get_model(self, key, index=-1):
        if isinstance(key, Model):
            key = key.__class__.__name__

        if key in self.model_store:
            if len(self.model_store[key]) > 0:
                return self.model_store[key][index]
        return None

    def pop_model(self, key):
        if isinstance(key, Model):
            key = key.__class__.__name__

        if key in self.model_store:
            if len(self.model_store[key]) > 0:
                return self.model_store[key].pop()
        return None

    def save_model(self, key, index=-1):
        return self.get_model(key, index).save()

    def update_related(self, model):
        """
        Currently a workaround for foreign key assignment before save
        """
        if model.__class__.__name__ in ("OrganisationNarrative", "Narrative"):
            # This is set in parser (IATI_2_02.py, IATI_2_03.py,
            # organisation_2_02 etc.) files:
            model.related_object = getattr(model, '_related_object')

        for field in model._meta.fields:
            if isinstance(field, (ForeignKey, OneToOneField)):
                setattr(model, field.name, getattr(model, field.name))

    def save_all_models(self):
        # TODO: problem: assigning unsaved model to foreign key results in
        # error because field_id has not been set (see: https://git.io/fbphN)
        for model_list in self.model_store.items():
            for model in model_list[1]:
                try:
                    self.update_related(model)

                    model.save()
                    try:
                        if len(model.namespace) != 0:
                            activity = self.get_model('Activity')
                            for namespace in model.namespace:
                                namespace.parent_element_id = model.pk
                                namespace.activity = activity
                                namespace.save()
                    except AttributeError:
                        pass

                except Exception as e:
                    log.exception(e)
                    pass

    def remove_brackets(self, function_name):
        result = ""
        flag = True
        for c in function_name:
            if c == "[":
                flag = False
            if flag:
                result += c
            if c == "]":
                flag = True
        return result

    def attach_namespace_to_model(self, element, attribute_dict=None):

        function_model_mapping = {
            # flake8: noqa E501
            # activity
            "iati_activities__iati_activity": "Activity",
            "iati_activities__iati_activity__iati_identifier": "Activity",
            "iati_activities__iati_activity__reporting_org": "ActivityReportingOrganisation",
            "iati_activities__iati_activity__participating_org": "ActivityParticipatingOrganisation",
            "iati_activities__iati_activity__title": "Title",
            "iati_activities__iati_activity__description": "Description",
            "iati_activities__iati_activity__other_identifier": "OtherIdentifier",
            "iati_activities__iati_activity__other_identifier__owner_org": "OtherIdentifier",
            "iati_activities__iati_activity__activity_status": "Activity",
            "iati_activities__iati_activity__activity_date": "ActivityDate",
            "iati_activities__iati_activity__contact_info": "ContactInfo",
            "iati_activities__iati_activity__contact_info__organisation": "ContactInfoOrganisation",
            "iati_activities__iati_activity__contact_info__department": "ContactInfoDepartment",
            "iati_activities__iati_activity__contact_info__person_name": "ContactInfoPersonName",
            "iati_activities__iati_activity__contact_info__job_title": "ContactInfoJobTitle",
            "iati_activities__iati_activity__contact_info__telephone": "ContactInfo",
            "iati_activities__iati_activity__contact_info__email": "ContactInfo",
            "iati_activities__iati_activity__contact_info__website": "ContactInfo",
            "iati_activities__iati_activity__contact_info__mailing_address": "ContactInfoMailingAddress",
            "iati_activities__iati_activity__activity_scope": "Activity",
            "iati_activities__iati_activity__recipient_country": "ActivityRecipientCountry",
            "iati_activities__iati_activity__recipient_region": "ActivityRecipientRegion",
            "iati_activities__iati_activity__location": "Location",
            "iati_activities__iati_activity__location__location_reach": "Location",
            "iati_activities__iati_activity__location__location_id": "Location",
            "iati_activities__iati_activity__location__name": "LocationName",
            "iati_activities__iati_activity__location__description": "LocationDescription",
            "iati_activities__iati_activity__location__activity_description": "LocationActivityDescription",
            "iati_activities__iati_activity__location__administrative": "LocationAdministrative",
            "iati_activities__iati_activity__location__point": "Location",
            "iati_activities__iati_activity__location__point__pos": "Location",
            "iati_activities__iati_activity__location__exactness": "Location",
            "iati_activities__iati_activity__location__location_class": "Location",
            "iati_activities__iati_activity__location__feature_designation": "Location",
            "iati_activities__iati_activity__sector": "ActivitySector",
            "iati_activities__iati_activity__country_budget_items": "CountryBudgetItem",
            "iati_activities__iati_activity__country_budget_items__budget_item": "BudgetItem",
            "iati_activities__iati_activity__country_budget_items__budget_item__description": "BudgetItemDescription",
            "iati_activities__iati_activity__humanitarian_scope": "HumanitarianScope",
            "iati_activities__iati_activity__policy_marker": "ActivityPolicyMarker",
            "iati_activities__iati_activity__collaboration_type": "Activity",
            "iati_activities__iati_activity__default_flow_type": "Activity",
            "iati_activities__iati_activity__default_finance_type": "Activity",
            "iati_activities__iati_activity__default_aid_type": "ActivityDefaultAidType",
            "iati_activities__iati_activity__default_tied_status": "Activity",
            "iati_activities__iati_activity__budget": "Budget",
            "iati_activities__iati_activity__budget__period_start": "Budget",
            "iati_activities__iati_activity__budget__period_end": "Budget",
            "iati_activities__iati_activity__budget__value": "Budget",
            "iati_activities__iati_activity__planned_disbursement": "PlannedDisbursement",
            "iati_activities__iati_activity__planned_disbursement__period_start": "PlannedDisbursement",
            "iati_activities__iati_activity__planned_disbursement__period_end": "PlannedDisbursement",
            "iati_activities__iati_activity__planned_disbursement__value": "PlannedDisbursement",
            "iati_activities__iati_activity__planned_disbursement__provider_org": "PlannedDisbursementProvider",
            "iati_activities__iati_activity__planned_disbursement__receiver_org": "PlannedDisbursementReceiver",
            "iati_activities__iati_activity__capital_spend": "Activity",
            "iati_activities__iati_activity__transaction": "Transaction",
            "iati_activities__iati_activity__transaction__transaction_type": "Transaction",
            "iati_activities__iati_activity__transaction__transaction_date": "Transaction",
            "ati_activities__iati_activity__transaction__value": "Transaction",
            "iati_activities__iati_activity__transaction__description": "TransactionDescription",
            "iati_activities__iati_activity__transaction__provider_org": "TransactionProvider",
            "iati_activities__iati_activity__transaction__receiver_org": "TransactionReceiver",
            "iati_activities__iati_activity__transaction__disbursement_channel": "Transaction",
            "iati_activities__iati_activity__transaction__sector": "TransactionSector",
            "iati_activities__iati_activity__transaction__recipient_country": "TransactionRecipientCountry",
            "iati_activities__iati_activity__transaction__recipient_region": "TransactionRecipientRegion",
            "iati_activities__iati_activity__transaction__flow_type": "Transaction",
            "iati_activities__iati_activity__transaction__finance_type": "Transaction",
            "iati_activities__iati_activity__transaction__aid_type": "TransactionAidType",
            "iati_activities__iati_activity__transaction__tied_status": "Transaction",
            "iati_activities__iati_activity__document_link": "DocumentLink",
            "iati_activities__iati_activity__document_link__document_date": "DocumentLink",
            "iati_activities__iati_activity__document_link__title": "DocumentLinkTitle",
            "iati_activities__iati_activity__document_link__description": "DocumentLinkDescription",
            "iati_activities__iati_activity__document_link__category": "DocumentLinkCategory",
            "iati_activities__iati_activity__document_link__language": "DocumentLinkLanguage",
            "iati_activities__iati_activity__related_activity": "RelatedActivity",
            "iati_activities__iati_activity__legacy_data": "LegacyData",
            "iati_activities__iati_activity__conditions": "Conditions",
            "iati_activities__iati_activity__conditions__condition": "Condition",
            "iati_activities__iati_activity__result": "Result",
            "iati_activities__iati_activity__result__reference": "ResultReference",
            "iati_activities__iati_activity__result__title": "ResultTitle",
            "iati_activities__iati_activity__result__description": "ResultDescription",
            "iati_activities__iati_activity__result__document_link": "DocumentLink",
            "iati_activities__iati_activity__result__document_link__title": "DocumentLinkTitle",
            "iati_activities__iati_activity__result__document_link__description": "DocumentLinkDescription",
            "iati_activities__iati_activity__result__document_link__category": "DocumentLinkCategory",
            "iati_activities__iati_activity__result__document_link__language": "DocumentLinkLanguage",
            "iati_activities__iati_activity__result__document_link__document_date": "DocumentLink",
            "iati_activities__iati_activity__result__indicator": "ResultIndicator",
            "iati_activities__iati_activity__result__indicator__reference": "ResultIndicatorReference",
            "iati_activities__iati_activity__result__indicator__title": "ResultIndicatorTitle",
            "iati_activities__iati_activity__result__indicator__description": "ResultIndicatorDescription",
            "iati_activities__iati_activity__result__indicator__document_link": "DocumentLink",
            "iati_activities__iati_activity__result__indicator__document_link__document_date": "DocumentLink",
            "iati_activities__iati_activity__result__indicator__document_link__title": "DocumentLinkTitle",
            "iati_activities__iati_activity__result__indicator__document_link__description": "DocumentLinkDescription",
            "iati_activities__iati_activity__result__indicator__document_link__category": "DocumentLinkCategory",
            "iati_activities__iati_activity__result__indicator__document_link__language": "DocumentLinkLanguage",
            "iati_activities__iati_activity__result__indicator__baseline": "ResultIndicatorBaseline",
            "iati_activities__iati_activity__result__indicator__baseline__comment": "ResultIndicatorBaselineComment",
            "iati_activities__iati_activity__result__indicator__baseline__location": "Location",
            "iati_activities__iati_activity__result__indicator__baseline__dimension":
                "ResultIndicatorBaselineDimension",
            "iati_activities__iati_activity__result__indicator__baseline__document_link": "DocumentLink",
            "iati_activities__iati_activity__result__indicator__baseline__document_link__document_date":
                "DocumentLink",
            "iati_activities__iati_activity__result__indicator__baseline__document_link__title": "DocumentLinkTitle",
            "iati_activities__iati_activity__result__indicator__baseline__document_link__description":
                "DocumentLinkDescription",
            "iati_activities__iati_activity__result__indicator__baseline__document_link__category":
                "DocumentLinkCategory",
            "iati_activities__iati_activity__result__indicator__baseline__document_link__language":
                "DocumentLinkLanguage",
            "iati_activities__iati_activity__result__indicator__period": "ResultIndicatorPeriod",
            "iati_activities__iati_activity__result__indicator__period__period_start": "ResultIndicatorPeriod",
            "iati_activities__iati_activity__result__indicator__period__period_end": "ResultIndicatorPeriod",
            "iati_activities__iati_activity__result__indicator__period__target": "ResultIndicatorPeriodTarget",
            "iati_activities__iati_activity__result__indicator__period__target__location":
                "ResultIndicatorPeriodTargetLocation",
            "iati_activities__iati_activity__result__indicator__period__target__dimension":
                "ResultIndicatorPeriodTargetDimension",
            "iati_activities__iati_activity__result__indicator__period__target__comment":
                "ResultIndicatorPeriodTargetComment",
            "iati_activities__iati_activity__result__indicator__period__target__document_link": "DocumentLink",
            "iati_activities__iati_activity__result__indicator__period__target__document_link__title":
                "DocumentLinkTitle",
            "iati_activities__iati_activity__result__indicator__period__target__document_link__description":
                "DocumentLinkDescription",
            "iati_activities__iati_activity__result__indicator__period__target__document_link__category":
                "DocumentLinkCategory",
            "iati_activities__iati_activity__result__indicator__period__target__document_link__language":
                "DocumentLinkLanguage",
            "iati_activities__iati_activity__result__indicator__period__target__document_link__document_date":
                "DocumentLink",
            "iati_activities__iati_activity__result__indicator__period__actual": "ResultIndicatorPeriodActual",
            "iati_activities__iati_activity__result__indicator__period__actual__location":
                "ResultIndicatorPeriodActualLocation",
            "iati_activities__iati_activity__result__indicator__period__actual__dimension":
                "ResultIndicatorPeriodActualDimension",
            "iati_activities__iati_activity__result__indicator__period__actual__comment":
                "ResultIndicatorPeriodActualComment",
            "iati_activities__iati_activity__result__indicator__period__actual__document_link": "DocumentLink",
            "iati_activities__iati_activity__result__indicator__period__actual__document_link__title":
                "DocumentLinkTitle",
            "iati_activities__iati_activity__result__indicator__period__actual__document_link__description":
                "DocumentLinkDescription",
            "iati_activities__iati_activity__result__indicator__period__actual__document_link__category":
                "DocumentLinkCategory",
            "iati_activities__iati_activity__result__indicator__period__actual__document_link__language":
                "DocumentLinkLanguage",
            "iati_activities__iati_activity__result__indicator__period__actual__document_link__document_date":
                "DocumentLink",
            "iati_activities__iati_activity__tag": "ActivityTag",
            "iati_activities__iati_activity__crs_add": "CrsAdd",
            "iati_activities__iati_activity__crs_add__loan_terms": "CrsAddLoanTerms",
            "iati_activities__iati_activity__crs_add__other_flags": "CrsAddOtherFlags",
            "iati_activities__iati_activity__crs_add__loan_status": "CrsAddLoanStatus",
            "iati_activities__iati_activity__fss": "Fss",
            "iati_activities__iati_activity__fss__forecast": "FssForecast",

            # organisation
            "iati_organisations__iati_organisation": "Organisation",
            "iati_organisations__iati_organisation__name": "OrganisationName",
            "iati_organisations__iati_organisation__reporting_org": "OrganisationReportingOrganisation",
            "iati_organisations__iati_organisation__total_budget": "TotalBudget",
            "iati_organisations__iati_organisation__total_budget__budget_line": "TotalBudgetLine",
            "iati_organisations__iati_organisation__recipient_org_budget": "RecipientOrgBudget",
            "iati_organisations__iati_organisation__recipient_org_budget__budget_line": "RecipientOrgBudgetLine",
            "iati_organisations__iati_organisation__recipient_region_budget": "RecipientRegionBudget",
            "iati_organisations__iati_organisation__recipient_region_budget__budget_line": "RecipientRegionBudgetLine",
            "iati_organisations__iati_organisation__recipient_country_budget": "RecipientCountryBudget",
            "iati_organisations__iati_organisation__recipient_country_budget__budget_line":
                "RecipientCountryBudgetLine",
            "iati_organisations__iati_organisation__total_expenditure": "TotalExpenditure",
            "iati_organisations__iati_organisation__total_expenditure__expense_line": "TotalExpenditureLine",
            "iati_organisations__iati_organisation__document_link": "OrganisationDocumentLink",
            "iati_organisations__iati_organisation__document_link__title": "DocumentLinkTitle",
            "iati_organisations__iati_organisation__document_link__description": "DocumentLinkDescription",
            "iati_organisations__iati_organisation__document_link__category": "OrganisationDocumentLinkCategory",
            "iati_organisations__iati_organisation__document_link__language": "OrganisationDocumentLinkLanguage",
            "iati_organisations__iati_organisation__document_link__document_date": "OrganisationDocumentLink",
            "iati_organisations__iati_organisation__document_link__recipient_country": "DocumentLinkRecipientCountry",

        }

        namespace = NameSpaceElement()
        namespace_list = []
        if attribute_dict is None:
            parent_element = element.getparent()
            x_path = self.root.getroottree().getpath(parent_element)
            function_name = self.generate_function_name(x_path)

            parent_element_name = function_model_mapping[function_name]
            namespace.parent_element_name = parent_element_name
            namespace.nsmap = element.nsmap
            namespace.sub_element = True

            xml_to_dict = xmltodict.parse(etree.tostring(element),
                                          process_namespaces=True)
            namespace.namespace = xml_to_dict  # etree.tostring(element).decode('utf-8')
        else:
            parent_element = element  # when namespace is attribute of the element, the parent element is itself.
            x_path = self.root.getroottree().getpath(parent_element)
            function_name = self.generate_function_name(x_path)

            parent_element_name = function_model_mapping[function_name]
            namespace.parent_element_name = parent_element_name
            namespace.nsmap = element.nsmap
            namespace.namespace = attribute_dict
            namespace.sub_element = False
        if hasattr(next(reversed(self.model_store[parent_element_name])),
                   'namespace'):
            next(reversed(
                self.model_store[parent_element_name])).namespace.append(
                namespace)
        else:
            namespace_list.append(namespace)
            setattr(next(reversed(self.model_store[parent_element_name])),
                    'namespace', namespace_list)
        pass
