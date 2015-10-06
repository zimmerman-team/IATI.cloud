from genericXmlParser import XMLParser
from django.db.models import Model
from django.contrib.gis.geos import GEOSGeometry, Point
from iati import models
from iati.transaction import models as transaction_models
from iati_codelists import models as codelist_models
from iati_vocabulary import models as vocabulary_models
from geodata.models import Country, Region
from iati.deleter import Deleter
from iati_synchroniser.exception_handler import exception_handler
from re import sub
import hashlib
import dateutil.parser
import time
import datetime
import re
import unicodedata

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')

def _cache_codelists():
    pass

class Parse(XMLParser):
    #version of IATI standard
    default_lang = 'en'
    iati_identifier = ''
    validated_reporters = ['GB-1', 'NL-1', 'all-other-known-reporting-orgs']

    def __init__(self, *args, **kwargs):
        self.VERSION = codelist_models.Version.objects.get(code='2.01')
        self.test = 'blabla'

    class RequiredFieldError(Exception):
        def __init__(self, field, msg):
            """
            field: the field that is required
            msg: explanation why
            """
            self.field = field

        def __str__(self):
            return repr(self.field)

    class ValidationError(Exception):
        def __init__(self, field, msg):
            """
            field: the field that is validated
            msg: explanation what went wrong
            """
            self.field = field

        def __str__(self):
            return repr(self.field)

    def get_or_none(self, model, *args, **kwargs):
        try:
            return model.objects.get(*args, **kwargs)
        except model.DoesNotExist:
            return None

    def _get_currency_or_raise(self, currency):
        """
        get default currency if not available for currency-related fields
        """
        if not currency:
            currency = self.get_model('Activity').get('default_currency')
            if not currency: raise self.RequiredFieldError("currency", "currency: currency is not set and default-currency is not set on activity as well")

        return currency


    def get_model(self, key):
        if isinstance(key, Model):
            return super(Parse, self).get_model(key.__name__) # class name

        return super(Parse, self).get_model(key)

    def pop_model(self, key):
        if isinstance(key, Model):
            return super(Parse, self).get_model(key.__name__) # class name

        return super(Parse, self).pop_model(key)

    def register_model(self, key, model=None):
        if isinstance(key, Model):
            help(key)
            return super(Parse, self).register_model(key.__name__, key) # class name

        super(Parse, self).register_model(key, model)

    def _slugify(self,value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        
        From Django's "django/template/defaultfilters.py".
        """
        if not isinstance(value, unicode):
            value = unicode(value)
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = unicode(_slugify_strip_re.sub('', value).strip().lower())
        return _slugify_hyphenate_re.sub('-', value)

    def hash8(self,w):
        h = hashlib.md5(w.encode('ascii', 'ignore'))
        hash_generated =  h.digest().encode('base64')[:8]
        return self._slugify(hash_generated)

    def validate_date(self, unvalidated_date):
        valid_date = None
        if unvalidated_date:
            unvalidated_date = unvalidated_date.strip(' \t\n\r')
        else:
            return None
        #check if standard data parser works
        try:
            return dateutil.parser.parse(unvalidated_date)
        except:
            pass

        if unvalidated_date:
            try:
                unvalidated_date = unvalidated_date.split("Z")[0]
                unvalidated_date = sub(r'[\t]', '', unvalidated_date)
                unvalidated_date = unvalidated_date.replace(" ", "")
                unvalidated_date = unvalidated_date.replace("/", "-")
                if len(unvalidated_date) == 4:
                    unvalidated_date = unvalidated_date + "-01-01"
                try:
                    validated_date = time.strptime(unvalidated_date, '%Y-%m-%d')
                except ValueError:
                    validated_date = time.strptime(unvalidated_date, '%d-%m-%Y')
                valid_date = datetime.fromtimestamp(time.mktime(validated_date))

            except ValueError:
                # if not any(c.isalpha() for c in unvalidated_date):
                #     exception_handler(None, "validate_date", 'Invalid date: ' + unvalidated_date)
                return None
            except Exception as e:
                exception_handler(e, "validate date", "validate_date")
                return None
        return valid_date

    def _get_main_narrative_child(self, elem):
        if len(elem):
            return elem[0].text.strip()

    def _in_whitelist(self, ref):
        """
        reporting_org and participating_org @ref attributes can be whitelisted, causing name to be determined by whitelist
        """
        return False

    def _save_whitelist(self, ref):
        """
        Actually save the whitelisted organisation when first encountered
        """
        pass

    def _normalize(self, attr):
        return attr.strip(' \t\n\r').replace("/", "-").replace(":", "-").replace(" ", "")

    def get_or_create_organisation(self, elem, name, is_reporting_org=False):
        """
        Add organisation business requirements:

        Organisations coming in via reporting-org, have unique refs, and their names should always me saved with the ref
        Organisations coming in via participating-org have non unique refs and org names, if the ref exists but names
        don't match create a new Organisation with:
        Organisation.original_ref = ref, Organisation.ref = something unique,

        additional requirements:

        -2.1 Organisation.refs should never contain spaces, line breaks, slashes etc.
        -2.2 Organisation.original_ref should always be the same as the ref in the xml file
        -2.3 A reporting-org's Organisation.ref and Organisation.name should always match the ref and name in the xml file
        TO DO:
        -2.4 save all mentions to reporting-orgs under the Organisation.ref = reporting-org ref,
            also when the reporting-org is not in OIPA yet, this can only be done with a pre-defined look-up list.

        assumptions made:
        -Reporting organisations are unique

        """

        ref = elem.attrib.get('ref')
        type_ref = elem.attrib.get('type')

        # requirement 2.2
        original_ref = ref
        # requirement 2.1
        ref = self._normalize(ref)

        org_type = None
        if self.isInt(type_ref) and self.cached_db_call(models.OrganisationType,type_ref) != None:
            org_type = self.cached_db_call(models.OrganisationType,type_ref)

        # organisation = models.Organisation.objects.filter(original_ref=ref)

        # if self._in_whitelist(original_ref):
        #     if models.Organisation.objects.filter(original_ref=ref).exists():
        #         return models.Organisation.objects.filter(original_ref=ref).get()
        #     else:
        #         return self._save_whitelist_org(ref)
        # if is_reporting_org:
        #     if models.Organisation.objects.filter(original_ref=ref).exists():
        #         return models.Organisation.objects.filter(original_ref=ref).get()
        # else:
        #     if models.Organisation.objects.filter(original_ref=ref, name=name).exists():
        #         ref = ref + '-' + self.hash8(name)

        organisation = models.Organisation()
        organisation.code = ref
        organisation.original_ref = original_ref
        organisation.type = org_type
        organisation.name = name

        self.register_model('Organisation', organisation)

        return organisation

    def add_narrative(self,element,parent):

        default_lang = self.default_lang # set on activity (if set)
        lang = element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', default_lang)
        text = element.text

        language = self.get_or_none(codelist_models.Language, code=lang)

        if not language: raise self.RequiredFieldError("narrative: must specify default_lang on activities or language on the element itself")
        if not text: raise self.RequiredFieldError("narrative: must contain text")
        if not parent: raise self.RequiredFieldError("parent", "Narrative: parent object must be passed")

        narrative = models.Narrative()
        narrative.language = language
        narrative.content = element.text
        narrative.iati_identifier = self.iati_identifier # TODO: we need this?
        narrative.parent_object = parent

        self.register_model('Narrative', narrative)

    '''atributes:
    {http://www.w3.org/XML/1998/namespace}lang:en
    default-currency:USD
    last-updated-datetime:2014-09-10T07:15:37Z
    linked-data-uri:http://data.example.org/123456789
    hierarchy:1

    tag:iati-activity'''
    def iati_activities__iati_activity(self,element):
        defaults = {
            'default_lang': 'en',             
            'hierarchy': 1,             
        }

        id = self._normalize(element.xpath('iati-identifier/text()')[0])
        default_lang = element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', defaults['default_lang'])
        hierarchy = element.attrib.get('hierarchy', defaults['hierarchy'])
        last_updated_datetime = self.validate_date(element.attrib.get('last-updated-datetime'))
        linked_data_uri = element.attrib.get('linked-data-uri')
        default_currency = self.get_or_none(models.Currency, code=element.attrib.get('default-currency'))

        if not id: raise self.RequiredFieldError("id", "activity: must contain id")
        
        old_activity = self.get_or_none(models.Activity, id=id)

        if old_activity:
            if last_updated_datetime and (last_updated_datetime < old_activity.last_updated_datetime):
                raise self.ValidationError("activity", "duplicate activity: last_updated_time is less than existing activity")
            if not last_updated_datetime and old_activity.last_updated_datetime:
                raise self.ValidationError("activity", "duplicate activity: last_updated_time is not present, but is present on duplicate activity")


        activity = models.Activity()
        activity.id = id
        activity.default_lang = default_lang
        activity.hierarchy = hierarchy
        activity.xml_source_ref = self.iati_source.ref
        if last_updated_datetime:
            activity.last_updated_datetime = last_updated_datetime
        activity.linked_data_uri = linked_data_uri
        activity.default_currency = default_currency
        activity.iati_standard_version_id = self.VERSION

        # for later reference
        self.iati_identifier = activity.id
        self.default_lang = activity.default_lang

        self.register_model('Activity', activity)
        return element

    '''atributes:

    tag:iati-identifier'''
    def iati_activities__iati_activity__iati_identifier(self,element):
        iati_identifier = element.text
        
        if not iati_identifier: raise self.RequiredFieldError("text", "iati_identifeir: must contain text")

        activity = self.get_model('Activity')
        activity.iati_identifier = iati_identifier
        self.register_model('Activity', activity)
        return element

    '''atributes:
    ref:AA-AAA-123456789
    type:40
    secondary-reporter:0

    tag:reporting-org'''
    def iati_activities__iati_activity__reporting_org(self,element):
        ref = element.attrib.get('ref')

        if not ref: raise self.RequiredFieldError("ref", "reporting-org: ref must be specified")

        normalized_ref = self._normalize(ref)
        org_type = self.get_or_none(codelist_models.OrganisationType, code=element.attrib.get('type'))
        secondary_reporter = element.attrib.get('secondary-reporter', False) # TODO: should this be false by default?
        organisation = self.get_or_none(models.Organisation, code=element.attrib.get('ref'))

        activity = self.get_model('Activity')
        reporting_organisation = models.ActivityReportingOrganisation()
        reporting_organisation.ref = ref
        reporting_organisation.normalized_ref = normalized_ref
        reporting_organisation.type = org_type  
        reporting_organisation.activity = activity
        reporting_organisation.organisation = organisation
        reporting_organisation.secondary_reporter = self.makeBool(secondary_reporter)

        self.register_model('ActivityReportingOrganisation', reporting_organisation)
    
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__reporting_org__narrative(self,element):
        model = self.get_model(models.ActivityReportingOrganisation)
        self.add_narrative(element, model)

        return element

    '''atributes:https://docs.djangoproject.com/en/1.8/topics/migrations/
    ref:BB-BBB-123456789
    role:1
    type:40

    tag:participating-org'''
    def iati_activities__iati_activity__participating_org(self,element):
        ref = element.attrib.get('ref')
        role = self.get_or_none(codelist_models.OrganisationRole, code=element.attrib.get('role'))

        if not ref: raise self.RequiredFieldError("ref", "participating-org: ref must be specified")
        if not role: raise self.RequiredFieldError("role", "participating-org: role must be specified")

        normalized_ref = self._normalize(ref)
        organisation = self.get_or_none(models.Organisation, code=ref)
        org_type = self.get_or_none(codelist_models.OrganisationType, code=element.attrib.get('type'))

        activity = self.get_model('Activity')
        participating_organisation = models.ActivityParticipatingOrganisation()
        participating_organisation.ref = ref
        participating_organisation.normalized_ref = normalized_ref
        participating_organisation.type = org_type  
        participating_organisation.activity = activity
        participating_organisation.organisation = organisation
        participating_organisation.role = role

        self.register_model('ActivityParticipatingOrganisation', participating_organisation)

        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__participating_org__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
        return element

    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__title(self,element):
        activity = self.get_model('Activity')
        title = models.Title()
        title.activity = activity
        self.register_model('Title', title)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__title__narrative(self,element):
        title = self.get_model('Title')
        self.add_narrative(element, title)
        
        return element

    '''atributes:
    type:1

    tag:description'''
    def iati_activities__iati_activity__description(self,element):

        description_type_code = element.attrib.get('type', 1)
        description_type = self.get_or_none(codelist_models.Language, code=description_type_code)

        activity = self.get_model('Activity')
        description = models.Description()
        description.activity = activity
        description.type = description_type

        self.register_model('Description', description)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__description__narrative(self,element):
        title = self.get_model('Description')
        self.add_narrative(element, title)
        
        return element

    '''atributes:
    ref:ABC123-XYZ
    type:A1
    tag:other-identifier'''
    def iati_activities__iati_activity__other_identifier(self,element):
        identifier = element.attrib.get('ref')
        type = self.get_or_none(models.OtherIdentifierType, code=element.attrib.get('type'))

        if not identifier: raise self.RequiredFieldError("identifier", "other-identifier: identifier is required")
        # TODO: iati docs say type should be required (but can't for backwards compatibility)

        activity = self.get_model('Activity')
        other_identifier = models.OtherIdentifier()
        other_identifier.activity = activity
        other_identifier.identifier=identifier
        other_identifier.type=type

        self.register_model('OtherIdentifier', other_identifier)
        return element

    '''atributes:
    ref:AA-AAA-123456789

    tag:owner-org'''
    def iati_activities__iati_activity__other_identifier__owner_org(self,element):
        ref = element.attrib.get('ref')

        if not ref: raise self.RequiredFieldError("identifier", "other-identifier: identifier is required")

        other_identifier = self.get_model('OtherIdentifier')
        other_identifier.owner_ref = ref
        self.register_model('OtherIdentifier', other_identifier)

        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__other_identifier__owner_org__narrative(self,element):
        other_identifier = self.get_model('OtherIdentifier')
        self.add_narrative(element, other_identifier)
        return element

    '''atributes:
    code:2

    tag:activity-status'''
    def iati_activities__iati_activity__activity_status(self, element):

        code = element.attrib.get('code')
        activity_status = self.get_or_none(codelist_models.ActivityStatus, code=code)

        if not code: raise self.RequiredFieldError("Code")

        activity = self.get_model('Activity')
        activity.activity_status = activity_status

        return element

    '''atributes:
    iso-date:2012-04-15
    type:1

    tag:activity-date'''
    def iati_activities__iati_activity__activity_date(self, element):

        iso_date = self.validate_date(element.attrib.get('iso-date'))
        type_code = self.get_or_none(codelist_models.ActivityDateType, code=element.attrib.get('type'))

        if not iso_date: raise self.RequiredFieldError("iso-date")
        if not type_code: raise self.RequiredFieldError("Type")

        activity = self.get_model('Activity')

        activity_date = models.ActivityDate()
        activity_date.iso_date = iso_date
        activity_date.type = type_code
        activity_date.activity = activity

        self.register_model('ActivityDate', activity_date)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__activity_date__narrative(self, element):
        activity_date = self.get_model('ActivityDate')
        self.add_narrative(element, activity_date)
        return element

    '''atributes:
    type:1

    tag:contact-info'''
    def iati_activities__iati_activity__contact_info(self, element):
        type_code = self.get_or_none(codelist_models.ContactType, code=element.attrib.get('type'))

        activity = self.get_model('Activity')
        contact_info =  models.ContactInfo()
        contact_info.activity = activity
        contact_info.type = type_code
        self.register_model('ContactInfo', contact_info)

        return element

    '''atributes:

    tag:organisation'''
    def iati_activities__iati_activity__contact_info__organisation(self, element):
        contact_info = self.get_model('ContactInfo')
        contact_info_organisation =  models.ContactInfoOrganisation()
        contact_info_organisation.contact_info = contact_info;
        self.register_model('ContactInfoOrganisation', contact_info_organisation)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__organisation__narrative(self,element):
        contact_info_organisation = self.get_model('ContactInfoOrganisation')
        self.add_narrative(element, contact_info_organisation)
        return element

    '''atributes:

    tag:department'''
    def iati_activities__iati_activity__contact_info__department(self,element):
        contact_info = self.get_model('ContactInfo')
        contact_info_department =  models.ContactInfoDepartment()
        contact_info_department.contact_info = contact_info

        self.register_model('ContactInfoDepartment', contact_info_department)
         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__department__narrative(self,element):
        contact_info_department = self.get_model('ContactInfoDepartment')
        self.add_narrative(element, contact_info_department)
        return element

    '''atributes:

    tag:person-name'''
    def iati_activities__iati_activity__contact_info__person_name(self,element):
        contact_info = self.get_model('ContactInfo')
        contact_info_person_name =  models.ContactInfoPersonName()
        contact_info_person_name.contact_info = contact_info
        self.register_model('ContactInfoPersonName', contact_info_person_name)
         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__person_name__narrative(self,element):
        contact_info_person_name = self.get_model('ContactInfoPersonName')
        self.add_narrative(element, contact_info_person_name)
        return element

    '''atributes:

    tag:job-title'''
    def iati_activities__iati_activity__contact_info__job_title(self,element):
        contact_info = self.get_model('ContactInfo')
        contact_info_job_title = models.ContactInfoJobTitle()
        contact_info_job_title.contact_info = contact_info
        self.register_model('ContactInfoJobTitle', contact_info_job_title)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__job_title__narrative(self,element):
        contact_info_job_title = self.get_model('ContactInfoJobTitle')
        self.add_narrative(element, contact_info_job_title)
        return element

    '''atributes:

    tag:telephone'''
    def iati_activities__iati_activity__contact_info__telephone(self,element):
        text = element.text

        if not text: raise self.RequiredFieldError("text", "contact_info_telephone: text is required")

        contact_info = self.get_model('ContactInfo')
        contact_info.telephone = text
        self.register_model('ContactInfo', contact_info)
         
        return element

    '''atributes:

    tag:email'''
    def iati_activities__iati_activity__contact_info__email(self,element):
        text = element.text

        if not text: raise self.RequiredFieldError("text", "contact_info_email: text is required")

        contact_info = self.get_model('ContactInfo')
        contact_info.email = text
        self.register_model('ContactInfo', contact_info)
         
        return element

    '''atributes:

    tag:website'''
    def iati_activities__iati_activity__contact_info__website(self,element):
        text = element.text

        if not text: raise self.RequiredFieldError("text", "contact_info_website: text is required")

        contact_info = self.get_model('ContactInfo')
        contact_info.website = text
        self.register_model('ContactInfo', contact_info)
         
        return element

    '''atributes:

    tag:mailing-address'''
    def iati_activities__iati_activity__contact_info__mailing_address(self,element):
        contact_info = self.get_model('ContactInfo')
        contact_info_mailing_address = models.ContactInfoMailingAddress()
        contact_info_mailing_address.contact_info = contact_info
        self.register_model('ContactInfoMailingAddress', contact_info_mailing_address)
         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__mailing_address__narrative(self,element):
        contact_info_mailing_address = self.get_model('ContactInfoMailingAddress')
        self.add_narrative(element, contact_info_mailing_address)
        return element

    '''atributes:
    code:3

    tag:activity-scope'''
    def iati_activities__iati_activity__activity_scope(self,element):
        activity_scope = self.get_or_none(codelist_models.ActivityScope, code=element.attrib.get('code'))

        if not activity_scope: raise self.RequiredFieldError("code", "activity_scope: code is required")

        activity = self.get_model('Activity')
        activity.scope = activity_scope
         
        return element

    '''atributes:
    code:AF
    percentage:25

    tag:recipient-country'''
    def iati_activities__iati_activity__recipient_country(self,element):

        country = self.get_or_none(Country, code=element.attrib.get('code'))
        percentage = element.attrib.get('percentage')

        if not country: raise self.RequiredFieldError("code", "recipient-country: code is required")

        activity = self.get_model('Activity')
        activity_recipient_country =  models.ActivityRecipientCountry()
        activity_recipient_country.country = country
        activity_recipient_country.activity = activity
        activity_recipient_country.percentage = percentage
         
        self.register_model('ActivityRecipientCountry', activity_recipient_country)

        return element

    '''atributes:
    code:489
    vocabulary:1
    percentage:25

    tag:recipient-region'''
    def iati_activities__iati_activity__recipient_region(self,element):
        region = self.get_or_none(Region, code=element.attrib.get('code'))
        vocabulary = self.get_or_none(vocabulary_models.RegionVocabulary, code=element.attrib.get('vocabulary', '1')) # TODO: make defaults more transparant, here: 'OECD-DAC default'
        percentage = element.attrib.get('percentage')

        if not region: raise self.RequiredFieldError("code", "recipient-region: code is required")
        if not vocabulary: raise self.RequiredFieldError("vocabulary", "recipient-region: vocabulary is required")

        activity = self.get_model('Activity')
        activity_recipient_region =  models.ActivityRecipientRegion()
        activity_recipient_region.region = region
        activity_recipient_region.activity = activity
        activity_recipient_region.percentage = percentage
        activity_recipient_region.vocabulary = vocabulary
        self.register_model('ActivityRecipientRegion', activity_recipient_region)
         
        return element

    '''atributes:
    ref:AF-KAN

    tag:location'''
    def iati_activities__iati_activity__location(self,element):
        ref = element.attrib.get('ref')

        activity = self.get_model('Activity')
        location =  models.Location()
        location.activity = activity
        location.ref = ref
        # location.adm_code = 'no admin code'

        self.register_model('Location', location)
        return element
         

    '''atributes:
    code:1

    tag:location-reach'''
    def iati_activities__iati_activity__location__location_reach(self,element):
        location_reach = self.get_or_none(codelist_models.GeographicLocationReach, code=element.attrib.get('code'))

        if not location_reach: raise self.RequiredFieldError("code", "location_reach: code is required")

        location = self.get_model('Location')
        location.location_reach = location_reach
         
        self.register_model('Location', location)
        return element

    '''atributes:
    vocabulary:G1
    code:1453782

    tag:location-id'''
    def iati_activities__iati_activity__location__location_id(self,element):
        code = element.attrib.get('code')
        vocabulary = self.get_or_none(codelist_models.GeographicVocabulary, code=element.attrib.get('vocabulary'))

        if not code: raise self.RequiredFieldError("code", "location_id: code is required")
        if not vocabulary: raise self.RequiredFieldError("vocabulary", "location_id: vocabulary is required")

        location = self.get_model('Location')
        location.location_id_vocabulary = vocabulary
        location.location_id_code = code

        self.register_model('Location', location)
        return element

    '''atributes:

    tag:name'''
    def iati_activities__iati_activity__location__name(self,element):

        location = self.get_model('Location')
        location_name = models.LocationName()
        location_name.location = location

        self.register_model('LocationName', location_name)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__location__name__narrative(self,element):
        location_name = self.get_model('LocationName')
        self.add_narrative(element, location_name)
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__location__description(self,element):
        location = self.get_model('Location')
        location_description = models.LocationDescription()
        location_description.location = location

        self.register_model('LocationDescription', location_description)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__location__description__narrative(self,element):
        location_description = self.get_model('LocationDescription')
        self.add_narrative(element, location_description)
        return element

    '''atributes:

    tag:activity-description'''
    def iati_activities__iati_activity__location__activity_description(self,element):
        location = self.get_model('Location')
        location_activity_description = models.LocationActivityDescription()
        location_activity_description.location = location

        self.register_model('LocationActivityDescription', location_activity_description)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__location__activity_description__narrative(self,element):
        location_activity_description = self.get_model('LocationActivityDescription')
        self.add_narrative(element, location_activity_description)
        return element

    '''atributes:
    vocabulary:G1
    level:1
    code:1453782

    tag:administrative'''
    def iati_activities__iati_activity__location__administrative(self,element):
        # TODO: enforce code is according to specified vocabulary standard?
        # TODO: default level?
        code = element.attrib.get('code')
        vocabulary = self.get_or_none(codelist_models.GeographicVocabulary, code=element.attrib.get('vocabulary'))
        level = element.attrib.get('level')

        if not code: raise self.RequiredFieldError("code", "location_administrative: code is required")
        if not vocabulary: raise self.RequiredFieldError("vocabulary", "location_administrative: vocabulary is required")

        location = self.get_model('Location')
        location_administrative = models.LocationAdministrative()
        location_administrative.location = location
        location_administrative.code = code
        location_administrative.vocabulary = vocabulary
        location_administrative.level = level
         
        self.register_model('LocationAdministrative', location_administrative)

        return element

    '''atributes:
    srsName:http://www.opengis.net/def/crs/EPSG/0/4326

    tag:point'''
    def iati_activities__iati_activity__location__point(self,element):
        srs_name = element.attrib.get('srsName')

        # TODO: make this field required?
        # if not srs_name: raise self.RequiredFieldError("srsName", "location_point: srsName is required")
        if not srs_name: srs_name = "http://www.opengis.net/def/crs/EPSG/0/4326"

        location = self.get_model('Location')
        location.point_srs_name = srs_name

        self.register_model('Location', location)
        return element

    '''atributes:

    tag:pos'''
    def iati_activities__iati_activity__location__point__pos(self,element):
        # TODO: validation of lat/long
        # TODO: Allow for different srid's
        text = element.text

        if not text: raise self.RequiredFieldError("text", "location_point_pos: text is required")

        try: 
            latlong = text.strip().split(' ')
            point = GEOSGeometry(Point(float(latlong[0]), float(latlong[1])), srid=4326)
        except Exception as e:
            raise self.ValidationError("latlong", "either lat or long is not present")

        location = self.get_model('Location')
        location.point_pos = point
        
        self.register_model('Location', location)
        return element

    '''atributes:
    code:1

    tag:exactness'''
    def iati_activities__iati_activity__location__exactness(self,element):
        code = self.get_or_none(codelist_models.GeographicExactness, code=element.attrib.get('code'))

        if not code: raise self.RequiredFieldError("code", "location_exactness: code is required")

        location = self.get_model('Location')
        location.exactness = code
        self.register_model('Location', location)
         
        return element

    '''atributes:
    code:2

    tag:location-class'''
    def iati_activities__iati_activity__location__location_class(self,element):
        code = self.get_or_none(codelist_models.GeographicLocationClass, code=element.attrib.get('code'))

        if not code: raise self.RequiredFieldError("code", "location_class: code is required")

        location = self.get_model('Location')
        location.location_class = code
         
        self.register_model('Location', location)
        return element

    '''atributes:
    code:ADMF

    tag:feature-designation'''
    def iati_activities__iati_activity__location__feature_designation(self,element):
        code = self.get_or_none(codelist_models.LocationType, code=element.attrib.get('code'))

        if not code: raise self.RequiredFieldError("code", "location_feature_designation: code is required")

        location = self.get_model('Location')
        location.feature_designation = code

        self.register_model('Location', location)
        return element

    '''atributes:
    code:489
    vocabulary:1
    percentage:25

    tag:recipient-sector'''
    def iati_activities__iati_activity__sector(self,element):
        sector = self.get_or_none(models.Sector, code=element.attrib.get('code'))
        vocabulary = self.get_or_none(vocabulary_models.SectorVocabulary, code=element.attrib.get('vocabulary', '1')) # TODO: make defaults more transparant, here: 'OECD-DAC default'
        percentage = element.attrib.get('percentage')

        if not sector: raise self.RequiredFieldError("code", "sector: code is required")
        if not vocabulary: raise self.RequiredFieldError("vocabulary", "sector: vocabulary is required")

        activity = self.get_model('Activity')
        activity_sector =  models.ActivitySector()
        activity_sector.sector = sector
        activity_sector.activity = activity
        activity_sector.percentage = percentage
        activity_sector.vocabulary = vocabulary
        self.register_model('ActivitySector', activity_sector)
         
        return element

    '''atributes:
    vocabulary:2

    tag:country-budget-items'''
    def iati_activities__iati_activity__country_budget_items(self,element):
        vocabulary = self.get_or_none(vocabulary_models.BudgetIdentifierVocabulary, code=element.attrib.get('vocabulary')) 

        if not vocabulary: raise self.RequiredFieldError("vocabulary", "country-budget-items: vocabulary is required")

        activity = self.get_model('Activity')
        country_budget_item = models.CountryBudgetItem()
        country_budget_item.activity = activity
        country_budget_item.vocabulary = vocabulary

        self.register_model('CountryBudgetItem', country_budget_item)
        return element

    '''atributes:
    code:1.1.1
    percentage:50

    tag:budget-item'''
    def iati_activities__iati_activity__country_budget_items__budget_item(self,element):
        # TODO: Add custom vocabularies
        code = self.get_or_none(codelist_models.BudgetIdentifier, code=element.attrib.get('code')) 
        percentage = element.attrib.get('percentage')

        if not code: raise self.RequiredFieldError("code", "country-budget: code is required")

        country_budget_item = self.get_model('CountryBudgetItem')
        budget_item = models.BudgetItem()
        budget_item.country_budget_item = country_budget_item
        budget_item.code = code
        budget_item.percentage = percentage

        self.register_model('BudgetItem', budget_item)
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__country_budget_items__budget_item__description(self,element):
        budget_item = self.get_model('BudgetItem')
        budget_item_description = models.BudgetItemDescription()
        budget_item_description.budget_item = budget_item

        self.register_model('BudgetItemDescription', budget_item_description)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__country_budget_items__budget_item__description__narrative(self,element):
        budget_item_description = self.get_model('BudgetItemDescription')
        self.add_narrative(element, budget_item_description)
        return element

    '''atributes:
    vocabulary:1
    code:2
    significance:3

    tag:policy-marker'''
    def iati_activities__iati_activity__policy_marker(self,element):
        # TODO: custom vocabulary (other than 1)
        code = self.get_or_none(codelist_models.PolicyMarker, code=element.attrib.get('code')) 
        vocabulary = self.get_or_none(vocabulary_models.PolicyMarkerVocabulary, code=element.attrib.get('vocabulary')) 
        significance = self.get_or_none(codelist_models.PolicySignificance, code=element.attrib.get('significance')) 

        if not code: raise self.RequiredFieldError("code", "policy-marker: code is required")
        if not vocabulary: raise self.RequiredFieldError("vocabulary", "policy-marker: vocabulary is required")

        activity = self.get_model('Activity')
        activity_policy_marker = models.ActivityPolicyMarker()
        activity_policy_marker.activity = activity
        activity_policy_marker.code = code
        activity_policy_marker.vocabulary = vocabulary
        activity_policy_marker.significance = significance

        self.register_model('ActivityPolicyMarker', activity_policy_marker)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__policy_marker__narrative(self, element):
        activity_policy_marker = self.get_model('ActivityPolicyMarker')
        self.add_narrative(element, activity_policy_marker)
        return element

    '''atributes:
    code:1

    tag:collaboration-type'''
    def iati_activities__iati_activity__collaboration_type(self,element):
        code = self.get_or_none(codelist_models.CollaborationType, code=element.attrib.get('code')) 

        if not code: raise self.RequiredFieldError("code", "collaboration-type: code is required")

        activity = self.get_model('Activity')
        activity.collaboration_type = code
        self.register_model('Activity', activity)
         
        return element

    '''atributes:
    code:10

    tag:default-flow-type'''
    def iati_activities__iati_activity__default_flow_type(self,element):
        code = self.get_or_none(codelist_models.FlowType, code=element.attrib.get('code')) 

        if not code: raise self.RequiredFieldError("code", "default-flow-type: code is required")

        activity = self.get_model('Activity')
        activity.default_flow_type = code
        self.register_model('Activity', activity)
         
        return element

    '''atributes:
    code:110

    tag:default-finance-type'''
    def iati_activities__iati_activity__default_finance_type(self,element):
        code = self.get_or_none(codelist_models.FinanceType, code=element.attrib.get('code')) 

        if not code: raise self.RequiredFieldError("code", "default-flow-type: code is required")

        activity = self.get_model('Activity')
        activity.default_finance_type = code
        self.register_model('Activity', activity)
         
        return element

    '''atributes:
    code:A01

    tag:default-aid-type'''
    def iati_activities__iati_activity__default_aid_type(self,element):
        code = self.get_or_none(codelist_models.AidType, code=element.attrib.get('code')) 

        if not code: raise self.RequiredFieldError("code", "default-flow-type: code is required")

        activity = self.get_model('Activity')
        activity.default_aid_type = code
        self.register_model('Activity', activity)
         
        return element

    '''atributes:
    code:3

    tag:default-tied-status'''
    def iati_activities__iati_activity__default_tied_status(self,element):
        code = self.get_or_none(codelist_models.TiedStatus, code=element.attrib.get('code')) 

        if not code: raise self.RequiredFieldError("code", "default-tied-status: code is required")

        activity = self.get_model('Activity')
        activity.default_tied_status = code
        self.register_model('Activity', activity)
         
        return element

    '''atributes:
    type:1

    tag:budget'''
    def iati_activities__iati_activity__budget(self,element):
        budget_type = self.get_or_none(codelist_models.BudgetType, code=element.attrib.get('type')) 
        activity = self.get_model('Activity')

        # if not budget_type: raise self.RequiredFieldError("type", "budget: type is required")

        budget = models.Budget()
        budget.activity = activity
        budget.type = budget_type

        self.register_model('Budget', budget)
        return element

    '''atributes:
    iso-date:2014-01-01

    tag:period-start'''
    def iati_activities__iati_activity__budget__period_start(self,element):
        iso_date = self.validate_date(element.attrib.get('iso-date'))

        if not iso_date: raise self.RequiredFieldError("iso-date", "budget-period-start: iso-date is required")
        budget = self.get_model('Budget')
        budget.period_start = iso_date
         
        self.register_model('Budget', budget)
        return element

    '''atributes:
    iso-date:2014-12-31

    tag:period-end'''
    def iati_activities__iati_activity__budget__period_end(self,element):
        iso_date = self.validate_date(element.attrib.get('iso-date'))

        if not iso_date: raise self.RequiredFieldError("iso-date", "budget-period-end: iso-date is required")
        budget = self.get_model('Budget')
        budget.period_end = iso_date
         
        self.register_model('Budget', budget)
        return element

    '''atributes:
    currency:EUR
    value-date:2014-01-01

    tag:value'''
    def iati_activities__iati_activity__budget__value(self,element):
        # TODO: currency decimal separator determination
        currency = self.get_or_none(models.Currency, code=element.attrib.get('currency'))
        value_date = self.validate_date(element.attrib.get('value-date'))
        value = element.text

        if not value: raise self.RequiredFieldError("value", "currency: value is required")

        if not currency:
            currency = self.get_model('Activity').get('default_currency')
            if not currency: raise self.RequiredFieldError("currency", "currency: budget-value: currency is not set and default-currency is not set on activity as well")

        budget = self.get_model('Budget')
        budget.value_string = value
        budget.value = self.guess_number(value)
        budget.value_date = value_date
        budget.currency = currency
         
        self.register_model('Budget', budget)
        return element

    '''atributes:
    type:1

    tag:planned-disbursement'''
    def iati_activities__iati_activity__planned_disbursement(self,element):
        budget_type = self.get_or_none(codelist_models.BudgetType, code=element.attrib.get('type')) 

        # if not budget_type: raise self.RequiredFieldError("type", "planned-disbursement: type is required")

        activity = self.get_model('Activity')
        planned_disbursement = models.PlannedDisbursement()
        planned_disbursement.activity = activity
        planned_disbursement.budget_type  = budget_type

        self.register_model('PlannedDisbursement', planned_disbursement)
         
        return element

    '''atributes:
    iso-date:2014-01-01

    tag:period-start'''
    def iati_activities__iati_activity__planned_disbursement__period_start(self,element):
        iso_date = self.validate_date(element.attrib.get('iso-date'))

        if not iso_date: raise self.RequiredFieldError("iso-date", "planned-disbursement-period-start:  iso-date is required")

        planned_disbursement = self.get_model('PlannedDisbursement')
        planned_disbursement.period_start = iso_date

        self.register_model('PlannedDisbursement', planned_disbursement)
         
        return element
    '''atributes:
    iso-date:2014-12-31

    tag:period-end'''
    def iati_activities__iati_activity__planned_disbursement__period_end(self,element):
        iso_date = self.validate_date(element.attrib.get('iso-date'))

        if not iso_date: raise self.RequiredFieldError("iso-date", "planned-disbursement-period-end: iso-date is required")

        planned_disbursement = self.get_model('PlannedDisbursement')
        planned_disbursement.period_end = iso_date

        self.register_model('PlannedDisbursement', planned_disbursement)
         
        return element

    '''atributes:
    currency:EUR
    value-date:2014-01-01

    tag:value'''
    def iati_activities__iati_activity__planned_disbursement__value(self,element):
        value = element.text

        currency = self.get_or_none(models.Currency, code=element.attrib.get('currency'))
        value_date = self.validate_date(element.attrib.get('value-date'))
        value = element.text

        if not value: raise self.RequiredFieldError("value", "currency: value is required")

        currency = self._get_currency_or_raise(currency)

        planned_disbursement = self.get_model('PlannedDisbursement')
        planned_disbursement.value_string = value
        planned_disbursement.value = self.guess_number(value)
        planned_disbursement.value_date = value_date
        planned_disbursement.currency = currency
         
        self.register_model('PlannedDisbursement', planned_disbursement)
        return element
    '''atributes:
    percentage:88.8

    tag:capital-spend'''
    def iati_activities__iati_activity__capital_spend(self,element):
        activity = self.get_model('Activity')
        activity.capital_spend = element.attrib.get('percentage')
        self.register_model('Activity', activity)
         
        return element

    '''atributes:
    ref:1234

    tag:transaction'''
    def iati_activities__iati_activity__transaction(self,element):
        ref = element.attrib.get('ref')

        activity = self.get_model('Activity')
        transaction = transaction_models.Transaction()
        transaction.activity = activity
        transaction.ref = ref

        self.register_model('Transaction', transaction)
        return element

    '''atributes:
    code:1

    tag:transaction-type'''
    def iati_activities__iati_activity__transaction__transaction_type(self,element):
        transaction_type = self.get_or_none(transaction_models.TransactionType, code=element.attrib.get('code'))

        if not transaction_type: raise self.RequiredFieldError("code", "transaction-type: code is required")

        transaction = self.get_model('Transaction')
        transaction.transaction_type = transaction_type

        self.register_model('Transaction', transaction)
        return element

    '''atributes:
    iso-date:2012-01-01

    tag:transaction-date'''
    def iati_activities__iati_activity__transaction__transaction_date(self,element):
        iso_date = self.validate_date(element.attrib.get('iso-date'))

        if not iso_date: raise self.RequiredFieldError("iso-date", "transaction-date: iso-date is required")
        
        transaction = self.get_model('Transaction')
        transaction.transaction_date = iso_date
         
        self.register_model('Transaction', transaction)
        return element

    '''atributes:
    currency:EUR
    value-date:2012-01-01

    tag:value'''
    def iati_activities__iati_activity__transaction__value(self,element):
        currency = self.get_or_none(models.Currency, code=element.attrib.get('currency'))
        value_date = self.validate_date(element.attrib.get('value-date'))
        value = element.text

        if not value: raise self.RequiredFieldError("value", "currency: value is required")

        currency = self._get_currency_or_raise(currency)

        transaction = self.get_model('Transaction')
        transaction.value_string = value
        transaction.value = self.guess_number(value)
        transaction.value_date = value_date
        transaction.currency = currency
         
        self.register_model('Transaction', transaction)
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__transaction__description(self,element):
        transaction = self.get_model('Transaction')
        description = transaction_models.TransactionDescription()
        description.transaction = transaction
         
        self.register_model('TransactionDescription', description)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__transaction__description__narrative(self, element):
        transaction_description = self.get_model('TransactionDescription')
        self.add_narrative(element, transaction_description)
        return element

    '''atributes:
    provider-activity-id:BB-BBB-123456789-1234AA
    ref:BB-BBB-123456789

    tag:provider-org'''
    def iati_activities__iati_activity__transaction__provider_org(self, element):
        ref = element.attrib.get('ref')
        provider_activity = element.attrib.get('provider-activity-id')

        if not ref: raise self.RequiredFieldError("ref", "transaction-provider-org: ref must be specified")

        normalized_ref = self._normalize(ref)
        organisation = self.get_or_none(models.Organisation, code=ref)

        transaction_provider = transaction_models.TransactionProvider()
        transaction_provider.ref = ref
        transaction_provider.normalized_ref = normalized_ref
        transaction_provider.organisation = organisation
        transaction_provider.provider_activity_ref = provider_activity
        transaction_provider.provider_activity = self.get_or_none(models.Activity, iati_identifier=provider_activity) 

        # update existing  transaction provider-activity foreign keys
        # TODO: do this at the end of parsing in one pass
        try:
            models.TransactionProvider.objects.filter(provider_activity_ref=activity.iati_identifier).update(provider_activity=activity)
        except:
            pass

        transaction = self.pop_model('Transaction')
        transaction.provider_organisation = transaction_provider

        self.register_model('TransactionProvider', transaction_provider)
        self.register_model('Transaction', transaction)
        return element


    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__transaction__provider_org__narrative(self, element):
        transaction_provider = self.get_model('TransactionProvider')
        self.add_narrative(element, transaction_provider)
        return element

    '''atributes:
    receiver-activity-id:AA-AAA-123456789-1234
    ref:AA-AAA-123456789

    tag:receiver-org'''
    def iati_activities__iati_activity__transaction__receiver_org(self,element):
        ref = element.attrib.get('ref')
        receiver_activity = element.attrib.get('receiver-activity-id')

        if not ref: raise self.RequiredFieldError("ref", "transaction-receiver-org: ref must be specified")

        normalized_ref = self._normalize(ref)
        organisation = self.get_or_none(models.Organisation, code=ref)

        transaction_receiver = transaction_models.TransactionReceiver()
        transaction_receiver.ref = ref
        transaction_receiver.normalized_ref = normalized_ref
        transaction_receiver.organisation = organisation
        transaction_receiver.receiver_activity_ref = receiver_activity
        transaction_receiver.receiver_activity = self.get_or_none(models.Activity, iati_identifier=receiver_activity) 

        # update existing  transaction receiver-activity foreign keys
        # TODO: do this at the end of parsing in one pass
        try:
            models.TransactionReceiver.objects.filter(receiver_activity_ref=activity.iati_identifier).update(receiver_activity=activity)
        except:
            pass

        transaction = self.pop_model('Transaction')
        transaction.receiver_organisation = transaction_receiver

        self.register_model('TransactionReceiver', transaction_receiver)
        self.register_model('Transaction', transaction)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__transaction__receiver_org__narrative(self,element):
        transaction_receiver = self.get_model('TransactionReceiver')
        self.add_narrative(element, transaction_receiver)
        return element

    '''atributes:
    code:1

    tag:disbursement-channel'''
    def iati_activities__iati_activity__transaction__disbursement_channel(self,element):
        disbursement_channel = self.get_or_none(codelist_models.DisbursementChannel, code=element.attrib.get('code'))

        if not disbursement_channel: raise self.RequiredFieldError("code", "disbursement-channel: code must be specified")

        transaction = self.get_model('Transaction')
        transaction.disbursement_channel = disbursement_channel

        self.register_model('Transaction', transaction)
        return element

    '''atributes:
    vocabulary:2
    code:111

    tag:sector'''
    def iati_activities__iati_activity__transaction__sector(self,element):
        sector = self.get_or_none(models.Sector, code=element.attrib.get('code'))
        vocabulary = self.get_or_none(vocabulary_models.SectorVocabulary, code=element.attrib.get('vocabulary', '1')) # TODO: make defaults more transparant, here: 'OECD-DAC default'

        if not sector: raise self.RequiredFieldError("code", "transaction-sector: code is required")
        if not vocabulary: raise self.RequiredFieldError("vocabulary", "transaction-sector: vocabulary is required")

        transaction = self.get_model('Transaction')
        transaction_sector = transaction_models.TransactionSector()
        transaction_sector.transaction = transaction
        transaction_sector.sector = sector
        transaction_sector.vocabulary = vocabulary

        self.register_model('TransactionSector', transaction_sector)
        return element

    '''atributes:
    code:AF

    tag:recipient-country'''
    def iati_activities__iati_activity__transaction__recipient_country(self,element):
        country = self.get_or_none(Country, code=element.attrib.get('code'))

        if not country: raise self.RequiredFieldError("code", "transaction-recipient-country: code is required")

        transaction = self.get_model('Transaction')
        transaction_country = transaction_models.TransactionRecipientCountry()
        transaction_country.transaction = transaction
        transaction_country.country = country

        self.register_model('TransactionRecipientCountry', transaction_country)
        return element

    '''atributes:
    code:456
    vocabulary:1

    tag:recipient-region'''
    def iati_activities__iati_activity__transaction__recipient_region(self,element):
        region = self.get_or_none(Region, code=element.attrib.get('code'))
        vocabulary = self.get_or_none(vocabulary_models.RegionVocabulary, code=element.attrib.get('vocabulary', '1')) # TODO: make defaults more transparant, here: 'OECD-DAC default'

        if not region: raise self.RequiredFieldError("code", "recipient-region: code is required")
        if not vocabulary: raise self.RequiredFieldError("vocabulary", "recipient-region: vocabulary is required")

        transaction = self.get_model('Transaction')
        transaction_recipient_region = transaction_models.TransactionRecipientRegion()
        transaction_recipient_region.transaction = transaction
        transaction_recipient_region.region = region
        transaction_recipient_region.vocabulary = vocabulary

        transaction = self.register_model('TransactionRecipientRegion', transaction_recipient_region)
        return element

    '''atributes:
    code:10

    tag:flow-type'''
    def iati_activities__iati_activity__transaction__flow_type(self,element):
        flow_type = self.get_or_none(codelist_models.FlowType, code=element.attrib.get('code')) 

        if not flow_type:
            flow_type = self.get_model('Activity').flow_type
            if not flow_type: raise self.RequiredFieldError("code", "transaction-flow-type: code is required")

        transaction = self.get_model('Transaction')
        transaction.flow_type = flow_type
        self.register_model('Transaction', transaction)
        return element

    '''atributes:
    code:110

    tag:finance-type'''
    def iati_activities__iati_activity__transaction__finance_type(self,element):
        finance_type = self.get_or_none(codelist_models.FinanceType, code=element.attrib.get('code')) 

        if not finance_type:
            finance_type = self.get_model('Activity').finance_type
            if not finance_type: raise self.RequiredFieldError("code", "transaction-finance-type: code is required")

        transaction = self.get_model('Transaction')
        transaction.finance_type = finance_type
        self.register_model('Transaction', transaction)
        return element

    '''atributes:
    code:A01

    tag:aid-type'''
    def iati_activities__iati_activity__transaction__aid_type(self,element):
        aid_type = self.get_or_none(codelist_models.AidType, code=element.attrib.get('code')) 

        if not aid_type:
            aid_type = self.get_model('Activity').aid_type
            if not aid_type: raise self.RequiredFieldError("code", "transaction-aid-type: code is required")

        transaction = self.get_model('Transaction')
        transaction.aid_type = aid_type
        self.register_model('Transaction', transaction)
        return element

    '''atributes:
    code:3

    tag:tied-status'''
    def iati_activities__iati_activity__transaction__tied_status(self,element):
        tied_status = self.get_or_none(codelist_models.TiedStatus, code=element.attrib.get('code')) 

        if not tied_status:
            tied_status = self.get_model('Activity').tied_status
            if not tied_status: raise self.RequiredFieldError("code", "transaction-tied-status: code is required")

        transaction = self.get_model('Transaction')
        transaction.tied_status = tied_status
        transaction = self.register_model('Transaction', transaction)
        return element

    '''atributes:
    format:application/vnd.oasis.opendocument.text
    url:http:www.example.org/docs/report_en.odt

    tag:document-link'''
    def iati_activities__iati_activity__document_link(self,element):
        url = element.attrib.get('url')
        file_format = self.get_or_none(codelist_models.FileFormat, code=element.attrib.get('format')) 

        if not url: raise self.RequiredFieldError("url", "document_link: url is required")
        if not file_format: raise self.RequiredFieldError("format", "document_link: format is required")

        activity = self.get_model('Activity')
        document_link = models.DocumentLink()
        document_link.activity = activity
        document_link.url = url
        document_link.file_format = file_format

        self.register_model('DocumentLink', document_link)
        return element

    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__document_link__title(self,element):
        document_link = self.get_model('DocumentLink')
        document_link_title = models.DocumentLinkTitle()
        document_link_title.document_link = document_link

        self.register_model('DocumentLinkTitle', document_link_title)
         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__document_link__title__narrative(self,element):
        document_link_title = self.get_model('DocumentLinkTitle')
        self.add_narrative(element, document_link_title)
        return element

    '''atributes:
    code:A01

    tag:category'''
    def iati_activities__iati_activity__document_link__category(self,element):
        category = self.get_or_none(codelist_models.DocumentCategory, code=element.attrib.get('code')) 

        if not category: raise self.RequiredFieldError("code", "document-link-category: code is required")

        document_link = self.get_model('DocumentLink')
        document_link_category = models.DocumentLinkCategory()
        document_link_category.document_link = document_link
        document_link_category.category = category

        self.register_model('DocumentLinkCategory', document_link_category)
        return element

    '''atributes:
    code:en

    tag:language'''
    def iati_activities__iati_activity__document_link__language(self,element):
        language = self.get_or_none(codelist_models.Language, code=element.attrib.get('code'))

        if not language: raise self.RequiredFieldError("language", "document-link: code is required")

        document_link = self.get_model('DocumentLink')
        document_link_language = models.DocumentLinkLanguage()
        document_link_language.document_link = document_link
        document_link_language.language = language

        self.register_model('DocumentLinkLanguage', document_link_language)
        return element

    '''atributes:
    ref:AA-AAA-123456789-6789
    type:1

    tag:related-activity'''
    def iati_activities__iati_activity__related_activity(self,element):
        related_activity_type = self.get_or_none(codelist_models.RelatedActivityType, code=element.attrib.get('type')) 
        ref = element.attrib.get('ref')

        if not related_activity_type: raise self.RequiredFieldError("type", "related-activity: type is required")
        if not ref: raise self.RequiredFieldError("ref", "related-activity: ref is required")


        activity = self.get_model('Activity')
        related_activity = models.RelatedActivity()
        related_activity.current_activity = activity # TODO: remove this field?
        related_activity.related_activity = self.get_or_none(models.Activity, iati_identifier=ref) 
        related_activity.ref = ref
        related_activity.type = related_activity_type


        # update existing related activitiy foreign keys
        # TODO: do this at the end of parsing in one pass
        try:
            models.RelatedActivity.objects.filter(ref=activity.iati_identifier).update(related_activity=activity)
        except:
            pass

        self.register_model('RelatedActivity', related_activity)
        return element

    '''atributes:
    name:Project Status
    value:7
    iati-equivalent:activity-status

    tag:legacy-data'''
    def iati_activities__iati_activity__legacy_data(self,element):
        model = self.get_func_parent_model()
        legacy_data = models.LegacyData()
        legacy_data.activity = model
        legacy_data.name = element.attrib.get('name')
        legacy_data.value = element.attrib.get('value')
        legacy_data.iati_equivalent = element.attrib.get('iati-equivalent')
        legacy_data.save()
        return element

    '''atributes:
    attached:1

    tag:conditions'''
    def iati_activities__iati_activity__conditions(self,element):
        activity = self.get_model('Activity')
        activity.has_conditions = self.makeBool(element.attrib.get('attached'))
        self.register_model('Activity', activity)

        return element

    '''atributes:
    type:1

    tag:condition'''
    def iati_activities__iati_activity__conditions__condition(self,element):
        model = self.get_func_parent_model()
        condition = models.Condition()
        condition.activity = model
        condition.type = self.cached_db_call(models.ConditionType,element.attrib.get('type'))
        self.set_func_model(condition)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__conditions__condition__narrative(self,element):
        activity_date = self.get_model('ActivityDate')
        self.add_narrative(element, activity_date)
        return element

    '''atributes:
    type:1
    aggregation-status:1

    tag:result'''
    def iati_activities__iati_activity__result(self,element):
        model = self.get_func_parent_model()
        result = models.Result()
        result.result_type = self.cached_db_call(models.ResultType,element.attrib.get('type'))
        result.activity = model
        result.aggregation_status = self.makeBool(element.attrib.get('aggregation-status'))
        self.set_func_model(result)
        return element

    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__result__title(self,element):
        model = self.get_func_parent_model()
        result_title = models.ResultTitle()
        result_title.result = model
        self.set_func_model(result_title)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__result__title__narrative(self,element):
        activity_date = self.get_model('ActivityDate')
        self.add_narrative(element, activity_date)
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__result__description(self,element):
        model = self.get_func_parent_model()
        result_description = models.ResultDescription()
        result_description.result = model
        self.set_func_model(result_description)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__result__description__narrative(self,element):
        activity_date = self.get_model('ActivityDate')
        self.add_narrative(element, activity_date)
        return element

    '''atributes:
    measure:1
    ascending:1

    tag:indicator'''
    def iati_activities__iati_activity__result__indicator(self,element):
        model = self.get_func_parent_model()
        result_indicator = models.ResultIndicator()
        result_indicator.result = model
        result_indicator.baseline_year = 0
        result_indicator.baseline_value = 0
        self.set_func_model(result_indicator)
        return element

    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__result__indicator__title(self,element):
        model = self.get_func_parent_model()
        result_indicator_title = models.ResultIndicatorTitle()
        result_indicator_title.result_indicator = model
        
        self.set_func_model(result_indicator_title)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__result__indicator__title__narrative(self,element):
        activity_date = self.get_model('ActivityDate')
        self.add_narrative(element, activity_date)
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__result__indicator__description(self,element):
        model = self.get_func_parent_model()
        result_indicator_description = models.ResultIndicatorDescription()
        result_indicator_description.result_indicator = model
        self.set_func_model(result_indicator_description)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__result__indicator__description__narrative(self,element):
        activity_date = self.get_model('ActivityDate')
        self.add_narrative(element, activity_date)
        return element

    '''atributes:
    year:2012
    value:10

    tag:baseline'''
    def iati_activities__iati_activity__result__indicator__baseline(self,element):
        model = self.get_func_parent_model()
        model.baseline_year = element.attrib.get('year')
        model.baseline_value = element.attrib.get('value')

        return element

    '''atributes:

    tag:comment'''
    def iati_activities__iati_activity__result__indicator__baseline__comment(self,element):
        model = self.get_func_parent_model()
        indicator_baseline_comment = models.ResultIndicatorBaseLineComment()
        indicator_baseline_comment.result_indicator = model
        self.set_func_model(indicator_baseline_comment)
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__result__indicator__baseline__comment__narrative(self,element):
        activity_date = self.get_model('ActivityDate')
        self.add_narrative(element, activity_date)
        return element

    '''atributes:

    tag:period'''
    def iati_activities__iati_activity__result__indicator__period(self,element):
        model = self.get_func_parent_model()
        result_indicator_period = models.ResultIndicatorPeriod()
        result_indicator_period.result_indicator = model
        self.set_func_model(result_indicator_period)
        return element

    '''atributes:
    iso-date:2013-01-01

    tag:period-start'''
    def iati_activities__iati_activity__result__indicator__period__period_start(self,element):
        model = self.get_func_parent_model()
        model.period_start = element.attrib.get('iso-date')
        return element

    '''atributes:
    iso-date:2013-03-31

    tag:period-end'''
    def iati_activities__iati_activity__result__indicator__period__period_end(self,element):
        model = self.get_func_parent_model()
        model.period_end = element.attrib.get('iso-date')
        return element

    '''atributes:
    value:10

    tag:target'''
    def iati_activities__iati_activity__result__indicator__period__target(self,element):
        model = self.get_func_parent_model()
        model.target = element.attrib.get('value')

        return element

    '''atributes:

    tag:comment'''
    def iati_activities__iati_activity__result__indicator__period__target__comment(self,element):
        model = self.get_func_parent_model()
        period_target_comment = models.ResultIndicatorPeriodTargetComment()
        period_target_comment.result_indicator_period = model
        self.set_func_model(period_target_comment)
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__result__indicator__period__target__comment__narrative(self,element):
        activity_date = self.get_model('ActivityDate')
        self.add_narrative(element, activity_date)
        return element

    '''atributes:
    value:11

    tag:actual'''
    def iati_activities__iati_activity__result__indicator__period__actual(self,element):
        model = self.get_func_parent_model()
        model.actual = element.attrib.get('value')
        return element

    '''atributes:

    tag:comment'''
    def iati_activities__iati_activity__result__indicator__period__actual__comment(self,element):
        model = self.get_func_parent_model()
        period_actual_comment = models.ResultIndicatorPeriodActualComment()
        period_actual_comment.result_indicator_period = model
        self.set_func_model(period_actual_comment)
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__result__indicator__period__actual__comment__narrative(self,element):
        activity_date = self.get_model('ActivityDate')
        self.add_narrative(element, activity_date)
        return element

    '''atributes:

    tag:crs-add'''
    def iati_activities__iati_activity__crs_add(self,element):
        model = self.get_func_parent_model()
        crs_add = models.CrsAdd()
        crs_add.activity = model
        self.set_func_model(crs_add)
         
        return element

    '''atributes:
    code:1
    significance:1

    tag:other-flags'''
    def iati_activities__iati_activity__crs_add__other_flags(self,element):
        model = self.get_func_parent_model()
        crs_other_flags = models.CrsAddOtherFlags()
        crs_other_flags.crs_add = model
        crs_other_flags.other_flags =  self.cached_db_call(models.OtherFlags,element.attrib.get('code'))
        crs_other_flags.significance = element.attrib.get('significance')
        crs_other_flags.save()
        return element

    '''atributes:
    rate-1:4
    rate-2:3

    tag:loan-terms'''
    def iati_activities__iati_activity__crs_add__loan_terms(self,element):
        model = self.get_func_parent_model()
        add_loan_terms = models.CrsAddLoanTerms()
        add_loan_terms.crs_add = model
        add_loan_terms.rate_1 = element.attrib.get('rate-1')
        add_loan_terms.rate_2 = element.attrib.get('rate-2')
        self.set_func_model(add_loan_terms)
        return element

    '''atributes:
    code:1

    tag:repayment-type'''
    def iati_activities__iati_activity__crs_add__loan_terms__repayment_type(self,element):
        model = self.get_func_parent_model()
        model.repayment_type = self.cached_db_call(models.LoanRepaymentType,element.attrib.get('code'))

         
        return element

    '''atributes:
    code:4

    tag:repayment-plan'''
    def iati_activities__iati_activity__crs_add__loan_terms__repayment_plan(self,element):
        model = self.get_func_parent_model()
        model.repayment_plan = self.cached_db_call(models.LoanRepaymentPeriod,element.attrib.get('code'))

        return element

    '''atributes:
    iso-date:2013-09-01

    tag:commitment-date'''
    def iati_activities__iati_activity__crs_add__loan_terms__commitment_date(self,element):
        model = self.get_func_parent_model()
        model.commitment_date = self.validate_date(element.attrib.get('iso-date'))
        return element

    '''atributes:
    iso-date:2014-01-01

    tag:repayment-first-date'''
    def iati_activities__iati_activity__crs_add__loan_terms__repayment_first_date(self,element):
        model = self.get_func_parent_model()
        model.repayment_first_date = self.validate_date(element.attrib.get('iso-date'))

    '''atributes:
    iso-date:2020-12-31

    tag:repayment-final-date'''
    def iati_activities__iati_activity__crs_add__loan_terms__repayment_final_date(self,element):
        model = self.get_func_parent_model()
        model.repayment_final_date = self.validate_date(element.attrib.get('iso-date'))
        return element

    '''atributes:
    year:2014
    currency:GBP
    value-date:2013-05-24

    tag:loan-status'''
    def iati_activities__iati_activity__crs_add__loan_status(self,element):
        model = self.get_func_parent_model()
        crs_loan_status = models.CrsAddLoanStatus()
        crs_loan_status.crs_add = model
        crs_loan_status.year = element.attrib.get('year')
        crs_loan_status.currency = self.cached_db_call(models.Currency,element.attrib.get('currency'))
        crs_loan_status.value_date =  self.validate_date(element.attrib.get('value-date'))
        self.set_func_model(crs_loan_status)
        return element

    '''atributes:

    tag:interest-received'''
    def iati_activities__iati_activity__crs_add__loan_status__interest_received(self,element):
        model = self.get_func_parent_model()
        model.interest_received = element.text
        return element

    '''atributes:

    tag:principal-outstanding'''
    def iati_activities__iati_activity__crs_add__loan_status__principal_outstanding(self,element):
        model = self.get_func_parent_model()
        model.principal_outstanding = element.text
        return element

    '''atributes:

    tag:principal-arrears'''
    def iati_activities__iati_activity__crs_add__loan_status__principal_arrears(self,element):
        model = self.get_func_parent_model()
        model.principal_arrears = element.text
        return element

    '''atributes:

    tag:interest-arrears'''
    def iati_activities__iati_activity__crs_add__loan_status__interest_arrears(self,element):
        model = self.get_func_parent_model()
        model.interest_arrears = element.text
        return element

    '''atributes:
    extraction-date:2014-05-06
    priority:1
    phaseout-year:2016

    tag:fss'''
    def iati_activities__iati_activity__fss(self,element):
        model = self.get_func_parent_model()
        fss = models.Fss()
        fss.activity = model
        fss.year = element.attrib.get('phaseout-year')
        fss.extraction_date = self.validate_date(element.attrib.get('extraction-date'))
        self.set_func_model(fss)
        return element

    '''atributes:
    year:2014
    value-date:2013-07-03
    currency:GBP

    tag:forecast'''
    def iati_activities__iati_activity__fss__forecast(self,element):
        model = self.get_func_parent_model()
        fss_forecast = models.FssForecast()
        fss_forecast.fss = model
        fss_forecast.year = element.attrib.get('year')
        fss_forecast.value_date = self.validate_date(element.attrib.get('value-date'))
        fss_forecast.currency = self.cached_db_call(models.Currency, element.attrib.get('currency'))
        return element

