import logging
import numbers
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify

from currency_convert import convert
from geodata.models import Country, Region
from iati import models
from iati.parser import post_save, post_save_validators
from iati.parser.exceptions import (
    FieldValidationError, IgnoredVocabularyError, ParserError,
    RequiredFieldError
)
from iati.parser.higher_order_parser import provider_org, receiver_org
from iati.parser.iati_parser import IatiParser
from iati.transaction import models as transaction_models
from iati_codelists import models as codelist_models
from iati_organisation import models as organisation_models
from iati_vocabulary import models as vocabulary_models

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Parse(IatiParser):

    def __init__(self, *args, **kwargs):
        super(Parse, self).__init__(*args, **kwargs)
        self.VERSION = '2.02'

    def add_narrative(self, element, parent, is_organisation_narrative=False):
        # set on activity (if set)

        default_lang = self.default_lang
        lang = element.attrib.get(
            '{http://www.w3.org/XML/1998/namespace}lang', default_lang)
        text = element.text
        if text is not None:
            text = text.replace('"', '""')

        if lang:
            lang = lang.lower()

        language = self.get_or_none(codelist_models.Language, code=lang)

        if not parent:
            raise ParserError(
                "Unknown",
                "narrative",
                "parent object must be passed")

        register_name = parent.__class__.__name__ + "Narrative"

        if not language:
            raise RequiredFieldError(
                register_name,
                "xml:lang",
                "must specify xml:lang on iati-activity or xml:lang on the \
                element itself")
        if not text:
            raise RequiredFieldError(
                register_name,
                "text",
                "empty narrative")

        if not is_organisation_narrative:
            narrative = models.Narrative()
            narrative.activity = self.get_model('Activity')
        else:
            narrative = organisation_models.OrganisationNarrative()
            narrative.organisation = self.get_model('Organisation')

        narrative.language = language
        narrative.content = text
        # This (instead of narrative.related_object) is required, otherwise
        # related object doesn't get passed to the model_store (memory) and
        # 'update_related()' fails.
        # It should probably be passed to the __init__() ?
        setattr(narrative, '_related_object', parent)

        self.register_model(register_name, narrative)

    def iati_activities__iati_activity(self, element):
        """attributes:
        {http://www.w3.org/XML/1998/namespace}lang:en
        default-currency:USD
        last-updated-datetime:2014-09-10T07:15:37Z
        linked-data-uri:http://data.example.org/123456789
        hierarchy:1

        tag:iati-activity"""

        iati_identifier = element.xpath('iati-identifier/text()')

        if len(iati_identifier) < 1:
            raise FieldValidationError(
                "iati-activity",
                "iati-identifier",
                "no iati-identifier found")

        activity_id = iati_identifier[0]
        normalized_activity_id = self._normalize(activity_id)
        # default is here to make it default to settings 'DEFAULT_LANG' on no
        # language set (validation error we want to be flexible with per
        # instance)
        default_lang_code = element.attrib.get(
            '{http://www.w3.org/XML/1998/namespace}lang',
            settings.DEFAULT_LANG)
        if default_lang_code:
            default_lang_code = default_lang_code.lower()

        default_lang = self.get_or_none(
            codelist_models.Language,
            code=default_lang_code
        )

        hierarchy = element.attrib.get('hierarchy')
        humanitarian = element.attrib.get('humanitarian')
        last_updated_datetime = self.validate_date(
            element.attrib.get('last-updated-datetime'))
        linked_data_uri = element.attrib.get('linked-data-uri')
        default_currency = self.get_or_none(
            models.Currency, code=element.attrib.get('default-currency'))

        if not activity_id:
            raise RequiredFieldError(
                "iati-identifier",
                "text",
                "required element empty")

        # old_activity = self.get_or_none(
        #     models.Activity, iati_identifier=activity_id)
        #
        # if old_activity and (old_activity.dataset.name != self.dataset.name):
        #     self.append_error(
        #         'FieldValidationError',
        #         "iati-identifier",
        #         "ref",
        #         "An activity with the same iati-identifier was found in \
        #         another dataset",
        #         element.sourceline,
        #         "found in dataset: '{}'".format(old_activity.dataset.name),
        #         activity_id)
        #
        # if (old_activity
        #         and not self.force_reparse and not old_activity.modified):
        #     # update last_updated_model to prevent the activity from being
        #     # deleted because its not updated (and thereby assumed not found
        #     # in the dataset)
        #     old_activity.save()
        #
        #     if last_updated_datetime\
        #         and last_updated_datetime\
        #             == old_activity.last_updated_datetime:
        #         raise NoUpdateRequired('activity', 'already up to date')
        #
        #     if last_updated_datetime and (last_updated_datetime <
        #                                   old_activity.last_updated_datetime):
        #         raise FieldValidationError(
        #             "iati-activity",
        #             "last-updated-datetime",
        #             "last-updated-time is less than existing activity",
        #             None,
        #             element.sourceline,
        #             activity_id,
        #             activity_id)
        #
        #     if not last_updated_datetime and old_activity\
        #             .last_updated_datetime:
        #         raise FieldValidationError(
        #             "iati-activity",
        #             "last-updated-datetime",
        #             "last-updated-time is not present, but is present on \
        #                     existing activity",
        #             None,
        #             element.sourceline,
        #             activity_id,
        #             activity_id)
        #
        #     # TODO: test activity is deleted along with related models
        #     # update on TODO above; only iati_title, TransactionReceiver,
        #     # TransactionProvider are not deleted atm - 2015-10-01
        #     # TODO: do this after activity is parsed along with other saves?

        try:
            old_activity = models.Activity.objects.get(
                iati_identifier=activity_id)
        except ObjectDoesNotExist:
            old_activity = None

        if old_activity:
            old_activity.delete()

        # TODO: assert title is in xml, for proper OneToOne relation
        # (only on 2.02)

        activity = models.Activity()
        activity.iati_identifier = activity_id
        activity.normalized_iati_identifier = normalized_activity_id
        activity.default_lang = default_lang
        if hierarchy:
            activity.hierarchy = hierarchy
        activity.humanitarian = self.makeBoolNone(humanitarian)
        activity.dataset = self.dataset
        activity.publisher = self.publisher
        activity.last_updated_datetime = last_updated_datetime
        activity.linked_data_uri = linked_data_uri
        activity.default_currency = default_currency
        activity.iati_standard_version_id = self.VERSION

        activity.published = True
        activity.ready_to_publish = True
        activity.modified = False

        # for later reference
        self.default_lang = default_lang_code

        # For this validation-only branch we only save activities and
        # organisations
        # All other elements are not written to the db
        activity.save()

        self.register_model('Activity', activity)
        return element

    def iati_activities__iati_activity__iati_identifier(self, element):
        """
        attributes:

        tag:iati-identifier
        """
        iati_identifier = element.text

        if not iati_identifier:
            raise RequiredFieldError(
                "iati-identifier",
                "text",
                "required element empty")

        activity = self.get_model('Activity')
        activity.iati_identifier = iati_identifier

        return element

    def iati_activities__iati_activity__reporting_org(self, element):
        """attributes:
        ref:AA-AAA-123456789
        type:40
        secondary-reporter:0

        tag:reporting-org"""
        ref = element.attrib.get('ref')

        if not ref:
            raise RequiredFieldError(
                "reporting-org",
                "ref",
                "required attribute missing")

        if ref:
            self.check_registration_agency_validity(
                "reporting-org/ref", element, ref)

        if ref is not None:
            normalized_ref = self._normalize(ref)
        org_type = self.get_or_none(
            codelist_models.OrganisationType,
            code=element.attrib.get('type'))
        secondary_reporter = element.attrib.get('secondary-reporter', '0')

        organisation = self.get_or_none(
            models.Organisation, organisation_identifier=ref)

        # create an organisation
        if not organisation:

            organisation = organisation_models.Organisation()
            organisation.organisation_identifier = ref
            organisation.last_updated_datetime = datetime.now()
            organisation.iati_standard_version_id = "2.02"
            organisation.reported_in_iati = False
            organisation.type = org_type

            # TODO: is this right? - 2017-03-27
            organisation.published = False
            organisation.ready_to_publish = True
            organisation.modified = False

            organisation.save()

            organisation_name = organisation_models.OrganisationName()
            organisation_name.organisation = organisation

            self.publisher.organisation = organisation

            # create an organization if it is not parsed yet or not in IATI
            # Also, link to publisher

            organisation_name.save()
            self.publisher.save()

            self.register_model('Organisation', organisation)
            self.register_model('OrganisationName', organisation_name)

            narratives = element.findall('narrative')

            if len(narratives) > 0:
                for narrative in narratives:
                    self.add_narrative(narrative, organisation_name,
                                       is_organisation_narrative=True)
                    organisation.primary_name = self.get_primary_name(
                        narrative, organisation.primary_name)
            else:
                organisation.primary_name = ref

        activity = self.get_model('Activity')
        reporting_organisation = models.ActivityReportingOrganisation()
        reporting_organisation.ref = ref
        reporting_organisation.normalized_ref = normalized_ref
        reporting_organisation.type = org_type
        reporting_organisation.activity = activity
        reporting_organisation.organisation = organisation
        reporting_organisation.secondary_reporter = self.makeBool(
            secondary_reporter)

        narratives = element.findall('narrative')
        if len(narratives) > 0:
            for narrative in narratives:
                self.add_narrative(narrative, reporting_organisation)

        activity.secondary_reporter = self.makeBool(secondary_reporter)

        self.register_model('ActivityReportingOrganisation',
                            reporting_organisation)

        return element

    def iati_activities__iati_activity__reporting_org__narrative(
            self, element):
        """attributes:

        tag:narrative
        """
        model = self.get_model('ActivityReportingOrganisation')
        self.add_narrative(element, model)

        return element

    def iati_activities__iati_activity__participating_org(self, element):
        """attributes:https://docs.djangoproject.com/en/1.8/topics/migrations/
        ref:BB-BBB-123456789
        role:1
        type:40

        tag:participating-org"""
        ref = element.attrib.get('ref', None)
        if ref == '':
            ref = None
        activity_id = element.attrib.get('activity-id', None)

        org_activity = self.get_or_none(
            models.Activity, iati_identifier=activity_id)
        role = self.get_or_none(
            codelist_models.OrganisationRole, code=element.attrib.get('role'))

        if ref is not None:
            normalized_ref = self._normalize(ref)
        else:
            normalized_ref = None

        organisation = self.get_or_none(
            models.Organisation, organisation_identifier=ref)
        org_type = self.get_or_none(
            codelist_models.OrganisationType,
            code=element.attrib.get('type'))

        if not role:
            raise RequiredFieldError(
                "participating-org",
                "role",
                "required attribute missing")

        if ref:
            self.check_registration_agency_validity(
                "participating-org", element, ref)

        activity = self.get_model('Activity')
        participating_organisation = models.ActivityParticipatingOrganisation()
        participating_organisation.ref = ref
        participating_organisation.normalized_ref = normalized_ref
        participating_organisation.type = org_type
        participating_organisation.activity = activity
        participating_organisation.organisation = organisation
        participating_organisation.role = role
        participating_organisation.org_activity_id = activity_id
        participating_organisation.org_activity_obj = org_activity

        self.register_model(
            'ActivityParticipatingOrganisation', participating_organisation)

        return element

    def iati_activities__iati_activity__participating_org__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        model = self.get_model('ActivityParticipatingOrganisation')
        self.add_narrative(element, model)

        # workaround for IATI ref uniqueness limitation
        model.primary_name = self.get_primary_name(element, model.primary_name)

        return element

    def iati_activities__iati_activity__title(self, element):
        """attributes:

        tag:title"""
        title_list = self.get_model_list('Title')

        if title_list and len(title_list) > 0:
            raise FieldValidationError(
                "title",
                "title",
                "duplicate titles are not allowed")

        # activity = self.pop_model('Activity')
        activity = self.get_model('Activity')

        title = models.Title()
        title.activity = activity

        # activity.title = title

        # order is important (
        # TODO: change datastructure to handle this case more transparant, like
        # insertBefore or something)
        self.register_model('Title', title)
        # self.register_model('Activity', activity)

    def iati_activities__iati_activity__title__narrative(self, element):
        """attributes:

        tag:narrative"""
        # TODO: make this more clear and not depend on order of things
        # title = self.get_model('Activity', index=-2) # this points to Title
        title = self.get_model('Title')  # this points to Title
        self.add_narrative(element, title)

        return element

    def iati_activities__iati_activity__description(self, element):
        """attributes:
        type:1

        tag:description"""

        description_type_code = element.attrib.get('type', 1)
        description_type = self.get_or_none(
            codelist_models.DescriptionType,
            code=description_type_code)

        activity = self.get_model('Activity')
        description = models.Description()
        description.activity = activity
        description.type = description_type

        self.register_model('Description', description)
        return element

    def iati_activities__iati_activity__description__narrative(self, element):
        """attributes:

        tag:narrative"""
        title = self.get_model('Description')
        self.add_narrative(element, title)

        return element

    def iati_activities__iati_activity__other_identifier(self, element):
        """attributes:
        ref:ABC123-XYZ
        type:A1
        tag:other-identifier"""
        identifier = element.attrib.get('ref')
        other_identifier_type = self.get_or_none(
            models.OtherIdentifierType, code=element.attrib.get('type'))

        if not identifier:
            raise RequiredFieldError(
                "other-identifier",
                "ref",
                "required attribute missing")
        # TODO: iati docs say type should be required (but can't for backwards
        # compatibility), should throw error on 2.0x

        activity = self.get_model('Activity')
        other_identifier = models.OtherIdentifier()
        other_identifier.activity = activity
        other_identifier.identifier = identifier
        other_identifier.type = other_identifier_type

        self.register_model('OtherIdentifier', other_identifier)
        return element

    def iati_activities__iati_activity__other_identifier__owner_org(
            self, element):
        """attributes:
        ref:AA-AAA-123456789

        tag:owner-org"""
        ref = element.attrib.get('ref')

        if not ref:
            raise RequiredFieldError(
                "other-identifier/owner-org",
                "ref",
                "required attribute missing")

        other_identifier = self.get_model('OtherIdentifier')
        other_identifier.owner_ref = ref

        return element

    def iati_activities__iati_activity__other_identifier__owner_org__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        other_identifier = self.get_model('OtherIdentifier')
        self.add_narrative(element, other_identifier)
        return element

    def iati_activities__iati_activity__activity_status(self, element):
        """attributes:
        code:2

        tag:activity-status"""

        code = element.attrib.get('code')
        activity_status = self.get_or_none(
            codelist_models.ActivityStatus, code=code)

        if not code:
            raise RequiredFieldError(
                "activity-status",
                "code",
                "required attribute missing")

        if not activity_status:
            raise FieldValidationError(
                "activity-status",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        activity = self.get_model('Activity')
        activity.activity_status = activity_status

        return element

    def iati_activities__iati_activity__activity_date(self, element):
        """attributes:
        iso-date:2012-04-15
        type:1

        tag:activity-date"""

        iso_date = element.attrib.get('iso-date')

        if not iso_date:
            raise RequiredFieldError(
                "activity-date",
                "iso-date",
                "required attribute missing")

        iso_date = self.validate_date(iso_date)

        if not iso_date:
            raise FieldValidationError(
                "activity-date",
                "iso-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('iso-date'))

        type_code = element.attrib.get('type')

        if not type_code:
            raise RequiredFieldError(
                "activity-date",
                "type",
                "required attribute missing")

        type_code = self.get_or_none(
            codelist_models.ActivityDateType, code=type_code)

        if not type_code:
            raise FieldValidationError(
                "activity-date",
                "type",
                "not found on the accompanying code list",
                None,
                None,
                element.attrib.get('type'))

        if type_code in ['2', '4']:
            if iso_date > datetime.now():
                raise FieldValidationError(
                    "activity-date",
                    "iso-date",
                    "All instances of the ActivityDateType code 2 & 4 (actual \
                            dates) are not expected to be in the future",
                    None,
                    None,
                    str(iso_date))

        activity = self.get_model('Activity')

        activity_date = models.ActivityDate()
        activity_date.iso_date = iso_date
        activity_date.type = type_code
        activity_date.activity = activity

        # to make ordering possible, activity dates are duplicated onto the
        # Activity model
        mapping = {
            '1': 'planned_start',
            '2': 'actual_start',
            '3': 'planned_end',
            '4': 'actual_end'
        }

        if type_code.code in mapping:
            setattr(activity, mapping[type_code.code], iso_date)

        self.register_model('ActivityDate', activity_date)
        return element

    def iati_activities__iati_activity__activity_date__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        # this is not implemented
        activity_date = self.get_model('ActivityDate')
        self.add_narrative(element, activity_date)
        return element

    def iati_activities__iati_activity__contact_info(self, element):
        """attributes:
        type:1

        tag:contact-info"""
        type_code = self.get_or_none(
            codelist_models.ContactType, code=element.attrib.get('type'))

        activity = self.get_model('Activity')
        contact_info = models.ContactInfo()
        contact_info.activity = activity
        contact_info.type = type_code
        self.register_model('ContactInfo', contact_info)

        return element

    def iati_activities__iati_activity__contact_info__organisation(
            self, element):
        """attributes:

        tag:organisation"""
        contact_info = self.get_model('ContactInfo')
        contact_info_organisation = models.ContactInfoOrganisation()
        contact_info_organisation.contact_info = contact_info
        self.register_model('ContactInfoOrganisation',
                            contact_info_organisation)
        return element

    def iati_activities__iati_activity__contact_info__organisation__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        contact_info_organisation = self.get_model('ContactInfoOrganisation')
        self.add_narrative(element, contact_info_organisation)
        return element

    def iati_activities__iati_activity__contact_info__department(
            self, element):
        """attributes:

        tag:department"""
        contact_info = self.get_model('ContactInfo')
        contact_info_department = models.ContactInfoDepartment()
        contact_info_department.contact_info = contact_info

        self.register_model('ContactInfoDepartment', contact_info_department)

        return element

    def iati_activities__iati_activity__contact_info__department__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        contact_info_department = self.get_model('ContactInfoDepartment')
        self.add_narrative(element, contact_info_department)
        return element

    def iati_activities__iati_activity__contact_info__person_name(
            self, element):
        """attributes:

        tag:person-name"""
        contact_info = self.get_model('ContactInfo')
        contact_info_person_name = models.ContactInfoPersonName()
        contact_info_person_name.contact_info = contact_info
        self.register_model('ContactInfoPersonName', contact_info_person_name)

        return element

    def iati_activities__iati_activity__contact_info__person_name__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        contact_info_person_name = self.get_model('ContactInfoPersonName')
        self.add_narrative(element, contact_info_person_name)
        return element

    def iati_activities__iati_activity__contact_info__job_title(self, element):
        """attributes:

        tag:job-title"""
        contact_info = self.get_model('ContactInfo')
        contact_info_job_title = models.ContactInfoJobTitle()
        contact_info_job_title.contact_info = contact_info
        self.register_model('ContactInfoJobTitle', contact_info_job_title)
        return element

    def iati_activities__iati_activity__contact_info__job_title__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        contact_info_job_title = self.get_model('ContactInfoJobTitle')
        self.add_narrative(element, contact_info_job_title)
        return element

    def iati_activities__iati_activity__contact_info__telephone(
            self, element):
        """attributes:

        tag:telephone"""
        text = element.text

        if not text:
            raise RequiredFieldError(
                "contact-info",
                "telephone",
                "empty element")

        contact_info = self.get_model('ContactInfo')
        contact_info.telephone = text

        return element

    def iati_activities__iati_activity__contact_info__email(self, element):
        """attributes:

        tag:email"""
        text = element.text

        if not text:
            raise RequiredFieldError(
                "contact-info",
                "email",
                "empty element")

        contact_info = self.get_model('ContactInfo')
        contact_info.email = text

        return element

    def iati_activities__iati_activity__contact_info__website(self, element):
        """attributes:

        tag:website"""
        text = element.text

        if not text:
            raise RequiredFieldError(
                "contact-info",
                "website",
                "empty element")

        contact_info = self.get_model('ContactInfo')
        contact_info.website = text

        return element

    def iati_activities__iati_activity__contact_info__mailing_address(
            self, element):
        """attributes:

        tag:mailing-address"""
        contact_info = self.get_model('ContactInfo')
        contact_info_mailing_address = models.ContactInfoMailingAddress()
        contact_info_mailing_address.contact_info = contact_info
        self.register_model('ContactInfoMailingAddress',
                            contact_info_mailing_address)

        return element

    def iati_activities__iati_activity__contact_info__mailing_address__narrative(self, element):  # NOQA: E501
        """attributes:

        tag:narrative"""
        contact_info_mailing_address = self.get_model(
            'ContactInfoMailingAddress')
        self.add_narrative(element, contact_info_mailing_address)
        return element

    def iati_activities__iati_activity__activity_scope(self, element):
        """attributes:
        code:3

        tag:activity-scope"""
        code = element.attrib.get('code')
        activity_scope = self.get_or_none(
            codelist_models.ActivityScope, code=code)

        if not code:
            raise RequiredFieldError(
                "activity-status",
                "code",
                "required attribute missing")

        if not activity_scope:
            raise FieldValidationError(
                "activity-status",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        activity = self.get_model('Activity')
        activity.scope = activity_scope

        return element

    def iati_activities__iati_activity__recipient_country(self, element):
        """attributes:
        code:AF
        percentage:25

        # tag:recipient-country
        #
        # IATI business rule: If transaction/recipient-country AND/OR
        # transaction/recipient-region are used THEN ALL transaction elements
        # MUST contain a recipient-country or
        # recipient-region element AND (iati-activity/recipient-country AND
        # iati-activity/recipient-region
        # MUST NOT be used)
        # """
        #
        # transaction_recipient_country = self.root.findall(
        #     "./iati-activity/transaction/recipient-country")
        # if len(transaction_recipient_country) > 0:
        #     raise ParserError(
        #         "iati-activity",
        #         "recipient-country",
        #         "activity/recipient-country must not used if "
        #         "transaction/recipient-country is used."
        #
        #     )
        code = element.attrib.get('code')
        country = self.get_or_none(Country, code=code)
        percentage = element.attrib.get('percentage')

        if not code:
            raise RequiredFieldError(
                "recipient-country",
                "code",
                "required attribute missing")

        if not country:
            raise FieldValidationError(
                "recipient-country",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                element.attrib.get('code'))

        if percentage:
            try:
                percentage = Decimal(percentage)
            except InvalidOperation:
                raise FieldValidationError(
                    "recipient-country",
                    "percentage",
                    "percentage value is not valid",
                    None,
                    None,
                    percentage)

        activity = self.get_model('Activity')
        activity_recipient_country = models.ActivityRecipientCountry()
        activity_recipient_country.country = country
        activity_recipient_country.activity = activity
        activity_recipient_country.percentage = percentage

        self.register_model('ActivityRecipientCountry',
                            activity_recipient_country)

        return element

    def iati_activities__iati_activity__recipient_country__narrative(self,
                                                                     element):
        """attributes:

        tag:narrative"""
        model = self.get_model('ActivityRecipientCountry')
        self.add_narrative(element, model)
        return element

    def iati_activities__iati_activity__recipient_region(self, element):
        """
        attributes:
        code:489
        vocabulary:1
        percentage:25

        # tag:recipient-region
        #
        # IATI business rule: If transaction/recipient-country AND/OR
        # transaction/recipient-region are used
        # THEN ALL transaction elements MUST contain a recipient-country or
        # recipient-region element
        # AND (iati-activity/recipient-country AND
        # iati-activity/recipient-region
        # MUST NOT be used).
        # """
        #
        # transaction_recipient_region = self.root.findall(
        #     "./iati-activity/transaction/recipient-region")
        # if len(transaction_recipient_region) > 0:
        #     raise ParserError(
        #         "iati-activity",
        #         "recipient-region",
        #         "activity/recipient-region must not used if transaction/recipient-region is used.",  # NOQA: E501
        #
        #     )
        code = element.attrib.get('code')

        # TODO: make defaults more transparant, here: 'OECD-DAC default'
        vocabulary = self.get_or_none(
            vocabulary_models.RegionVocabulary,
            code=element.attrib.get(
                'vocabulary',
                '1'))
        vocabulary_uri = element.attrib.get('vocabulary-uri')
        percentage = element.attrib.get('percentage')
        region = Region.objects.filter(code=code,
                                       region_vocabulary=vocabulary).first()

        if not code:
            raise RequiredFieldError(
                "recipient-region",
                "code",
                "code is unspecified or invalid")

        if not vocabulary:
            raise RequiredFieldError(
                "recipient-region",
                "vocabulary",
                "not found on the accompanying code list")

        if not region and vocabulary.code == '1':
            raise FieldValidationError(
                "recipient-region",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        elif not region and vocabulary.code == '99':
            try:
                region_vocabulary = \
                    vocabulary_models.RegionVocabulary.objects.get(code='99')
            except vocabulary_models.RegionVocabulary.DoesNotExist:
                raise IgnoredVocabularyError(
                    "recipient-region",
                    "code",
                    "code is unspecified or invalid")
            region = Region()
            region.code = code
            region.name = 'Vocabulary 99'
            region.region_vocabulary = region_vocabulary
            region.save()

        elif not region:
            raise IgnoredVocabularyError(
                "recipient-region",
                "code",
                "code is unspecified or invalid"
            )

        if percentage:
            try:
                percentage = Decimal(percentage)
            except InvalidOperation:
                raise FieldValidationError(
                    "activity-sector",
                    "percentage",
                    "percentage value is not valid",
                    None,
                    None,
                    percentage)

        activity = self.get_model('Activity')
        activity_recipient_region = models.ActivityRecipientRegion()
        activity_recipient_region.region = region
        activity_recipient_region.activity = activity
        activity_recipient_region.percentage = percentage
        activity_recipient_region.vocabulary = vocabulary
        activity_recipient_region.vocabulary_uri = vocabulary_uri
        self.register_model('ActivityRecipientRegion',
                            activity_recipient_region)

        return element

    def iati_activities__iati_activity__recipient_region__narrative(self,
                                                                    element):
        """attributes:

        tag: narrative"""
        model = self.get_model('ActivityRecipientRegion')
        self.add_narrative(element, model)
        return element

    def iati_activities__iati_activity__location(self, element):
        """attributes:
        ref:AF-KAN

        tag:location"""
        ref = element.attrib.get('ref')

        activity = self.get_model('Activity')
        location = models.Location()
        location.activity = activity
        location.ref = ref

        self.register_model('Location', location)
        return element

    def iati_activities__iati_activity__location__location_reach(
            self, element):
        """attributes:
        code:1

        tag:location-reach"""
        code = element.attrib.get('code')
        location_reach = self.get_or_none(
            codelist_models.GeographicLocationReach, code=code)

        if not code:
            raise RequiredFieldError(
                "location/location-reach",
                "code",
                "required attribute missing")

        if not location_reach:
            raise RequiredFieldError(
                "location/location-reach",
                "code",
                "not found on the accompanying code list")

        location = self.get_model('Location')
        location.location_reach = location_reach

        return element

    def iati_activities__iati_activity__location__location_id(self, element):
        """attributes:
        vocabulary:G1
        code:1453782

        tag:location-id"""
        code = element.attrib.get('code')
        vocabulary_code = element.attrib.get('vocabulary')
        vocabulary = self.get_or_none(
            vocabulary_models.GeographicVocabulary, code=vocabulary_code)

        if not code:
            raise RequiredFieldError(
                "location/location-id",
                "code",
                "required attribute missing")

        if not vocabulary_code:
            raise RequiredFieldError(
                "location",
                "vocabulary",
                "required attribute missing")

        if not vocabulary:
            raise RequiredFieldError(
                "location/location-id",
                "vocabulary",
                "not found on the accompanying code list")

        location = self.get_model('Location')
        location.location_id_vocabulary = vocabulary
        location.location_id_code = code

        return element

    def iati_activities__iati_activity__location__name(self, element):
        """attributes:

        tag:name"""

        location = self.get_model('Location')
        location_name = models.LocationName()
        location_name.location = location

        self.register_model('LocationName', location_name)
        return element

    def iati_activities__iati_activity__location__name__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        location_name = self.get_model('LocationName')
        self.add_narrative(element, location_name)
        return element

    def iati_activities__iati_activity__location__description(self, element):
        """attributes:

        tag:description"""
        location = self.get_model('Location')
        location_description = models.LocationDescription()
        location_description.location = location

        self.register_model('LocationDescription', location_description)
        return element

    def iati_activities__iati_activity__location__description__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        location_description = self.get_model('LocationDescription')
        self.add_narrative(element, location_description)
        return element

    def iati_activities__iati_activity__location__activity_description(
            self, element):
        """attributes:

        tag:activity-description"""
        location = self.get_model('Location')
        location_activity_description = models.LocationActivityDescription()
        location_activity_description.location = location

        self.register_model('LocationActivityDescription',
                            location_activity_description)
        return element

    def iati_activities__iati_activity__location__activity_description__narrative(self, element):  # NOQA: E501
        """attributes:

        tag:narrative"""
        location_activity_description = self.get_model(
            'LocationActivityDescription')
        self.add_narrative(element, location_activity_description)
        return element

    def iati_activities__iati_activity__location__administrative(
            self, element):
        """attributes:
        vocabulary:G1
        level:1
        code:1453782

        tag:administrative"""
        # TODO: enforce code is according to specified vocabulary standard?
        # TODO: default level?
        code = element.attrib.get('code')
        vocabulary_code = element.attrib.get('vocabulary')
        vocabulary = self.get_or_none(
            vocabulary_models.GeographicVocabulary, code=vocabulary_code)
        level = element.attrib.get('level')

        if not code:
            raise RequiredFieldError(
                "location/administrative",
                "code",
                "required attribute missing")
        # TODO parse logging check if there's a default voc

        if not vocabulary_code:
            raise RequiredFieldError(
                "location/administrative",
                "vocabulary",
                "required attribute missing")

        if not vocabulary:
            raise FieldValidationError(
                "location/administrative",
                "vocabulary",
                "not found on the accompanying code list",
                None,
                None,
                vocabulary_code)

        location = self.get_model('Location')
        location_administrative = models.LocationAdministrative()
        location_administrative.location = location
        location_administrative.code = code
        location_administrative.vocabulary = vocabulary
        location_administrative.level = level

        self.register_model('LocationAdministrative', location_administrative)

        return element

    def iati_activities__iati_activity__location__point(self, element):
        """attributes:
        srsName:http://www.opengis.net/def/crs/EPSG/0/4326

        tag:point"""
        srs_name = element.attrib.get('srsName')

        # TODO: make this field required?
        # if not srs_name: raise RequiredFieldError("srsName",
        # "location_point: srsName is required")
        if not srs_name:
            srs_name = "http://www.opengis.net/def/crs/EPSG/0/4326"

        location = self.get_model('Location')
        location.point_srs_name = srs_name

        return element

    def iati_activities__iati_activity__location__point__pos(self, element):
        """attributes:

        tag:pos"""
        # TODO: validation of lat/long
        # TODO: Allow for different srid's
        text = element.text

        if not text:
            raise RequiredFieldError(
                "location/point",
                "pos",
                "required element empty")

        try:
            latlong = text.strip().split(' ')
            # geos point = long lat, iati point lat long, hence the
            # latlong[1], latlong[0]
            point = GEOSGeometry(
                Point(float(latlong[1]), float(latlong[0])), srid=4326)
        except Exception as e:
            raise FieldValidationError(
                "location/point",
                "pos",
                "latitude/longitude formatting incorrect",
                None,
                None,
                text)

        location = self.get_model('Location')
        location.point_pos = point

        return element

    def iati_activities__iati_activity__location__exactness(self, element):
        """attributes:
        code:1

        tag:exactness"""
        code = element.attrib.get('code')
        exactness = self.get_or_none(
            codelist_models.GeographicExactness, code=code)

        if not code:
            raise RequiredFieldError(
                "location/exactness",
                "code",
                "required attribute missing")

        if not exactness:
            raise FieldValidationError(
                "location/exactness",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        location = self.get_model('Location')
        location.exactness = exactness

        return element

    def iati_activities__iati_activity__location__location_class(
            self, element):
        """attributes:
        code:2

        tag:location-class"""
        code = element.attrib.get('code')
        location_class = self.get_or_none(
            codelist_models.GeographicLocationClass, code=code)

        if not code:
            raise RequiredFieldError(
                "location/location-class",
                "code",
                "required attribute code")

        if not location_class:
            raise FieldValidationError(
                "location/location-class",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        location = self.get_model('Location')
        location.location_class = location_class

        return element

    def iati_activities__iati_activity__location__feature_designation(
            self, element):
        """attributes:
        code:ADMF

        tag:feature-designation"""
        code = element.attrib.get('code')
        feature_designation = self.get_or_none(
            codelist_models.LocationType, code=code)

        if not code:
            raise RequiredFieldError(
                "location/feature-designation",
                "code",
                "required attribute missing")

        if not feature_designation:
            raise FieldValidationError(
                "location/feature-designation",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        location = self.get_model('Location')
        location.feature_designation = feature_designation

        return element

    def iati_activities__iati_activity__sector(self, element):
        """attributes:
        code:489
        vocabulary:1
        percentage:25

        tag:recipient-sector"""
        code = element.attrib.get('code')
        # TODO: make defaults more transparant, here: 'OECD-DAC default'
        vocabulary = self.get_or_none(
            vocabulary_models.SectorVocabulary,
            code=element.attrib.get(
                'vocabulary',
                '1'))
        vocabulary_uri = element.attrib.get('vocabulary-uri')
        percentage = element.attrib.get('percentage')

        if not code:
            raise RequiredFieldError(
                "sector",
                "code",
                "required attribute missing")

        if not vocabulary:
            raise FieldValidationError(
                "sector",
                "vocabulary",
                "not found on the accompanying code list",
                None,
                None,
                vocabulary.code)

        sector = models.Sector.objects.filter(code=slugify(code),
                                              vocabulary=vocabulary).first()

        if not sector and vocabulary.code == '1':
            raise FieldValidationError(
                "sector",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        elif not sector and vocabulary.code in ['99', '98']:
            # This is needed to create a new sector if related to vocabulary 99 or 98  # NOQA: E501
            # ref. http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/sector/  # NOQA: E501

            code = slugify(code)
            sector = self.get_or_none(models.Sector, code=code)

            if not sector:
                sector = models.Sector()
                sector.code = code
                sector.vocabulary = vocabulary
                sector.name = 'Vocabulary 99 or 98'
                sector.description = 'The sector reported corresponds to a sector vocabulary maintained by the reporting organisation for this activity'  # NOQA: E501
                sector.save()

        elif not sector:
            raise IgnoredVocabularyError(
                "sector",
                "vocabulary",
                "non implemented vocabulary")

        if percentage:
            try:
                percentage = Decimal(percentage)
            except InvalidOperation:
                raise FieldValidationError(
                    "sector",
                    "percentage",
                    "percentage value is not valid",
                    None,
                    None,
                    percentage)

        activity = self.get_model('Activity')
        activity_sector = models.ActivitySector()
        activity_sector.sector = sector
        activity_sector.activity = activity
        activity_sector.percentage = percentage
        activity_sector.vocabulary = vocabulary
        activity_sector.vocabulary_uri = vocabulary_uri
        self.register_model('ActivitySector', activity_sector)

        return element

    def iati_activities__iati_activity__sector__narrative(self, element):
        """attribute:

        tag: narrative"""
        model = self.get_model('ActivitySector')
        self.add_narrative(element, model)
        return element

    def iati_activities__iati_activity__country_budget_items(self, element):
        """attributes:
        vocabulary:2

        tag:country-budget-items"""
        code = element.attrib.get('vocabulary')
        vocabulary = self.get_or_none(
            vocabulary_models.BudgetIdentifierVocabulary, code=code)

        if not code:
            raise RequiredFieldError(
                "country-budget-items",
                "vocabulary",
                "invalid vocabulary")

        if not vocabulary:
            raise FieldValidationError(
                "country-budget-items",
                "vocabulary",
                "not found on the accompanying code list",
                None,
                None,
                code)

        activity = self.get_model('Activity')
        country_budget_item = models.CountryBudgetItem()
        country_budget_item.activity = activity
        country_budget_item.vocabulary = vocabulary

        self.register_model('CountryBudgetItem', country_budget_item)
        return element

    def iati_activities__iati_activity__country_budget_items__budget_item(
            self, element):
        """attributes:
        code:1.1.1
        percentage:50

        tag:budget-item"""
        # TODO: Add custom vocabularies
        code = element.attrib.get('code')
        budget_identifier = self.get_or_none(
            codelist_models.BudgetIdentifier, code=code)
        percentage = element.attrib.get('percentage')

        if not code:
            raise RequiredFieldError(
                "country-budget-items/budget-item",
                "code",
                "required attribute missing")

        if not budget_identifier:
            raise FieldValidationError(
                "country-budget-items/budget-item",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        if percentage:
            try:
                percentage = Decimal(percentage)
            except InvalidOperation:
                raise FieldValidationError(
                    "sector",
                    "percentage",
                    "percentage value is not valid",
                    None,
                    None,
                    percentage)

        country_budget_item = self.get_model('CountryBudgetItem')
        budget_item = models.BudgetItem()
        budget_item.country_budget_item = country_budget_item
        budget_item.code = budget_identifier
        budget_item.percentage = percentage

        self.register_model('BudgetItem', budget_item)
        return element

    def iati_activities__iati_activity__country_budget_items__budget_item__description(  # NOQA: E501
            self, element):
        """attributes:

        tag:description"""
        budget_item = self.get_model('BudgetItem')
        budget_item_description = models.BudgetItemDescription()
        budget_item_description.budget_item = budget_item

        self.register_model('BudgetItemDescription', budget_item_description)
        return element

    def iati_activities__iati_activity__country_budget_items__budget_item__description__narrative(self, element):  # NOQA: E501
        """attributes:

        tag:narrative"""
        budget_item_description = self.get_model('BudgetItemDescription')
        self.add_narrative(element, budget_item_description)
        return element

    def iati_activities__iati_activity__humanitarian_scope(self, element):

        activity = self.get_model('Activity')
        scope_type_code = element.attrib.get('type')
        scope_type = self.get_or_none(
            codelist_models.HumanitarianScopeType, code=scope_type_code)
        vocabulary_code = element.attrib.get('vocabulary')
        vocabulary = self.get_or_none(
            vocabulary_models.HumanitarianScopeVocabulary,
            code=vocabulary_code)
        vocabulary_uri = element.attrib.get('vocabulary-uri')
        code = element.attrib.get('code')

        if not code:
            raise RequiredFieldError(
                "humanitarian-scope",
                "code",
                "required attribute missing")

        if not scope_type_code:
            raise RequiredFieldError(
                "humanitarian-scope",
                "type",
                "required attribute missing")

        if not scope_type:
            raise FieldValidationError(
                "humanitarian-scope",
                "type",
                "not found on the accompanying code list",
                None,
                None,
                scope_type_code)

        if not vocabulary_code:
            raise RequiredFieldError(
                "humanitarian-scope",
                "vocabulary",
                "required attribute missing")

        if not vocabulary:
            raise FieldValidationError(
                "humanitarian-scope",
                "vocabulary",
                "not found on the accompanying code list",
                None,
                None,
                vocabulary_code)

        humanitarian_scope = models.HumanitarianScope()
        humanitarian_scope.activity = activity
        humanitarian_scope.type = scope_type
        humanitarian_scope.code = code
        humanitarian_scope.vocabulary = vocabulary
        humanitarian_scope.vocabulary_uri = vocabulary_uri
        self.register_model('HumanitarianScope', humanitarian_scope)

        return element

    def iati_activities__iati_activity__humanitarian_scope__narrative(
            self, element):
        """attributes:

        tag:narrative"""

        humanitarian_scope = self.get_model('HumanitarianScope')
        self.add_narrative(element, humanitarian_scope)

        return element

    def iati_activities__iati_activity__policy_marker(self, element):
        """attributes:
        vocabulary:1
        code:2
        significance:3

        tag:policy-marker"""
        # TODO: custom vocabulary (other than 1)
        code = element.attrib.get('code')
        policy_marker_code = self.get_or_none(
            codelist_models.PolicyMarker, code=code)
        vocabulary = self.get_or_none(
            vocabulary_models.PolicyMarkerVocabulary,
            code=element.attrib.get(
                'vocabulary',
                '1'))
        vocabulary_uri = element.attrib.get('vocabulary-uri')
        significance = self.get_or_none(
            codelist_models.PolicySignificance,
            code=element.attrib.get('significance'))

        if not code:
            raise RequiredFieldError(
                "policy-marker",
                "code",
                "required attribute missing")

        # will never happen with the default above
        if not vocabulary:
            raise FieldValidationError(
                "policy-marker",
                "vocabulary",
                "not found on the accompanying code list",
                None,
                None,
                element.attrib.get('vocabulary'))

        if not policy_marker_code and vocabulary.code == '1':
            raise FieldValidationError(
                "policy-marker",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)
        elif vocabulary.code == '1' and significance is None:
            raise RequiredFieldError(
                "policy-marker",
                "significance",
                "significance is required when using OECD DAC CRS vocabulary")
        elif not policy_marker_code and vocabulary.code in ['99', '98']:
            # This is needed to create a new policy marker if related to vocabulary 99 or 98  # NOQA: E501
            # ref. http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/policy-marker/  # NOQA: E501

            code = slugify(code)
            policy_marker_code = self.get_or_none(models.PolicyMarker,
                                                  code=code)

            if not policy_marker_code:
                policy_marker_code = models.PolicyMarker()
                policy_marker_code.code = code
                policy_marker_code.name = 'Vocabulary 99 or 98'
                policy_marker_code.description = 'The policy marker is maintained by a reporting organisation'  # NOQA: E501
                policy_marker_code.save()

        elif not policy_marker_code:
            raise IgnoredVocabularyError(
                "policy-marker",
                "vocabulary",
                "non implemented vocabulary")

        activity = self.get_model('Activity')
        activity_policy_marker = models.ActivityPolicyMarker()
        activity_policy_marker.activity = activity
        activity_policy_marker.code = policy_marker_code
        activity_policy_marker.vocabulary = vocabulary
        activity_policy_marker.vocabulary_uri = vocabulary_uri
        activity_policy_marker.significance = significance

        self.register_model('ActivityPolicyMarker', activity_policy_marker)
        return element

    def iati_activities__iati_activity__policy_marker__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        activity_policy_marker = self.get_model('ActivityPolicyMarker')
        self.add_narrative(element, activity_policy_marker)
        return element

    def iati_activities__iati_activity__collaboration_type(self, element):
        """attributes:
        code:1

        tag:collaboration-type"""
        code = element.attrib.get('code')
        collaboration_type = self.get_or_none(
            codelist_models.CollaborationType, code=code)

        if not code:
            raise RequiredFieldError(
                "collaboration-type",
                "code",
                "required attribute missing")

        if not collaboration_type:
            raise FieldValidationError(
                "collaboration-type",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        activity = self.get_model('Activity')
        activity.collaboration_type = collaboration_type

        return element

    def iati_activities__iati_activity__default_flow_type(self, element):
        """attributes:
        code:10

        tag:default-flow-type"""
        code = element.attrib.get('code')
        default_flow_type = self.get_or_none(
            codelist_models.FlowType, code=code)

        if not code:
            raise RequiredFieldError(
                "default-flow-type",
                "code",
                "code is unspecified or invalid")

        if not default_flow_type:
            raise FieldValidationError(
                "default-flow-type",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        activity = self.get_model('Activity')
        activity.default_flow_type = default_flow_type

        return element

    def iati_activities__iati_activity__default_finance_type(self, element):
        """attributes:
        code:110

        tag:default-finance-type"""
        code = element.attrib.get('code')
        default_finance_type = self.get_or_none(
            codelist_models.FinanceType, code=code)

        if not code:
            raise RequiredFieldError(
                "default-finance-type",
                "code",
                "required attribute missing")

        if not default_finance_type:
            raise FieldValidationError(
                "default-finance-type",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        activity = self.get_model('Activity')
        activity.default_finance_type = default_finance_type

        return element

    def iati_activities__iati_activity__default_aid_type(self, element):
        """attributes:
        code:A01

        tag:default-aid-type"""
        code = element.attrib.get('code')
        default_aid_type = codelist_models.AidType.objects.filter(
            code=code,
        ).first()

        if not code:
            raise RequiredFieldError(
                "default-aid-type",
                "code",
                "required attribute missing")

        if not default_aid_type:
            raise FieldValidationError(
                "default-aid-type",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        activity = self.get_model('Activity')
        activity_default_aid_type = models.ActivityDefaultAidType()

        activity_default_aid_type.activity = activity
        activity_default_aid_type.aid_type = default_aid_type

        self.register_model(
            'ActivityDefaultAidType',
            activity_default_aid_type
        )

        return element

    def iati_activities__iati_activity__default_tied_status(self, element):
        """attributes:
        code:3

        tag:default-tied-status"""
        code = element.attrib.get('code')
        default_tied_status = self.get_or_none(
            codelist_models.TiedStatus, code=code)

        if not code:
            raise RequiredFieldError(
                "default-tied-status",
                "code",
                "code is unspecified or invalid")

        if not default_tied_status:
            raise FieldValidationError(
                "default-tied-status",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        activity = self.get_model('Activity')
        activity.default_tied_status = default_tied_status

        return element

    def iati_activities__iati_activity__budget(self, element):
        """attributes:
        type:1

        tag:budget"""
        # If the @type attribute is omitted, then BudgetType code 1 (Original)
        # is assumed
        budget_type_code = element.attrib.get('type', '1')
        budget_type = self.get_or_none(
            codelist_models.BudgetType, code=budget_type_code)
        # If the @status attribute is omitted, then BudgetStatus code 1
        # (Indicative) is assumed
        status_code = element.attrib.get('status', '1')
        status = self.get_or_none(
            codelist_models.BudgetStatus, code=status_code)
        activity = self.get_model('Activity')

        if not budget_type_code:
            raise RequiredFieldError(
                "budget",
                "type",
                "required attribute missing")

        if not budget_type:
            raise FieldValidationError(
                "budget",
                "type",
                "not found on the accompanying code list",
                None,
                None,
                budget_type_code)

        if not status_code:
            raise RequiredFieldError(
                "budget",
                "status",
                "required attribute missing")

        if not status:
            raise FieldValidationError(
                "budget",
                "status",
                "not found on the accompanying code list",
                None,
                None,
                status_code)

        budget = models.Budget()
        budget.activity = activity
        budget.type = budget_type
        budget.status = status

        self.register_model('Budget', budget)
        return element

    def iati_activities__iati_activity__budget__period_start(self, element):
        """attributes:
        iso-date:2014-01-01

        tag:period-start"""
        iso_date = element.attrib.get('iso-date')

        if not iso_date:
            raise RequiredFieldError(
                "budget/period-start",
                "iso-date",
                "required attribute missing")

        iso_date = self.validate_date(iso_date)

        if not iso_date:
            raise FieldValidationError(
                "budget/period-start",
                "iso-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('iso-date'))

        budget = self.get_model('Budget')
        budget.period_start = iso_date

        return element

    def iati_activities__iati_activity__budget__period_end(self, element):
        """attributes:
        iso-date:2014-12-31

        tag:period-end"""
        iso_date = element.attrib.get('iso-date')

        if not iso_date:
            raise RequiredFieldError(
                "budget/period-end",
                "iso-date",
                "required attribute missing")

        iso_date = self.validate_date(iso_date)

        if not iso_date:
            raise FieldValidationError(
                "budget/period-end",
                "iso-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('iso-date'))

        budget = self.get_model('Budget')
        budget.period_end = iso_date

        return element

    def iati_activities__iati_activity__budget__value(self, element):
        """attributes:
        currency:EUR
        value-date:2014-01-01

        tag:value"""
        currency = self.get_or_none(
            models.Currency, code=element.attrib.get('currency'))
        value = element.text
        decimal_value = self.guess_number('budget', value)

        if decimal_value is None:
            raise RequiredFieldError(
                "budget",
                "value",
                "required element missing")

        value_date = element.attrib.get('value-date')

        if not value_date:
            raise RequiredFieldError(
                "budget/value",
                "value-date",
                "required attribute missing")

        value_date = self.validate_date(value_date)

        if not value_date:
            raise FieldValidationError(
                "budget/value",
                "value-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('value-date'))

        currency = self._get_currency_or_raise('budget/value', currency)

        budget = self.get_model('Budget')
        budget.value_string = value
        budget.value = decimal_value
        budget.value_date = value_date
        budget.currency = currency

        if settings.CONVERT_CURRENCIES:
            budget.xdr_value = convert.currency_from_to(
                budget.currency_id, 'XDR', budget.value_date, budget.value)
            budget.usd_value = round(convert.currency_from_to(
                budget.currency_id, 'USD', budget.value_date, budget.value), 2)
            budget.eur_value = convert.currency_from_to(
                budget.currency_id, 'EUR', budget.value_date, budget.value)
            budget.gbp_value = convert.currency_from_to(
                budget.currency_id, 'GBP', budget.value_date, budget.value)
            budget.jpy_value = convert.currency_from_to(
                budget.currency_id, 'JPY', budget.value_date, budget.value)
            budget.cad_value = convert.currency_from_to(
                budget.currency_id, 'CAD', budget.value_date, budget.value)
            imf_url, usd_exchange_rate = convert.get_imf_url_and_exchange_rate(
                budget.currency_id, budget.value_date)
            budget.imf_url = imf_url
            budget.usd_exchange_rate = round(usd_exchange_rate,
                                             5) if isinstance(
                usd_exchange_rate, numbers.Number) else usd_exchange_rate

        return element

    def iati_activities__iati_activity__planned_disbursement(self, element):
        """attributes:
        type:1

        tag:planned-disbursement"""
        budget_type = self.get_or_none(
            codelist_models.BudgetType, code=element.attrib.get('type'))

        # if not budget_type: raise RequiredFieldError("type",
        # "planned-disbursement: type is required")

        activity = self.get_model('Activity')
        planned_disbursement = models.PlannedDisbursement()
        planned_disbursement.activity = activity
        planned_disbursement.type = budget_type

        self.register_model('PlannedDisbursement', planned_disbursement)

        return element

    def iati_activities__iati_activity__planned_disbursement__period_start(
            self, element):
        """attributes:
        iso-date:2014-01-01

        tag:period-start"""
        iso_date = element.attrib.get('iso-date')

        if not iso_date:
            raise RequiredFieldError(
                "planned-disbursement/period-start",
                "iso-date",
                "required attribute missing")

        iso_date = self.validate_date(iso_date)

        if not iso_date:
            raise FieldValidationError(
                "planned-disbursement/period-start",
                "iso-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('iso-date'))

        planned_disbursement = self.get_model('PlannedDisbursement')
        planned_disbursement.period_start = iso_date

        return element

    def iati_activities__iati_activity__planned_disbursement__period_end(
            self, element):
        """attributes:
        iso-date:2014-12-31

        tag:period-end"""
        iso_date = element.attrib.get('iso-date')

        if not iso_date:
            raise RequiredFieldError(
                "planned-disbursement/period-end",
                "iso-date",
                "required attribute missing")

        iso_date = self.validate_date(iso_date)

        if not iso_date:
            raise FieldValidationError(
                "planned-disbursement/period-end",
                "iso-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('iso-date'))

        planned_disbursement = self.get_model('PlannedDisbursement')
        planned_disbursement.period_end = iso_date

        return element

    def iati_activities__iati_activity__planned_disbursement__value(
            self, element):
        """attributes:
        currency:EUR
        value-date:2014-01-01

        tag:value"""

        currency = self.get_or_none(
            models.Currency, code=element.attrib.get('currency'))
        value = element.text
        decimal_value = self.guess_number('planned-disbursement', value)

        if decimal_value is None:
            raise RequiredFieldError(
                "planned-disbursement/value",
                "text",
                "required element missing")

        value_date = element.attrib.get('value-date')

        if not value_date:
            raise RequiredFieldError(
                "planned-disbursement/value",
                "value-date",
                "required attribute missing")

        value_date = self.validate_date(value_date)

        if not value_date:
            raise FieldValidationError(
                "planned-disbursement/value",
                "value-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('value-date'))

        currency = self._get_currency_or_raise(
            'planned-disbursement/value', currency)

        planned_disbursement = self.get_model('PlannedDisbursement')
        planned_disbursement.value_string = value
        planned_disbursement.value = decimal_value
        planned_disbursement.value_date = value_date
        planned_disbursement.currency = currency

        if settings.CONVERT_CURRENCIES:
            planned_disbursement.xdr_value = convert.currency_from_to(
                planned_disbursement.currency_id, 'XDR',
                planned_disbursement.value_date,
                planned_disbursement.value)
            planned_disbursement.usd_value = round(convert.currency_from_to(
                planned_disbursement.currency_id, 'USD',
                planned_disbursement.value_date,
                planned_disbursement.value), 2)
            planned_disbursement.eur_value = convert.currency_from_to(
                planned_disbursement.currency_id, 'EUR',
                planned_disbursement.value_date,
                planned_disbursement.value)
            planned_disbursement.gbp_value = convert.currency_from_to(
                planned_disbursement.currency_id, 'GBP',
                planned_disbursement.value_date,
                planned_disbursement.value)
            planned_disbursement.jpy_value = convert.currency_from_to(
                planned_disbursement.currency_id, 'JPY',
                planned_disbursement.value_date,
                planned_disbursement.value)
            planned_disbursement.cad_value = convert.currency_from_to(
                planned_disbursement.currency_id, 'CAD',
                planned_disbursement.value_date,
                planned_disbursement.value)
            imf_url, usd_exchange_rate = convert.get_imf_url_and_exchange_rate(
                planned_disbursement.currency_id,
                planned_disbursement.value_date)
            planned_disbursement.imf_url = imf_url
            planned_disbursement.usd_exchange_rate = round(
                usd_exchange_rate, 5) if isinstance(usd_exchange_rate,
                                                    numbers.Number) else usd_exchange_rate  # NOQA: E501
        return element

    def iati_activities__iati_activity__planned_disbursement__provider_org(
            self, element):
        """attributes:
        provider-activity-id:BB-BBB-123456789-1234AA
        ref:BB-BBB-123456789

        tag:provider-org"""

        return provider_org(
            self,
            self.get_model('PlannedDisbursement'),
            models.PlannedDisbursementProvider(),
            'planned_disbursement',
        )(element)

    def iati_activities__iati_activity__planned_disbursement__provider_org__narrative(  # NOQA: E501
            self, element):
        """attributes:

        tag:narrative"""
        model = self.get_model('PlannedDisbursementProvider')
        self.add_narrative(element, model)
        model.primary_name = self.get_primary_name(element, model.primary_name)
        return element

    def iati_activities__iati_activity__planned_disbursement__receiver_org(
            self, element):
        """attributes:
        receiver-activity-id:BB-BBB-123456789-1234AA
        ref:BB-BBB-123456789

        tag:receiver-org"""
        # TODO fix/test higher order parser or do this in the old fashion
        return receiver_org(
            self,
            self.get_model('PlannedDisbursement'),
            models.PlannedDisbursementReceiver(),
            'planned_disbursement',
        )(element)

    def iati_activities__iati_activity__planned_disbursement__receiver_org__narrative(  # NOQA: E501
            self, element):
        """attributes:

        tag:narrative"""
        model = self.get_model('PlannedDisbursementReceiver')
        self.add_narrative(element, model)
        model.primary_name = self.get_primary_name(element, model.primary_name)
        return element

    def iati_activities__iati_activity__capital_spend(self, element):
        """attributes:
        percentage:88.8

        tag:capital-spend"""
        activity = self.get_model('Activity')
        activity.capital_spend = element.attrib.get('percentage')

        return element

    def iati_activities__iati_activity__transaction(self, element):
        """attributes:
        ref:1234

        tag:transaction"""

        transaction_type = element.findall('transaction-date')
        if len(transaction_type) is 0:
            self.append_error(
                'RequiredFieldError',
                "transaction/transaction-date",
                "element",
                "required element missing",
                element.sourceline,
                "-")

        transaction_recipient_country = element.findall('recipient-country')
        if len(transaction_recipient_country) > 1:
            raise ParserError(
                "transaction",
                "recipient-country",
                "must occur no more than once")

        transaction_recipient_region = element.findall('recipient-region')
        if len(transaction_recipient_region) > 1:
            raise ParserError(
                "transaction",
                "recipient-region",
                "must occur no more than once")

        ref = element.attrib.get('ref')
        humanitarian = element.attrib.get('humanitarian')

        activity = self.get_model('Activity')
        transaction = transaction_models.Transaction()
        transaction.activity = activity
        transaction.ref = ref
        transaction.humanitarian = self.makeBoolNone(humanitarian)
        transaction.flow_type = self.get_model('Activity').default_flow_type
        transaction.finance_type = self.get_model(
            'Activity').default_finance_type
        transaction.aid_type = self.get_model('Activity').default_aid_type
        transaction.tied_status = self.get_model(
            'Activity').default_tied_status

        self.register_model('Transaction', transaction)
        return element

    def iati_activities__iati_activity__transaction__transaction_type(
            self, element):
        """attributes:
        code:1

        tag:transaction-type"""
        transaction_type = self.get_or_none(
            codelist_models.TransactionType,
            code=element.attrib.get('code'))

        if not transaction_type:
            # TODO; pop transaction model to prevent trying to save /
            # 'loss on save'?
            # That might save next sub elemens of the transaction to the
            # previous transaction?
            raise RequiredFieldError(
                "transaction/transaction-type",
                "code",
                "required attribute missing")

        transaction = self.get_model('Transaction')
        transaction.transaction_type = transaction_type

        return element

    def iati_activities__iati_activity__transaction__transaction_date(
            self, element):
        """attributes:
        iso-date:2012.02-01

        tag:transaction-date"""
        iso_date = element.attrib.get('iso-date')

        if not iso_date:
            raise RequiredFieldError(
                "transaction/transaction-date",
                "iso-date",
                "required attribute missing")

        iso_date = self.validate_date(iso_date)

        if not iso_date:
            raise FieldValidationError(
                "transaction/transaction-date",
                "iso-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('iso-date'))

        if iso_date > datetime.now():
            raise FieldValidationError(
                "transaction/transaction-date",
                "iso-date",
                "Must be today, or in the past",
                None,
                None,
                element.attrib.get('iso-date'))

        transaction = self.get_model('Transaction')
        transaction.transaction_date = iso_date

        return element

    def iati_activities__iati_activity__transaction__value(self, element):
        """attributes:
        currency:EUR
        value-date:2012.02-01

        tag:value"""
        currency = self.get_or_none(
            models.Currency, code=element.attrib.get('currency'))
        value = element.text
        decimal_value = self.guess_number('transaction', value)

        if decimal_value is None:
            raise RequiredFieldError(
                "transaction/value",
                "text",
                "Unspecified or invalid.")

        value_date = element.attrib.get('value-date')

        if not value_date:
            raise RequiredFieldError(
                "transaction/value",
                "value-date",
                "required attribute missing")

        value_date = self.validate_date(value_date)

        if not value_date:
            raise FieldValidationError(
                "transaction/value",
                "value-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('value-date'))

        # we don't want to farm out activity level elements/values to
        # transaction.
        # currency = self._get_currency_or_raise('transaction/value', currency)

        transaction = self.get_model('Transaction')
        transaction.value_string = value
        transaction.value = decimal_value
        transaction.value_date = value_date
        transaction.currency = currency

        if settings.CONVERT_CURRENCIES:
            transaction.xdr_value = convert.currency_from_to(
                transaction.currency_id, 'XDR', transaction.value_date,
                transaction.value)
            transaction.usd_value = round(convert.currency_from_to(
                transaction.currency_id, 'USD', transaction.value_date,
                transaction.value), 2)
            transaction.eur_value = convert.currency_from_to(
                transaction.currency_id, 'EUR', transaction.value_date,
                transaction.value)
            transaction.gbp_value = convert.currency_from_to(
                transaction.currency_id, 'GBP', transaction.value_date,
                transaction.value)
            transaction.jpy_value = convert.currency_from_to(
                transaction.currency_id, 'JPY', transaction.value_date,
                transaction.value)
            transaction.cad_value = convert.currency_from_to(
                transaction.currency_id, 'CAD', transaction.value_date,
                transaction.value)
            imf_url, usd_exchange_rate = convert.get_imf_url_and_exchange_rate(
                transaction.currency_id, transaction.value_date)
            transaction.imf_url = imf_url
            transaction.usd_exchange_rate = round(usd_exchange_rate, 5) if \
                isinstance(usd_exchange_rate, numbers.Number) else \
                usd_exchange_rate

        return element

    def iati_activities__iati_activity__transaction__description(
            self, element):
        """attributes:

        tag:description"""
        transaction = self.get_model('Transaction')

        description = transaction_models.TransactionDescription()
        description.transaction = transaction

        self.register_model('TransactionDescription', description)

        return element

    def iati_activities__iati_activity__transaction__description__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        transaction_description = self.get_model('TransactionDescription')
        self.add_narrative(element, transaction_description)
        return element

    def iati_activities__iati_activity__transaction__provider_org(
            self, element):
        """attributes:
        provider-activity-id:BB-BBB-123456789-1234AA
        ref:BB-BBB-123456789

        tag:provider-org"""

        return provider_org(
            self,
            self.get_model('Transaction'),
            transaction_models.TransactionProvider(),
            'transaction',
        )(element)

    def iati_activities__iati_activity__transaction__provider_org__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        # TODO: make this more transparant in data structure or handling
        # transaction_provider = self.get_model('Transaction', -2)
        transaction_provider = self.get_model('TransactionProvider')
        self.add_narrative(element, transaction_provider)

        transaction_provider.primary_name = self.get_primary_name(
            element, transaction_provider.primary_name)

        return element

    def iati_activities__iati_activity__transaction__receiver_org(
            self, element):
        """attributes:
        receiver-activity-id:AA-AAA-123456789-1234
        ref:AA-AAA-123456789

        tag:receiver-org"""

        # To do; test this!
        return receiver_org(
            self,
            self.get_model('Transaction'),
            transaction_models.TransactionReceiver(),
            'transaction',
        )(element)

    def iati_activities__iati_activity__transaction__receiver_org__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        # TODO: make this more transparant in data structure or handling
        # transaction_receiver = self.get_model('Transaction', -2)
        transaction_receiver = self.get_model('TransactionReceiver')
        self.add_narrative(element, transaction_receiver)

        transaction_receiver.primary_name = self.get_primary_name(
            element, transaction_receiver.primary_name)

        return element

    def iati_activities__iati_activity__transaction__disbursement_channel(
            self, element):
        """attributes:
        code:1

        tag:disbursement-channel"""
        code = element.attrib.get('code')
        disbursement_channel = self.get_or_none(
            codelist_models.DisbursementChannel, code=code)

        if not code:
            raise RequiredFieldError(
                "transaction/disbursement-channel",
                "code",
                "required attribute missing")

        if not disbursement_channel:
            raise RequiredFieldError(
                "transaction/disbursement-channel",
                "code",
                "not found on the accompanying code list")

        transaction = self.get_model('Transaction')
        transaction.disbursement_channel = disbursement_channel

        return element

    def iati_activities__iati_activity__transaction__sector(self, element):
        """attributes:
        vocabulary:2
        code:111

        tag:sector"""
        code = element.attrib.get('code')
        # TODO: make defaults more transparant, here: 'OECD-DAC default'
        vocabulary = self.get_or_none(
            vocabulary_models.SectorVocabulary,
            code=element.attrib.get(
                'vocabulary',
                '1'))
        vocabulary_uri = element.attrib.get('vocabulary-uri')

        if not code:
            raise RequiredFieldError(
                "transaction/sector",
                "code",
                "required attribute missing")

        if not vocabulary:
            raise FieldValidationError(
                "transaction/sector",
                "vocabulary",
                "not found on the accompanying code list",
                None,
                None,
                element.attrib.get('vocabulary'))

        sector = models.Sector.objects.filter(code=slugify(code),
                                              vocabulary=vocabulary).first()

        if not sector and vocabulary.code == '1':
            raise FieldValidationError(
                "transaction/sector",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        elif not sector and vocabulary.code in ['99', '98']:
            # This is needed to create a new sector if related to vocabulary 99 or 98  # NOQA: E501
            # ref. http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/sector/  # NOQA: E501

            code = slugify(code)
            sector = self.get_or_none(models.Sector, code=code)

            if not sector:
                sector = models.Sector()
                sector.code = code
                sector.vocabulary = vocabulary
                sector.name = 'Vocabulary 99 or 98'
                sector.description = 'The sector reported corresponds to a sector vocabulary maintained by the reporting organisation for this activity'  # NOQA: E501
                sector.save()

        elif not sector:
            raise IgnoredVocabularyError(
                "transaction/sector",
                "vocabulary",
                "non implemented vocabulary")

        transaction = self.get_model('Transaction')
        transaction_sector = transaction_models.TransactionSector()
        transaction_sector.transaction = transaction
        transaction_sector.reported_transaction = transaction
        transaction_sector.sector = sector
        transaction_sector.vocabulary = vocabulary
        transaction_sector.vocabulary_uri = vocabulary_uri
        transaction_sector.percentage = 100
        transaction_sector.reported_on_transaction = True

        self.register_model('TransactionSector', transaction_sector)
        return element

    def iati_activities__iati_activity__transaction__sector__narrative(
            self, element):
        """attributes:

        tag: narrative"""
        model = self.get_model('TransactionSector')
        self.add_narrative(element, model)
        return element

    def iati_activities__iati_activity__transaction__recipient_country(
            self, element):
        """attributes:
        code:AF

        tag:recipient-country"""
        code = element.attrib.get('code')
        country = self.get_or_none(Country, code=code)

        if not code:
            raise RequiredFieldError(
                "transaction/recipient-country",
                "code",
                "required attribute missing")

        if not country:
            raise FieldValidationError(
                "transaction/recipient-country",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        transaction = self.get_model('Transaction')
        transaction_country = transaction_models.TransactionRecipientCountry()
        transaction_country.transaction = transaction
        transaction_country.reported_transaction = transaction
        transaction_country.country = country
        transaction_country.percentage = 100
        transaction_country.reported_on_transaction = True

        self.register_model('TransactionRecipientCountry', transaction_country)
        return element

    def iati_activities__iati_activity__transaction__recipient_country__narrative(self, element):  # NOQA: E501
        """attributes:

        tag: narrative"""
        model = self.get_model('TransactionRecipientCountry')
        self.add_narrative(element, model)
        return element

    def iati_activities__iati_activity__transaction__recipient_region(
            self, element):
        """attributes:
        code:456
        vocabulary:1

        tag:recipient-region"""
        code = element.attrib.get('code')

        # TODO: make defaults more transparant, here: 'OECD-DAC default'
        vocabulary = self.get_or_none(
            vocabulary_models.RegionVocabulary,
            code=element.attrib.get(
                'vocabulary',
                '1'))
        vocabulary_uri = element.attrib.get('vocabulary-uri')
        region = Region.objects.filter(code=code,
                                       region_vocabulary=vocabulary).first()

        if not code:
            raise RequiredFieldError(
                "transaction/recipient-region",
                "code",
                "code is unspecified or invalid")

        if not vocabulary:
            raise RequiredFieldError(
                "transaction/recipient-region",
                "vocabulary",
                "not found on the accompanying code list")

        if not region and vocabulary.code == '1':
            raise FieldValidationError(
                "transaction/recipient-region",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)
        elif not region:
            raise IgnoredVocabularyError(
                "transaction/recipient-region",
                "code",
                "code is unspecified or invalid")

        transaction = self.get_model('Transaction')
        transaction_recipient_region = transaction_models\
            .TransactionRecipientRegion()
        transaction_recipient_region.transaction = transaction
        transaction_recipient_region.reported_transaction = transaction
        transaction_recipient_region.region = region
        transaction_recipient_region.vocabulary = vocabulary
        transaction_recipient_region.vocabulary_uri = vocabulary_uri
        transaction_recipient_region.percentage = 100
        transaction_recipient_region.reported_on_transaction = True

        self.register_model('TransactionRecipientRegion',
                            transaction_recipient_region)
        return element

    def iati_activities__iati_activity__transaction__recipient_region__narrative(self, element):  # NOQA:E501
        """attributes:

        tag: narrative"""
        model = self.get_model('TransactionRecipientRegion')
        self.add_narrative(element, model)
        return element

    def iati_activities__iati_activity__transaction__flow_type(self, element):
        """attributes:
        code:10

        tag:flow-type"""
        code = element.attrib.get('code')
        flow_type = self.get_or_none(codelist_models.FlowType, code=code)

        if not flow_type and not code:
            raise RequiredFieldError(
                "transaction/flow-type",
                "code",
                "required attribute missing")
        elif not flow_type:
            raise FieldValidationError(
                "transaction/flow-type",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        transaction = self.get_model('Transaction')
        transaction.flow_type = flow_type
        return element

    def iati_activities__iati_activity__transaction__finance_type(
            self, element):
        """attributes:
        code:110

        tag:finance-type"""
        code = element.attrib.get('code')
        finance_type = self.get_or_none(codelist_models.FinanceType, code=code)

        if not finance_type and not code:
            raise RequiredFieldError(
                "transaction/finance-type",
                "code",
                "required attribute missing")
        elif not finance_type:
            raise FieldValidationError(
                "transaction/finance-type",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        transaction = self.get_model('Transaction')
        transaction.finance_type = finance_type

        return element

    def iati_activities__iati_activity__transaction__aid_type(self, element):
        """attributes:
        code:A01

        tag:aid-type"""
        code = element.attrib.get('code')
        aid_type = codelist_models.AidType.objects.filter(
            code=code,
        ).first()

        if not aid_type and not code:
            raise RequiredFieldError(
                "transaction/aid-type",
                "code",
                "required attribute missing")
        elif not aid_type:
            raise FieldValidationError(
                "transaction/aid-type",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        transaction = self.get_model('Transaction')
        transaction.aid_type = aid_type

        return element

    def iati_activities__iati_activity__transaction__tied_status(
            self, element):
        """attributes:
        code:3

        tag:tied-status"""
        code = element.attrib.get('code')
        tied_status = self.get_or_none(codelist_models.TiedStatus, code=code)

        if not tied_status and not code:
            raise RequiredFieldError(
                "transaction/tied-status",
                "code",
                "required attribute missing")
        elif not tied_status:
            raise FieldValidationError(
                "transaction/tied-status",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        transaction = self.get_model('Transaction')
        transaction.tied_status = tied_status
        return element

    def iati_activities__iati_activity__document_link(self, element):
        """attributes:
        format:application/vnd.oasis.opendocument.text
        url:http:www.example.org/docs/report_en.odt

        tag:document-link"""
        url = element.attrib.get('url')

        file_format_code = element.attrib.get('format')
        file_format = self.get_or_none(
            codelist_models.FileFormat, code=file_format_code)

        if not url:
            raise RequiredFieldError(
                "document-link",
                "url",
                "required attribute missing")

        if not file_format_code:
            raise RequiredFieldError(
                "document-link",
                "format",
                "required attribute missing")

        if not file_format:
            raise FieldValidationError(
                "document-link",
                "format",
                "not found on the accompanying code list",
                None,
                None,
                file_format_code)

        activity = self.get_model('Activity')
        document_link = models.DocumentLink()
        document_link.activity = activity
        document_link.url = url
        document_link.file_format = file_format

        self.register_model('DocumentLink', document_link)
        return element

    def iati_activities__iati_activity__document_link__document_date(
            self, element):
        """attributes:
        format:application/vnd.oasis.opendocument.text
        url:http:www.example.org/docs/report_en.odt

        tag:document-link"""
        iso_date = element.attrib.get('iso-date')

        if not iso_date:
            raise RequiredFieldError(
                "document-link/document-date",
                "iso-date",
                "required attribute missing")

        iso_date = self.validate_date(iso_date)

        if not iso_date:
            raise FieldValidationError(
                "document-link/document-date",
                "iso-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('iso-date'))

        document_link = self.pop_model('DocumentLink')
        document_link.iso_date = iso_date

        self.register_model('DocumentLink', document_link)
        return element

    def iati_activities__iati_activity__document_link__title(self, element):
        """attributes:

        tag:title"""
        document_link = self.get_model('DocumentLink')
        document_link_title = models.DocumentLinkTitle()
        document_link_title.document_link = document_link

        self.register_model('DocumentLinkTitle', document_link_title)

        return element

    def iati_activities__iati_activity__document_link__title__narrative(
            self, element):
        """attributes:

        tag:narrative"""
        document_link_title = self.get_model('DocumentLinkTitle')
        self.add_narrative(element, document_link_title)
        return element

    def iati_activities__iati_activity__document_link__category(self, element):
        """attributes:
        code:A01

        tag:category"""
        code = element.attrib.get('code')
        category = self.get_or_none(
            codelist_models.DocumentCategory, code=code)

        if not code:
            raise RequiredFieldError(
                "document-link/category",
                "code",
                "required attribute missing")

        if not category:
            raise FieldValidationError(
                "document-link/category",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        document_link = self.get_model('DocumentLink')
        document_link_category = models.DocumentLinkCategory()
        document_link_category.document_link = document_link
        document_link_category.category = category

        self.register_model('DocumentLinkCategory', document_link_category)
        return element

    def iati_activities__iati_activity__document_link__language(self, element):
        """attributes:
        code:en

        tag:language"""
        code = element.attrib.get('code')
        language = self.get_or_none(codelist_models.Language, code=code)

        if not code:
            raise RequiredFieldError(
                "document-link/language",
                "code",
                "required attribute missing")

        if not language:
            raise FieldValidationError(
                "document-link/language",
                "code",
                "not found on the accompanying code list",
                None,
                None,
                code)

        document_link = self.get_model('DocumentLink')
        document_link_language = models.DocumentLinkLanguage()
        document_link_language.document_link = document_link
        document_link_language.language = language

        self.register_model('DocumentLinkLanguage', document_link_language)
        return element

    def iati_activities__iati_activity__related_activity(self, element):
        """attributes:
        ref:AA-AAA-123456789-6789
        type:1

        tag:related-activity"""
        ra_type_code = element.attrib.get('type')
        related_activity_type = self.get_or_none(
            codelist_models.RelatedActivityType, code=ra_type_code)
        ref = element.attrib.get('ref')

        if not ra_type_code:
            raise RequiredFieldError(
                "related-activity",
                "type",
                "required attribute missing")

        if not related_activity_type:
            raise FieldValidationError(
                "related-activity",
                "type",
                "not found on the accompanying code list",
                None,
                None,
                ra_type_code)

        if not ref:
            raise RequiredFieldError(
                "related-activity",
                "ref",
                "required attribute missing")

        activity = self.get_model('Activity')
        related_activity = models.RelatedActivity()
        # TODO: remove this field?
        related_activity.current_activity = activity
        related_activity.ref_activity = self.get_or_none(
            models.Activity, iati_identifier=ref)
        related_activity.ref = ref
        related_activity.type = related_activity_type

        # update existing related activity foreign keys, happens post save
        self.register_model('RelatedActivity', related_activity)
        return element

    # tag:legacy-data"""
    def iati_activities__iati_activity__legacy_data(self, element):
        activity = self.get_model('Activity')
        legacy_data = models.LegacyData()
        legacy_data.activity = activity
        legacy_data.name = element.attrib.get('name')
        legacy_data.value = element.attrib.get('value')
        legacy_data.iati_equivalent = element.attrib.get('iati-equivalent')

        self.register_model('LegacyData', legacy_data)

        return element

    def iati_activities__iati_activity__conditions(self, element):
        conditions_attached = element.attrib.get('attached')

        if not conditions_attached:
            raise RequiredFieldError(
                "conditions",
                "attached",
                "required attribute missing"
            )
        activity = self.get_model('Activity')
        conditions = models.Conditions()
        conditions.activity = activity
        conditions.attached = self.makeBool(conditions_attached)

        self.register_model('Conditions', conditions)
        return element

    # tag: condition"""
    def iati_activities__iati_activity__conditions__condition(self, element):

        condition_type_code = element.attrib.get('type')

        condition_type = self.get_or_none(codelist_models.ConditionType,
                                          code=condition_type_code)

        # 'type_code'is required attribute.

        if not condition_type_code:
            raise RequiredFieldError(
                "condition",
                "type",
                "required attribute missing."
            )

        #  'condition_type_code' value must be on the 'ConditionType codelist.
        #  so:'

        if not condition_type:
            raise FieldValidationError(
                "condition",
                "type",
                "not found on the accompanying codelist.",
                None,
                None,
                condition_type_code
            )
        conditions = self.get_model('Conditions')  # parent element
        condition = models.Condition()
        condition.conditions = conditions
        condition.type = condition_type

        self.register_model('Condition', condition)
        return element

    def iati_activities__iati_activity__conditions__condition__narrative(
            self, element):
        condition = self.get_model('Condition')
        self.add_narrative(element, condition)
        return element

    # tag:result"""
    def iati_activities__iati_activity__result(self, element):
        result_type_code = element.attrib.get('type')
        result_type = self.get_or_none(
            codelist_models.ResultType, code=result_type_code)
        aggregation_status = element.attrib.get('aggregation-status')

        if not result_type_code:
            raise RequiredFieldError(
                "result",
                "type",
                "required attribute missing")

        if not result_type:
            raise FieldValidationError(
                "result",
                "type",
                "not found on the accompanying code list",
                None,
                None,
                result_type_code)

        activity = self.get_model('Activity')
        result = models.Result()
        result.activity = activity
        result.type = result_type
        result.aggregation_status = self.makeBool(aggregation_status)

        self.register_model('Result', result)
        return element

    # """attributes:

    # tag:title"""
    def iati_activities__iati_activity__result__title(self, element):
        result = self.get_model('Result')
        result_title = models.ResultTitle()
        result_title.result = result

        self.register_model('ResultTitle', result_title)
        return element

    def iati_activities__iati_activity__result__title__narrative(
            self, element):
        # this points to Title
        title = self.get_model('ResultTitle')
        self.add_narrative(element, title)

        return element

    # """attributes:

    # tag:description"""
    def iati_activities__iati_activity__result__description(self, element):
        result = self.get_model('Result')
        result_description = models.ResultDescription()
        result_description.result = result

        self.register_model('ResultDescription', result_description)
        return element

    # """attributes:

    # tag:narrative"""
    def iati_activities__iati_activity__result__description__narrative(
            self, element):
        # this points to Description
        description = self.get_model('ResultDescription')
        self.add_narrative(element, description)

        return element

    def iati_activities__iati_activity__result__indicator(self, element):
        measure_code = element.attrib.get('measure')
        measure = self.get_or_none(
            codelist_models.IndicatorMeasure, code=measure_code)
        ascending = element.attrib.get('ascending', '1')

        if not measure_code:
            raise RequiredFieldError(
                "result/indicator",
                "measure",
                "required attribute missing")
        if not measure:
            raise RequiredFieldError(
                "result/indicator",
                "measure",
                "not found on the accompanying code list")

        result = self.get_model('Result')
        result_indicator = models.ResultIndicator()
        result_indicator.result = result
        result_indicator.measure = measure
        result_indicator.ascending = self.makeBool(ascending)

        self.register_model('ResultIndicator', result_indicator)
        return element

    def iati_activities__iati_activity__result__indicator__reference(
            self, element):
        vocabulary_code = element.attrib.get('vocabulary')
        vocabulary = self.get_or_none(
            vocabulary_models.IndicatorVocabulary, code=vocabulary_code)
        code = element.attrib.get('code')
        indicator_uri = element.attrib.get('indicator-uri')

        if not vocabulary_code:
            raise RequiredFieldError(
                "result/indicator/reference",
                "vocabulary",
                "required attribute missing")

        if not vocabulary:
            raise FieldValidationError(
                "result/indicator/reference",
                "vocabulary",
                "not found on the accompanying code list",
                None,
                None,
                vocabulary_code)

        if not code:
            raise RequiredFieldError(
                "result/indicator/reference",
                "code",
                "Unspecified or invalid.")

        result_indicator = self.get_model('ResultIndicator')
        result_indicator_reference = models.ResultIndicatorReference()
        result_indicator_reference.result_indicator = result_indicator
        result_indicator_reference.code = code
        result_indicator_reference.vocabulary = vocabulary
        result_indicator_reference.indicator_uri = indicator_uri

        self.register_model('ResultIndicatorReference',
                            result_indicator_reference)
        return element

    def iati_activities__iati_activity__result__indicator__title(
            self, element):
        result_indicator = self.get_model('ResultIndicator')
        result_indicator_title = models.ResultIndicatorTitle()
        result_indicator_title.result_indicator = result_indicator

        self.register_model('ResultIndicatorTitle', result_indicator_title)
        return element

    # """attributes:

    # tag:narrative"""
    def iati_activities__iati_activity__result__indicator__title__narrative(
            self, element):
        title = self.get_model('ResultIndicatorTitle')
        self.add_narrative(element, title)
        title.primary_name = self.get_primary_name(element, title.primary_name)

        return element

    # """attributes:

    # tag:description"""
    def iati_activities__iati_activity__result__indicator__description(
            self, element):
        result_indicator = self.get_model('ResultIndicator')
        result_indicator_description = models.ResultIndicatorDescription()
        result_indicator_description.result_indicator = result_indicator

        self.register_model('ResultIndicatorDescription',
                            result_indicator_description)
        return element

    # """attributes:

    # tag:narrative"""
    def iati_activities__iati_activity__result__indicator__description__narrative(self, element):  # NOQA: E501
        description = self.get_model('ResultIndicatorDescription')
        self.add_narrative(element, description)

        return element

    # tag:baseline"""
    def iati_activities__iati_activity__result__indicator__baseline(
            self, element):
        year = element.attrib.get('year')
        iso_date = element.attrib.get('iso-date', None)
        value = element.attrib.get('value')

        try:
            year = int(year)
            if not (year > 1900 and year < 2200):
                year = None
        except Exception as e:
            year = None

        if not year:
            raise RequiredFieldError(
                "result/indicator/baseline",
                "year",
                "required attribute missing (should be of type \
                        xsd:positiveInteger with format (yyyy))")

        if value is None:
            raise RequiredFieldError(
                "result/indicator/baseline",
                "value",
                "required attribute missing.")

        result_indicator = self.get_model("ResultIndicator")
        result_indicator_baseline = models.ResultIndicatorBaseline()

        result_indicator_baseline.result_indicator = result_indicator
        result_indicator_baseline.iso_date = iso_date
        result_indicator_baseline.year = year
        result_indicator_baseline.value = value if value else None  # can be
        # None

        self.register_model('ResultIndicatorBaseline',
                            result_indicator_baseline)
        return element

    # """attributes:

    # tag:comment"""
    def iati_activities__iati_activity__result__indicator__baseline__comment(
            self, element):
        result_indicator_baseline = self.get_model('ResultIndicatorBaseline')
        result_indicator_baseline_comment = \
            models.ResultIndicatorBaselineComment()
        result_indicator_baseline_comment.result_indicator_baseline = \
            result_indicator_baseline

        self.register_model('ResultIndicatorBaselineComment',
                            result_indicator_baseline_comment)
        return element

    # """attributes:

    # tag:narrative"""
    def iati_activities__iati_activity__result__indicator__baseline__comment__narrative(  # NOQA: E501
            self, element):
        baseline_comment = self.get_model('ResultIndicatorBaselineComment')
        self.add_narrative(element, baseline_comment)

        return element

    # """attributes:

    # tag:period"""
    def iati_activities__iati_activity__result__indicator__period(
            self, element):

        # do validation on "Period-start must be before period-end"
        try:
            start_date = element.find('period-start').get('iso-date')
            end_date = element.find('period-end').get('iso-date')

            if start_date and end_date:
                start_date_iso = self.validate_date(start_date)
                end_date_iso = self.validate_date(end_date)

                if start_date_iso\
                        and end_date_iso and (start_date_iso > end_date_iso):

                    raise FieldValidationError(
                        "result/indicator/period/period-start",
                        "iso-date",
                        "Period-start must be before period-end",
                        None,
                        None,
                        "start date: {} , end_date: {}".format(
                            start_date, end_date))

        except AttributeError:
            # period start/end dont exist
            pass

        # start with actual functionality for period

        result_indicator = self.get_model('ResultIndicator')
        result_indicator_period = models.ResultIndicatorPeriod()
        result_indicator_period.result_indicator = result_indicator

        self.register_model('ResultIndicatorPeriod', result_indicator_period)
        return element

    # tag:period-start"""
    def iati_activities__iati_activity__result__indicator__period__period_start(self, element):  # NOQA: E501
        iso_date = element.attrib.get('iso-date')

        if not iso_date:
            raise RequiredFieldError(
                "result/indicator/period/period-start",
                "iso-date",
                "required attribute missing")

        iso_date = self.validate_date(iso_date)

        if not iso_date:
            raise FieldValidationError(
                "result/indicator/period/period-start",
                "iso-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('iso-date'))

        result_indicator_period = self.pop_model('ResultIndicatorPeriod')
        result_indicator_period.period_start = iso_date

        self.register_model('ResultIndicatorPeriod', result_indicator_period)
        return element

    # tag:period-end"""
    def iati_activities__iati_activity__result__indicator__period__period_end(
            self, element):

        iso_date = element.attrib.get('iso-date')

        if not iso_date:
            raise RequiredFieldError(
                "result/indicator/period/period-end",
                "iso-date",
                "required attribute missing")

        iso_date = self.validate_date(iso_date)

        if not iso_date:
            raise FieldValidationError(
                "result/indicator/period/period-end",
                "iso-date",
                "iso-date not of type xsd:date",
                None,
                None,
                element.attrib.get('iso-date'))

        result_indicator_period = self.pop_model('ResultIndicatorPeriod')
        result_indicator_period.period_end = iso_date

        self.register_model('ResultIndicatorPeriod', result_indicator_period)
        return element

    def iati_activities__iati_activity__result__indicator__period__target(
            self, element):
        value = element.attrib.get('value')
        # TODO, 'guess number'

        try:
            value = Decimal(value)
        except Exception as e:
            value = None   # value could be None according to
            # iati-specification but we should not add None to our database
            # otherwise it would raise error in endpoint aggregation.
            # Example API call:
            # /api/results/aggregations/?group_by=result_indicator_title
            # &aggregations=actuals&format=json
            # We have updated codes in api aggregation to enable null

        result_indicator_period = self.get_model('ResultIndicatorPeriod')
        result_indicator_period_target = models.ResultIndicatorPeriodTarget()
        result_indicator_period_target.value = value
        result_indicator_period_target.result_indicator_period = \
            result_indicator_period

        self.register_model('ResultIndicatorPeriodTarget',
                            result_indicator_period_target)
        return element

    def iati_activities__iati_activity__result__indicator__period__target__location(self, element):  # NOQA: E501

        ref = element.attrib.get('ref')

        if not ref:
            raise RequiredFieldError(
                "result/indicator/period/period/target/location",
                "ref",
                "required attribute missing")

        locations = self.get_model_list('Location')
        location = []

        if locations:
            location = list(filter(lambda x: x.ref == ref, locations))

        if not len(location):
            raise FieldValidationError(
                "result/indicator/period/period/target/location",
                "ref",
                "referenced location does not exist in a location element of \
                        this activity",
                None,
                None,
                ref)

        period_target = self.get_model('ResultIndicatorPeriodTarget')
        target_location = models.ResultIndicatorPeriodTargetLocation()
        target_location.result_indicator_period_target = period_target
        target_location.ref = ref
        target_location.location = location[0]

        self.register_model(
            'ResultIndicatorPeriodTargetLocation', target_location)
        return element

    def iati_activities__iati_activity__result__indicator__period__target__dimension(  # NOQA: E501
            self, element):

        name = element.attrib.get('name')
        value = element.attrib.get('value')

        if not name:
            raise RequiredFieldError(
                "result/indicator/period/period/target/dimension",
                "name",
                "required attribute missing")

        if value is None:
            raise RequiredFieldError(
                "result/indicator/period/period/target/dimension",
                "value",
                "required attribute missing")

        period_target = self.get_model('ResultIndicatorPeriodTarget')

        target_dimension = models.ResultIndicatorPeriodTargetDimension()
        target_dimension.result_indicator_period_target = period_target
        target_dimension.name = name
        target_dimension.value = value

        self.register_model(
            'ResultIndicatorPeriodTargetDimension', target_dimension)
        return element

    def iati_activities__iati_activity__result__indicator__period__target__comment(self, element):  # NOQA: E501
        result_indicator_period_target = \
            self.get_model('ResultIndicatorPeriodTarget')
        result_indicator_period_target_comment = models\
            .ResultIndicatorPeriodTargetComment()
        result_indicator_period_target_comment\
            .result_indicator_period_target = result_indicator_period_target

        self.register_model(
            'ResultIndicatorPeriodTargetComment',
            result_indicator_period_target_comment)
        return element

    # """attributes:

    # tag:narrative"""
    def iati_activities__iati_activity__result__indicator__period__target__comment__narrative(  # NOQA: E501
            self, element):
        period_target_comment = self.get_model(
            'ResultIndicatorPeriodTargetComment')
        self.add_narrative(element, period_target_comment)

        return element

    # """attributes:
    # value:11

    # tag:actual"""
    def iati_activities__iati_activity__result__indicator__period__actual(
            self, element):
        value = element.attrib.get('value')

        try:
            value = Decimal(value)
        except Exception as e:
            value = None  # value could be None according to
            # iati-specification but we should not add None to our database
            # otherwise it would raise error in endpoint aggregation.
            # Example API call:
            # /api/results/aggregations/?group_by=result_indicator_title
            # &aggregations=actuals&format=json
            # we have updated codes in api aggregation to enable null

        result_indicator_period = self.get_model('ResultIndicatorPeriod')

        result_indicator_period_actual = models.ResultIndicatorPeriodActual()
        result_indicator_period_actual.result_indicator_period = \
            result_indicator_period
        result_indicator_period_actual.value = value

        self.register_model('ResultIndicatorPeriodActual',
                            result_indicator_period_actual)
        return element

    def iati_activities__iati_activity__result__indicator__period__actual__location(self, element):  # NOQA: E501

        ref = element.attrib.get('ref')

        if not ref:
            raise RequiredFieldError(
                "result/indicator/period/actual/location",
                "ref",
                "required attribute missing")

        locations = self.get_model_list('Location')
        location = list(filter(lambda x: x.ref == ref, locations))

        if not len(location):
            raise FieldValidationError(
                "result/indicator/period/actual/location",
                "ref",
                "referenced location does not exist in a location element of \
                        this activity",
                None,
                None,
                ref)

        period_actual = self.get_model('ResultIndicatorPeriodActual')

        actual_location = models.ResultIndicatorPeriodActualLocation()
        actual_location.result_indicator_period_actual = period_actual
        actual_location.ref = ref
        actual_location.location = location[0]

        self.register_model(
            'ResultIndicatorPeriodActualLocation', actual_location)
        return element

    def iati_activities__iati_activity__result__indicator__period__actual__dimension(  # NOQA: E501
            self, element):

        name = element.attrib.get('name')
        value = element.attrib.get('value')

        if not name:
            raise RequiredFieldError(
                "result/indicator/period/actual/dimension",
                "name",
                "required attribute missing")

        if value is None:
            raise RequiredFieldError(
                "result/indicator/period/actual/dimension",
                "value",
                "required attribute missing")

        period_actual = self.get_model('ResultIndicatorPeriodActual')

        actual_dimension = models.ResultIndicatorPeriodActualDimension()
        actual_dimension.result_indicator_period_actual = period_actual
        actual_dimension.name = name
        actual_dimension.value = value

        self.register_model(
            'ResultIndicatorPeriodActualDimension', actual_dimension)
        return element

    def iati_activities__iati_activity__result__indicator__period__actual__comment(self, element):  # NOQA: E501
        result_indicator_period_actual = \
            self.get_model('ResultIndicatorPeriodActual')
        result_indicator_period_actual_comment = models\
            .ResultIndicatorPeriodActualComment()
        result_indicator_period_actual_comment\
            .result_indicator_period_actual = result_indicator_period_actual

        self.register_model(
            'ResultIndicatorPeriodActualComment',
            result_indicator_period_actual_comment)
        return element

    def iati_activities__iati_activity__result__indicator__period__actual__comment__narrative(  # NOQA: E501
            self, element):
        period_actual_comment = self.get_model(
            'ResultIndicatorPeriodActualComment')
        self.add_narrative(element, period_actual_comment)

        return element

    def iati_activities__iati_activity__crs_add(self, element):
        """New (optional) <crs-add> element inside
          <iati-activities/iati-activity> element in 2.02
        """
        # FIXME: should database relation be changed to OnetoOne?? see #981
        # we need to check if this element occurs more than once in  the
        # parent element, which is <iati-activity>
        activity = self.get_model('Activity')
        if 'CrsAdd' in self.model_store:
            for crs_add in self.model_store['CrsAdd']:
                if crs_add.activity == activity:
                    raise ParserError("Activity", "CrsAdd", "must occur no "
                                                            "more than once")

        # 'channel-code' must not occur no more than once within each parent
        # element.
        channel_code_list = element.xpath('channel-code')

        if len(channel_code_list) > 1:
            raise ParserError(
                "crs-add",
                "channel-code",
                "must occur no more than once")
        elif len(channel_code_list) == 1:
            channel_code = self.get_or_none(codelist_models.CRSChannelCode,
                                            code=channel_code_list[0].text)
            if not channel_code:
                raise FieldValidationError(
                    "iati-activities/iati-activity/crs-add",
                    "channel-code",
                    "not found on the accompanying code list",
                    None,
                    None,
                    channel_code)
        else:
            channel_code = None  # 'channel-code'is optional.

        crs_add = models.CrsAdd()
        crs_add.activity = activity
        crs_add.channel_code = channel_code
        self.register_model('CrsAdd', crs_add)
        return element

    def iati_activities__iati_activity__crs_add__other_flags(self, element):
        """"A method to save (optional) <other-flags> element and its
        attributes inside <crs-add> element in 2.02
        """
        code = element.attrib.get('code')
        significance = element.attrib.get('significance')
        if not code:
            raise RequiredFieldError(
                "crs-add/other-flags",
                "code",
                "required attribute missing."
            )
        if not significance:
            raise RequiredFieldError(
                "crs-add/other-flags",
                "significance",
                "required attribute missing."
            )
        code_in_codelist = self.get_or_none(codelist_models.OtherFlags,
                                            code=code)
        if code_in_codelist is None:
            raise FieldValidationError(
                "crs-add/other-flags",
                "code",
                "not found on the accompanying code list.",
                None,
                None,
                code)
        crs_add = self.get_model('CrsAdd')
        other_flags = models.CrsAddOtherFlags()
        other_flags.other_flags = code_in_codelist
        other_flags.significance = self.makeBool(significance)
        other_flags.crs_add = crs_add
        self.register_model('CrsAddOtherFlags', other_flags)
        return element

    def iati_activities__iati_activity__crs_add__loan_terms(self, element):
        '''New (optional) <loan-terms> element for <crs-add> element
           inside <iati-activity> element in 2.02
        '''

        rate_1 = element.attrib.get('rate-1')
        rate_2 = element.attrib.get('rate-2')

        # repayment_type_code is of type list.
        repayment_type_code = element.xpath('repayment-type')
        if len(repayment_type_code) > 1:
            raise ParserError("loan-terms", "repayment-type",
                              "must occur no more than once.")
        elif len(repayment_type_code) == 1:
            # repayment_type_code is of type string.
            repayment_type_code = repayment_type_code[
                0].attrib.get('code')
            if not repayment_type_code:  # 'code'is required.
                raise RequiredFieldError(
                    "repayment-type",
                    "code",
                    "required attribute missing."
                )

            # repayment_type_code is of type LoanRepaymentType object.
            repayment_type_code = self.get_or_none(
                codelist_models.LoanRepaymentType, code=repayment_type_code)
            if repayment_type_code is None:
                raise FieldValidationError(
                    "repayment-type",
                    "code",
                    "not found on the accompanying codelist",
                    None,
                    None,
                    repayment_type_code)

        # repayment_plan_code is of type list.
        repayment_plan_code = element.xpath('repayment-plan')
        if len(repayment_plan_code) > 1:
            raise ParserError("loan-terms", "repayment-plan",
                              "must occur no more than once.")
        elif len(repayment_plan_code) == 1:
            # repayment_plan_code is of type string.
            repayment_plan_code = repayment_plan_code[0].attrib.get('code')
            if not repayment_plan_code:
                raise RequiredFieldError(
                    "repayment-plan",
                    "code",
                    "required attribute missing."
                )
            # repayment_plan_code is of type LoanRepaymentPeriod object.
            repayment_plan_code = self.get_or_none(
                codelist_models.LoanRepaymentPeriod,
                code=repayment_plan_code)
            if repayment_plan_code is None:
                raise FieldValidationError(
                    "repayment-plan",
                    "code",
                    "not found on the accompanying codelist.",
                    None,
                    None,
                    repayment_plan_code)

        # commitment_iso_date is of type list.
        commitment_iso_date = element.xpath('commitment-date')
        if len(commitment_iso_date) > 1:
            raise ParserError("loan-terms", "commitment-date",
                              "must occur no more than once.")
        elif len(commitment_iso_date) == 1:
            # commitment_iso_date is of type string.
            commitment_iso_date = commitment_iso_date[0].attrib.get(
                'iso-date')
            if not commitment_iso_date:
                raise RequiredFieldError(
                    "commitment-date",
                    "iso-date",
                    "required attribute missing."
                )
            # commitment_iso_date  is of type datetime.datetime
            commitment_iso_date = self.validate_date(commitment_iso_date)
            if commitment_iso_date is None:
                raise FieldValidationError(
                    "commitment-date",
                    "iso-date",
                    "iso-date is not in correct range.",
                    None,
                    None,
                )

        # repayment_firs_iso_date is of type list.
        repayment_first_iso_date = element.xpath('repayment-first-date')
        if len(repayment_first_iso_date) > 1:
            raise ParserError("loan-terms", "repayment-first-date",
                              "must occur no more than once.")
        elif len(repayment_first_iso_date) == 1:
            # repayment_first_iso_date is of type string.
            repayment_first_iso_date = repayment_first_iso_date[0].attrib.get(
                'iso-date')
            if not repayment_first_iso_date:
                raise RequiredFieldError(
                    "repayment-first-date",
                    "iso-date",
                    "required attribute missing."
                )
            # repayment_first_iso_date is of type datetime.datetime
            repayment_first_iso_date = self.validate_date(
                repayment_first_iso_date)
            if repayment_first_iso_date is None:
                raise FieldValidationError(
                    "repayment-first-date",
                    "iso-date",
                    "iso-date is not in correct range.",
                    None,
                    None,
                )

        # repayment_final_iso_date is of type list.
        repayment_final_iso_date = element.xpath('repayment-final-date')
        if len(repayment_final_iso_date) > 1:
            raise ParserError("loan-terms", "repayment-final-date",
                              "must occur no more than once.")
        elif len(repayment_final_iso_date) == 1:
            # repayment_final_iso_date is of type string.
            repayment_final_iso_date = repayment_final_iso_date[0].attrib.get(
                'iso-date')
            if not repayment_final_iso_date:
                raise RequiredFieldError(
                    "repayment-final-date",
                    "iso-date",
                    "required attribute missing."
                )
            # repayment_final_iso_date is of type datetime.datetime.
            repayment_final_iso_date = self.validate_date(
                repayment_final_iso_date)
            if repayment_final_iso_date is None:
                raise FieldValidationError(
                    "repayment-final-date",
                    "iso-date",
                    "iso-date is not in correct range.",
                    None,
                    None,
                )

        crs_add = self.get_model('CrsAdd')
        crs_add_loan_terms = models.CrsAddLoanTerms()
        crs_add_loan_terms.crs_add = crs_add
        crs_add_loan_terms.rate_1 = self.guess_number('loan-terms', rate_1)
        crs_add_loan_terms.rate_2 = self.guess_number('loan-terms', rate_2)
        crs_add_loan_terms.repayment_type = repayment_type_code
        crs_add_loan_terms.repayment_plan = repayment_plan_code
        crs_add_loan_terms.commitment_date = commitment_iso_date
        crs_add_loan_terms.repayment_first_date = repayment_first_iso_date
        crs_add_loan_terms.repayment_final_date = repayment_final_iso_date
        self.register_model('CrsAddLoanTerms', crs_add_loan_terms)
        return element

    def iati_activities__iati_activity__crs_add__loan_status(self, element):

        year = element.attrib.get('year')
        currency = self.get_or_none(codelist_models.Currency,
                                    code=element.attrib.get('currency'))
        value_date = element.attrib.get('value-date')

        # @year is required field.
        if not year:
            raise RequiredFieldError(
                "CrsAddLoanStatus", "year", "required field missing.")

        # @year is must be of type xsd:decimal but here it is checked if
        # integer as it is a year.
        if not self.isInt(year):
            raise FieldValidationError(
                "CrsAddLoanStatus",
                "year",
                "year not of type xsd:decimal",
                None,
                None,
                element.attrib.get('year'))

        # @currency is required unless the iati-activity/@default-currency
        # is present and applies. This value must be on the Currency codelist.
        if currency is None:
            currency = self._get_currency_or_raise(
                "CrsAddLoanStatus", currency)

        # @value-date is required field.
        if not value_date:
            raise RequiredFieldError(
                "CrsAddLoanStatus", "value-date", "required field missing.")

        # @value-date must be of type xsd:date and in the correct range.
        value_date = self.validate_date(value_date)
        if value_date is None:
            raise FieldValidationError(
                "CrsAddLoanStatus",
                "value-date",
                "is not in correct range.",
                None,
                None,
            )

        # interest-received must occur no more than once. The text in this
        # element must be of type xsd:decimal.
        interest_received = element.xpath('interest-received')
        if len(interest_received) > 1:
            raise ParserError("CrsAddLoanStatus", "interest-received",
                              "must occur no more than once.")
        elif len(interest_received) == 1:
            # interest_received is of type string.
            interest_received = interest_received[0].text
            # text is optional so we check if it is decimal only when it
            # presents.
            if interest_received:
                # interest_received is of type decimal. Otherwise
                # guess_number() method would raise an error.
                interest_received = self.guess_number(
                    "CrsAddLoanStatus", interest_received)

        # principal-outstanding must occur no more than once. The text in
        # this element must be of type xsd:decimal.
        principal_outstanding = element.xpath('principal-outstanding')
        if len(principal_outstanding) > 1:
            raise ParserError("CrsAddLoanStatus", "principal-outstanding",
                              "must occur no more than once.")
        elif len(principal_outstanding) == 1:
            # principal-outstanding is of type string.
            principal_outstanding = principal_outstanding[0].text
            # text is optional so we check if it is decimal only when it
            # presents.
            if principal_outstanding:
                # principal-outstanding must be of type decimal. Otherwise
                # guess_number() method would raise error.
                principal_outstanding = self.guess_number(
                    "CrsAddLoanStatus", principal_outstanding)

        # principal-arrears must occur no more than once. The text in this
        # element must be of type xsd:decimal.
        principal_arrears = element.xpath('principal-arrears')
        if len(principal_arrears) > 1:
            raise ParserError("CrsAddLoanStatus", "principal-arrears",
                              "must occur no more than once.")
        elif len(principal_arrears) == 1:
            # Here principal-arrears is of type string.
            principal_arrears = principal_arrears[0].text
            # text is optional so we check if it is decimal only when it
            # presents.
            if principal_arrears:
                # principal-arrears is of type decimal. Otherwise
                # guess_number() method would raise error.
                principal_arrears = self.guess_number(
                    "CrsAddLoanStatus", principal_arrears)

        # interest-arrears must occur no more than once. The text in this
        # element must be of type xsd:decimal.
        interest_arrears = element.xpath('interest-arrears')
        if len(interest_arrears) > 1:
            raise ParserError("CrsAddLoanStatus", "interest-arrears",
                              "must occur no more than once.")
        elif len(interest_arrears) == 1:
            # Here interest-arrears is of type string.
            interest_arrears = interest_arrears[0].text
            # text is optional so we check if it is decimal only when it
            # presents.
            if interest_arrears:
                # interest-arrears is of type decimal. Otherwise
                # guess_number() method would raise error.
                interest_arrears = self.guess_number(
                    "CrsAddLoanStatus", interest_arrears)

        crs_add = self.get_model("CrsAdd")
        crs_add_loan_status = models.CrsAddLoanStatus()
        crs_add_loan_status.crs_add = crs_add
        crs_add_loan_status.year = year
        crs_add_loan_status.currency = currency
        crs_add_loan_status.value_date = value_date
        crs_add_loan_status.interest_received = interest_received
        crs_add_loan_status.principal_outstanding = principal_outstanding
        crs_add_loan_status.principal_arrears = principal_arrears
        crs_add_loan_status.interest_arrears = interest_arrears

        self.register_model("CrsAddLoanStatus", crs_add_loan_status)
        return element

    def iati_activities__iati_activity__fss(self, element):
        """"(optional) <fss> element inside <iati-activities/iati-activity>
        element in 2.02
        """
        # FIXME: should database relation be changed to OnetoOne?? see #964
        activity = self.get_model('Activity')
        if 'Fss' in self.model_store:
            for fss in self.model_store['Fss']:
                if fss.activity == activity:
                    raise ParserError("Activity", "Fss", "must occur no more "
                                                         "than once.")

        extraction_date = element.attrib.get('extraction-date')
        priority = element.attrib.get('priority')
        phaseout_year = element.attrib.get('phaseout-year')

        if not extraction_date:
            raise RequiredFieldError(
                "fss",
                "extraction-date",
                "required attribute missing"
            )
        extraction_date = self.validate_date(extraction_date)

        if not extraction_date:
            raise FieldValidationError(
                "fss",
                "extraction-date",
                "extraction-date not of type xsd:date",
                None,
                None,
                element.attrib.get('extraction-date'))

        # phaseout_year must be of type xsd:decimal but here it is checked if
        # it is integer as it is year.

        if phaseout_year is not None:  # 'phasoutout_year' is an optional
            # attribute.
            if not self.isInt(phaseout_year):
                raise FieldValidationError(
                    "fss",
                    "phaseout-year",
                    "phaseout-year not of type xsd:decimal",
                    None,
                    None,
                    element.attrib.get('phaseout-year'))

        priority_bool = self.makeBool(priority)
        fss = models.Fss()
        fss.activity = activity
        fss.extraction_date = extraction_date
        fss.phaseout_year = phaseout_year
        fss.priority = priority_bool

        self.register_model('Fss', fss)
        return element

    def iati_activities__iati_activity__fss__forecast(self, element):
        year = element.attrib.get('year')
        currency = self.get_or_none(models.Currency,
                                    code=element.attrib.get('currency'))
        value_date = element.attrib.get('value-date')
        value = element.text

        if not year:  # year is required field.
            raise RequiredFieldError(
                "iati-activity/fss/forecast",
                "year",
                "required attribute missing"
            )
        else:
            # year must be of type xsd:decimal but here it is checked
            # if it is integer as it is year.
            if not self.isInt(year):
                raise FieldValidationError(
                    "forecast",
                    "year",
                    "year not of correct type",
                    None,
                    None,
                    element.attrib.get('year'))

        # value_date is optional field.
        if value_date:
            value_date = self.validate_date(value_date)
            if value_date is None:
                raise FieldValidationError(
                    "budget/value",
                    "value-date",
                    "value-date not in correct range",
                    None,
                    None,
                    element.attrib.get('value-date'))

        if not value:
            raise RequiredFieldError(
                "forcast",
                "value",
                "required element missing")

        if not currency:
            currency = self._get_currency_or_raise('forecast', currency)

        decimal_value = self.guess_number('forecast', value)
        fss = self.get_model('Fss')
        fss_forecast = models.FssForecast()
        fss_forecast.value = decimal_value
        fss_forecast.year = year
        fss_forecast.currency = currency
        fss_forecast.value_date = value_date
        fss_forecast.fss = fss
        self.register_model('FssForecast', fss_forecast)
        return element

    def post_save_models(self):
        """Perform all actions that need to happen after a single activity's
        been parsed."""
        activity = self.get_model('Activity')

        # the model was not saved
        if not activity or not activity.pk:
            return False

        participating_organisations = self.get_model_list(
            'ActivityParticipatingOrganisation')

        post_save.set_related_activities(activity)
        post_save.set_participating_organisation_activity_id(
            participating_organisations)
        post_save.set_transaction_provider_receiver_activity(activity)
        post_save.set_derived_activity_dates(activity)
        # post_save.set_activity_aggregations(activity)
        post_save.update_activity_search_index(activity)
        # post_save.set_sector_transaction(activity)
        post_save.set_sector_budget(activity)

    def post_save_file(self, dataset, activities_to_keep):
        """Perform all actions that need to happen after a single IATI
        datasets has been parsed.

        Keyword arguments:
        dataset -- the Dataset object
        """
        self.delete_removed_activities(dataset, activities_to_keep)

    def delete_removed_activities(self, dataset, activities_to_keep):
        """ Delete activities that were not found in the dataset any longer

        Keyword arguments:
        dataset -- the Dataset object

        Used variables:
        activity.last_updated_model -- the datetime at which this activity
        was last saved
        self.parse_start_datetime -- the datetime at which parsing this
        dataset started
        """
        models.Activity.objects.filter(
            dataset=dataset,
            last_updated_model__lt=self.parse_start_datetime)\
            .exclude(iati_identifier__in=activities_to_keep).delete()

    def post_save_validators(self, dataset):

        for a in models.Activity.objects.filter(dataset=dataset):

            post_save_validators.identifier_correct_prefix(self, a)
            post_save_validators.geo_percentages_add_up(self, a)
            post_save_validators.sector_percentages_add_up(self, a)
            post_save_validators.use_sector_or_transaction_sector(self, a)
            post_save_validators.use_direct_geo_or_transaction_geo(self, a)

        post_save_validators.unfound_identifiers(self, dataset)
        post_save_validators.transactions_at_multiple_levels(self, dataset)
