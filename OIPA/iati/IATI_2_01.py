from genericXmlParser import XMLParser
from django.db.models import Model
from iati import models
from iati_codelists import models as codelist_models
from geodata.models import Country, Region
from iati.deleter import Deleter
from iati_synchroniser.exception_handler import exception_handler
from re import sub
import hashlib
import dateutil.parser
import time
import datetime
import re

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')

class Parse(XMLParser):
    #version of IATI standard
    default_lang = 'en'
    iati_identifier = ''
    validated_reporters = ['GB-1', 'NL-1', 'all-other-known-reporting-orgs']

    def __init__(self, *args, **kwargs):
        self.VERSION = codelist_models.Version.objects.get(code='2.01')
        self.test = 'blabla'

    def get_model(self, key):
        if isinstance(key, Model):
            return super(Parse, self).get_model(key.__name__) # class name

        return super(Parse, self).get_model(key)

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
        import unicodedata
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
        ref = ref.strip(' \t\n\r').replace("/", "-").replace(":", "-").replace(" ", "")

        org_type = None
        if self.isInt(type_ref) and self.cached_db_call(models.OrganisationType,type_ref) != None:
            org_type = self.cached_db_call(models.OrganisationType,type_ref)

        # organisation = models.Organisation.objects.filter(original_ref=ref)

        if self._in_whitelist(original_ref):

            if models.Organisation.objects.filter(original_ref=ref).exists():
                return models.Organisation.objects.filter(original_ref=ref).get()
            else:
                return self._save_whitelist_org(ref)

        if is_reporting_org:
            if models.Organisation.objects.filter(original_ref=ref).exists():
                return models.Organisation.objects.filter(original_ref=ref).get()
        else:
            if models.Organisation.objects.filter(original_ref=ref, name=name).exists():
                ref = ref + '-' + self.hash8(name)

        organisation = models.Organisation()
        organisation.code = ref
        organisation.original_ref = original_ref
        organisation.type = org_type
        organisation.name = name

        print('registering organisation')
        print(organisation.__dict__)

        self.register_model('Organisation', organisation)

        return organisation

    def add_narrative(self,element,parent):
        narrative = models.Narrative()
        lang = self.default_lang 
        if '{http://www.w3.org/XML/1998/namespace}lang' in element.attrib:
            lang = element.attrib['{http://www.w3.org/XML/1998/namespace}lang']

        if element.text is None or element.text == '':
            return
        narrative.language = self.cached_db_call(models.Language,lang)
        narrative.content = element.text
        narrative.iati_identifier = self.iati_identifier
        narrative.parent_object = parent
        narrative.save()

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

        activity = models.Activity()
        activity.default_lang = element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', defaults['default_lang'])
        activity.hierarchy = element.attrib.get('hierarchy', defaults['hierarchy'])
        activity.xml_source_ref = self.iati_source.ref
        activity.last_updated_datetime = self.validate_date(element.attrib.get('last-updated-datetime'))
        activity.linked_data_uri = element.attrib.get('linked-data-uri')
        activity.id = element.xpath('iati-identifier/text()')[0].replace(":", "-").replace(" ", "").replace("/", "-").strip(' \t\n\r')

        from lxml import etree
        print(etree.tostring(element, pretty_print=True))

        # foreign keys
        activity.iati_standard_version_id = self.VERSION

        if 'default-currency' in element.attrib:
            activity.default_currency = self.cached_db_call(models.Currency, element.attrib.get('default-currency'))
        # get_codelist(codelist_models.Currency, )
        # activity.default_currency = codelist_models.Currencyget()element.attrib.get('default-currency')

        # activity.default_currency = self.cached_db_call(models.Currency, element.attrib.get('default-currency'))
        # activity.iati_standard_version_id = self.cached_db_call(models.Version, self.VERSION, createNew = True)
        print(activity.default_currency)
        
        # for later reference
        self.iati_identifier = activity.id
        self.default_lang = activity.default_lang

        # activity.save()
        # self.set_func_model(activity)
        self.register_model('Activity', activity)


        return element

    '''atributes:

    tag:iati-identifier'''
    def iati_activities__iati_activity__iati_identifier(self,element):
        # model = self.get_func_parent_model() # activity
        activity = self.get_model('Activity')
        activity.iati_identifier = element.text
        self.register_model('Activity', activity)
        # model.save()
        return

    '''atributes:
    ref:AA-AAA-123456789
    type:40
    secondary-reporter:0

    tag:reporting-org'''
    def iati_activities__iati_activity__reporting_org(self,element):
        print(self.model_store)
        activity = self.get_model('Activity')

        reported_org_name = self._get_main_narrative_child(element)
        organisation = self.get_or_create_organisation(element, reported_org_name, is_reporting_org=True)

        print(activity)

        reporting_organisation = models.ActivityReportingOrganisation()
        reporting_organisation.activity = activity
        reporting_organisation.organisation = organisation
        reporting_organisation.secondary_reporter = self.makeBool(element.attrib.get('secondary-reporter'))

        self.register_model('ActivityReportingOrganisation', reporting_organisation)
    
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__reporting_org__narrative(self,element):
        model = self.get_model(models.ActivityReportingOrganisation)
        self.add_narrative(element, model)

        return element

    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__title(self,element):
        model = self.get_func_parent_model()
        title = models.Title()
        title.activity = model
        self.set_func_model(title)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__title__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
        
        return element

    '''atributes:
    type:1

    tag:description'''
    def iati_activities__iati_activity__description(self,element):
        model = self.get_func_parent_model()
        description = models.Description()
        description.activity = model
        desc_type = self.cached_db_call(models.DescriptionType, element.attrib.get('type'))
        description.type = desc_type
        self.set_func_model(description)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__description__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
        return element


    '''atributes:https://docs.djangoproject.com/en/1.8/topics/migrations/
    ref:BB-BBB-123456789
    role:1
    type:40

    tag:participating-org'''
    def iati_activities__iati_activity__participating_org(self,element):
        model = self.get_func_parent_model()
        org = self.get_or_create_organisation(element)
        activityParticipatingOrganisation = models.ActivityParticipatingOrganisation()
        activityParticipatingOrganisation.organisation = org
        activityParticipatingOrganisation.activity = model
        activityParticipatingOrganisation.type = self.cached_db_call(models.OrganisationType,element.attrib.get('type'))
        activityParticipatingOrganisation.role = self.cached_db_call(models.OrganisationRole, element.attrib.get('role'))
        self.set_func_model(activityParticipatingOrganisation)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__participating_org__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
        return element

    '''atributes:
    ref:ABC123-XYZ
    type:A1
    tag:other-identifier'''
    def iati_activities__iati_activity__other_identifier(self,element):
        model = self.get_func_parent_model()
        identifier = element.attrib.get('ref')
        type = self.cached_db_call(models.OtherIdentifierType, element.attrib.get('type'))

        new_other_identifier = models.OtherIdentifier(activity=model, identifier=identifier,type=type)
        self.set_func_model(new_other_identifier)
        new_other_identifier.save()
        return element

    '''atributes:
    ref:AA-AAA-123456789

    tag:owner-org'''
    def iati_activities__iati_activity__other_identifier__owner_org(self,element):
        model = self.get_func_parent_model()
        model.owner_ref = element.attrib.get('ref')
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__other_identifier__owner_org__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
        return element

    '''atributes:
    code:2

    tag:activity-status'''
    def iati_activities__iati_activity__activity_status(self, element):
        model = self.get_func_parent_model()
        model.activity_status = self.cached_db_call_no_version(models.ActivityStatus,element.attrib.get('code'))

        return element

    '''atributes:
    iso-date:2012-04-15
    type:1

    tag:activity-date'''
    def iati_activities__iati_activity__activity_date(self, element):
        model = self.get_func_parent_model()
        activity_date = models.ActivityDate()
        if 'iso-date' in element.attrib:
            activity_date.iso_date = self.validate_date(element.attrib.get('iso-date'))
        activity_date.type = self.cached_db_call(models.ActivityDateType, element.attrib.get('type'))
        if activity_date.type.codelist_successor:
            activity_date.type = self.cached_db_call(models.ActivityDateType, activity_date.type.codelist_successor)
        activity_date.activity = model
        activity_date.save()
        self.set_func_model(activity_date)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__activity_date__narrative(self, element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)

        return element

    '''atributes:
    type:1

    tag:contact-info'''
    def iati_activities__iati_activity__contact_info(self, element):
        model = self.get_func_parent_model()
        contactInfo =  models.ContactInfo()
        contactInfo.activity = model
        self.set_func_model(contactInfo)

         

        return element

    '''atributes:

    tag:organisation'''
    def iati_activities__iati_activity__contact_info__organisation(self, element):
        model = self.get_func_parent_model()
        contactInfoOrganisation =  models.ContactInfoOrganisation()
        contactInfoOrganisation.ContactInfo = model;
        self.set_func_model(contactInfoOrganisation)
         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__organisation__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
         
        return element

    '''atributes:

    tag:department'''
    def iati_activities__iati_activity__contact_info__department(self,element):
        model = self.get_func_parent_model()
        contactInfoDepartment =  models.ContactInfoDepartment()
        contactInfoDepartment.ContactInfo = model

        self.set_func_model(contactInfoDepartment)

         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__department__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
         
        return element

    '''atributes:

    tag:person-name'''
    def iati_activities__iati_activity__contact_info__person_name(self,element):
        model = self.get_func_parent_model()
        contactInfoPersonName =  models.ContactInfoPersonName()
        contactInfoPersonName.ContactInfo = model
        self.set_func_model(contactInfoPersonName)
         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__person_name__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
         
        return element

    '''atributes:

    tag:job-title'''
    def iati_activities__iati_activity__contact_info__job_title(self,element):
        model = self.get_func_parent_model()
        contactInfoJobTitle =  models.ContactInfoJobTitle()
        contactInfoJobTitle.ContactInfo = model
        self.set_func_model(contactInfoJobTitle)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__job_title__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)

         
        return element

    '''atributes:

    tag:telephone'''
    def iati_activities__iati_activity__contact_info__telephone(self,element):
        model = self.get_func_parent_model()
        model.telephone = element.text
         
        return element

    '''atributes:

    tag:email'''
    def iati_activities__iati_activity__contact_info__email(self,element):
        model = self.get_func_parent_model()
        model.email = element.text
         

        return element

    '''atributes:

    tag:website'''
    def iati_activities__iati_activity__contact_info__website(self,element):
        model = self.get_func_parent_model()
        model.website = element.text
         
        return element

    '''atributes:

    tag:mailing-address'''
    def iati_activities__iati_activity__contact_info__mailing_address(self,element):
        model = self.get_func_parent_model()
        contactInfoMailingAddress = models.ContactInfoMailingAddress()
        contactInfoMailingAddress.ContactInfo = model
        self.set_func_model(contactInfoMailingAddress)
         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__mailing_address__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
         
        return element

    '''atributes:
    code:3

    tag:activity-scope'''
    def iati_activities__iati_activity__activity_scope(self,element):
        model = self.get_func_parent_model()
        model.scope = self.cached_db_call(models.ActivityScope,element.attrib.get('code'))
         
        return element

    '''atributes:
    code:AF
    percentage:25

    tag:recipient-country'''
    def iati_activities__iati_activity__recipient_country(self,element):
        model = self.get_func_parent_model()
        activity_recipient_country =  models.ActivityRecipientCountry()
        country = self.cached_db_call_no_version(Country,element.attrib.get('code'))
        activity_recipient_country.country = country
        activity_recipient_country.activity = model
        activity_recipient_country.percentage = element.attrib.get('percentage')
        activity_recipient_country.save()
         
        return element

    '''atributes:
    code:489
    vocabulary:1
    percentage:25

    tag:recipient-region'''
    def iati_activities__iati_activity__recipient_region(self,element):
        model = self.get_func_parent_model()
        activity_recipient_region =  models.ActivityRecipientRegion()
        region = self.cached_db_call(Region,element.attrib.get('code'))
        activity_recipient_region.region = region
        activity_recipient_region.activity = model
        activity_recipient_region.percentage = element.attrib.get('percentage')
        activity_recipient_region.vocabulary = self.cached_db_call(models.RegionVocabulary,element.attrib.get('vocabulary'))
        activity_recipient_region.save()
         
        return element

    '''atributes:
    ref:AF-KAN

    tag:location'''
    def iati_activities__iati_activity__location(self,element):
        model = self.get_func_parent_model()
        location =  models.Location()
        location.activity = model
        if 'ref' in element.attrib:
            location.ref = element.attrib.get('ref')
        else:
            location.ref = 'no ref'

        location.adm_code = 'no admin code'
        self.set_func_model(location)
         
        return element

    '''atributes:
    code:1

    tag:location-reach'''
    def iati_activities__iati_activity__location__location_reach(self,element):
        model = self.get_func_parent_model()
        model.location_reach = self.cached_db_call(models.GeographicLocationReach,element.attrib.get('code'))
         
        return element

    '''atributes:
    vocabulary:G1
    code:1453782

    tag:location-id'''
    def iati_activities__iati_activity__location__location_id(self,element):
        model = self.get_func_parent_model()
        model.location_id_vocabulary = self.cached_db_call(models.GeographicVocabulary,element.attrib.get('vocabulary'))
        model.location_id_code = element.attrib.get('code')
         
        return element

    '''atributes:

    tag:name'''
    def iati_activities__iati_activity__location__name(self,element):
        model = self.get_func_parent_model()
        location_name = models.LocationName()
        location_name.location = model
        self.set_func_model(location_name)

         

        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__location__name__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
         
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__location__description(self,element):
        model = self.get_func_parent_model()
        location_description = models.LocationDescription()
        location_description.location  = model
        self.set_func_model(location_description)

         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__location__description__narrative(self,element):
        model = self.get_func_parent_model()
         
        self.add_narrative(element,model)
        return element

    '''atributes:

    tag:activity-description'''
    def iati_activities__iati_activity__location__activity_description(self,element):
        model = self.get_func_parent_model()
        location_activity_description = models.LocationActivityDescription()
        location_activity_description.location  = model
        self.set_func_model(location_activity_description)


         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__location__activity_description__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
         
        return element

    '''atributes:
    vocabulary:G1
    level:1
    code:1453782

    tag:administrative'''
    def iati_activities__iati_activity__location__administrative(self,element):
        model = self.get_func_parent_model()
        model.adm_code = element.attrib.get('code')
        model.adm_vocabulary = self.cached_db_call_no_version(models.GeographicVocabulary,element.attrib.get('vocabulary'))
         
        return element

    '''atributes:
    srsName:http://www.opengis.net/def/crs/EPSG/0/4326

    tag:point'''
    def iati_activities__iati_activity__location__point(self,element):
        model = self.get_func_parent_model()
        model.point_srs_name = element.attrib.get('srsName')

         
        return element

    '''atributes:

    tag:pos'''
    def iati_activities__iati_activity__location__point__pos(self,element):
        model = self.get_func_parent_model()
        model.point_pos = element.text
        
         
        return element

    '''atributes:
    code:1

    tag:exactness'''
    def iati_activities__iati_activity__location__exactness(self,element):
        model = self.get_func_parent_model()
        model.exactness = self.cached_db_call(models.GeographicExactness,element.attrib.get('code'))
         
        return element

    '''atributes:
    code:2

    tag:location-class'''
    def iati_activities__iati_activity__location__location_class(self,element):
        model = self.get_func_parent_model()
        model.location_class = self.cached_db_call(models.GeographicLocationClass,element.attrib.get('code'))
         
        return element

    '''atributes:
    code:ADMF

    tag:feature-designation'''
    def iati_activities__iati_activity__location__feature_designation(self,element):
        model = self.get_func_parent_model()
        model.feature_designation = self.cached_db_call(models.LocationType,element.attrib.get('code'))
         
        return element
        model.save()

    '''atributes:
    vocabulary:2
    code:111
    percentage:50

    tag:sector'''
    def iati_activities__iati_activity__sector(self,element):
        model = self.get_func_parent_model()
        activity_sector = models.ActivitySector()
        activity_sector.activity = model
        activity_sector.sector = self.cached_db_call(models.Sector,element.attrib.get('code'))
        activity_sector.vocabulary = self.cached_db_call(models.SectorVocabulary,element.attrib.get('vocabulary'))
        activity_sector.percentage =  element.attrib.get('percentage')
        activity_sector.save()
         
        return element

    '''atributes:
    vocabulary:2

    tag:country-budget-items'''
    def iati_activities__iati_activity__country_budget_items(self,element):
        model = self.get_func_parent_model()
        country_budget_item = models.CountryBudgetItem()
        country_budget_item.activity = model
        country_budget_item.vocabulary = self.cached_db_call(models.BudgetIdentifierVocabulary,element.attrib.get('vocabulary'))
        self.set_func_model(country_budget_item)

        
        return element

    '''atributes:
    code:1.1.1
    percentage:50

    tag:budget-item'''
    def iati_activities__iati_activity__country_budget_items__budget_item(self,element):
        model = self.get_func_parent_model()
        budget_item = models.BudgetItem()
        budget_item.country_budget_item = model
        budget_item.code = element.attrib.get('code')
        budget_item.percentage = element.attrib.get('percentage')
        self.set_func_model(budget_item)
         
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__country_budget_items__budget_item__description(self,element):
        model = self.get_func_parent_model()
        budget_item_description = models.BudgetItemDescription()
        budget_item_description.budget_item = model
        self.set_func_model(budget_item_description)
         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__country_budget_items__budget_item__description__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
         
        return element

    '''atributes:
    vocabulary:1
    code:2
    significance:3

    tag:policy-marker'''
    def iati_activities__iati_activity__policy_marker(self,element):
        model = self.get_func_parent_model()
         
        activity_policy_marker = models.ActivityPolicyMarker()
        activity_policy_marker.activity = model
        activity_policy_marker.policy_marker = self.cached_db_call(models.PolicyMarker,element.attrib.get('code'))
        activity_policy_marker.vocabulary = self.cached_db_call(models.Vocabulary,element.attrib.get('vocabulary'))
        activity_policy_marker.policy_significance = self.cached_db_call(models.PolicySignificance,element.attrib.get('significance'))
        activity_policy_marker.code = element.attrib.get('code')
        activity_policy_marker.save()
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__policy_marker__narrative(self, element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
         
        return element

    '''atributes:
    code:1

    tag:collaboration-type'''
    def iati_activities__iati_activity__collaboration_type(self,element):
        model = self.get_func_parent_model()
        model.collaboration_type = self.cached_db_call_no_version(models.CollaborationType,element.attrib.get('code'))
         
        return element

    '''atributes:
    code:10

    tag:default-flow-type'''
    def iati_activities__iati_activity__default_flow_type(self,element):
        model = self.get_func_parent_model()
        model.default_flow_type = self.cached_db_call_no_version(models.FlowType,element.attrib.get('code'))
         
        return element

    '''atributes:
    code:110

    tag:default-finance-type'''
    def iati_activities__iati_activity__default_finance_type(self,element):
        model = self.get_func_parent_model()
        model.default_finance_type  = self.cached_db_call_no_version(models.FinanceType,element.attrib.get('code'))
         
        return element

    '''atributes:
    code:A01

    tag:default-aid-type'''
    def iati_activities__iati_activity__default_aid_type(self,element):
        model = self.get_func_parent_model()
        model.default_aid_type  = self.cached_db_call_no_version(models.AidType,element.attrib.get('code'))
         
        return element

    '''atributes:
    code:3

    tag:default-tied-status'''
    def iati_activities__iati_activity__default_tied_status(self,element):
        model = self.get_func_parent_model()
        model.default_tied_status = self.cached_db_call_no_version(models.TiedStatus,element.attrib.get('code'))
         
        return element

    '''atributes:
    type:1

    tag:budget'''
    def iati_activities__iati_activity__budget(self,element):
        model = self.get_func_parent_model()
        budget = models.Budget()
        budget.activity = model
        budget.type = self.cached_db_call(models.BudgetType,element.attrib.get('type'))
        budget.value = 0
        self.set_func_model(budget)
         
        return element

    '''atributes:
    iso-date:2014-01-01

    tag:period-start'''
    def iati_activities__iati_activity__budget__period_start(self,element):
        model = self.get_func_parent_model()
        model.period_start = element.attrib.get('iso-date')
         
        return element

    '''atributes:
    iso-date:2014-12-31

    tag:period-end'''
    def iati_activities__iati_activity__budget__period_end(self,element):
        model = self.get_func_parent_model()
        model.period_end = element.attrib.get('iso-date')
         
        return element

    '''atributes:
    currency:EUR
    value-date:2014-01-01

    tag:value'''
    def iati_activities__iati_activity__budget__value(self,element):
        model = self.get_func_parent_model()
        value = element.text
        value = self.guess_number(value)
        model.value = value
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        model.currency  = self.cached_db_call(models.Currency,element.attrib.get('currency'))
         
        return element

    '''atributes:
    type:1

    tag:planned-disbursement'''
    def iati_activities__iati_activity__planned_disbursement(self,element):
        model = self.get_func_parent_model()
        planned_disbursement = models.PlannedDisbursement()
        planned_disbursement.activity = model
        planned_disbursement.value = 0
        planned_disbursement.budget_type  = self.cached_db_call(models.BudgetType,element.attrib.get('type'))
        self.set_func_model(planned_disbursement)
         
        return element

    '''atributes:
    iso-date:2014-01-01

    tag:period-start'''
    def iati_activities__iati_activity__planned_disbursement__period_start(self,element):
        model = self.get_func_parent_model()
        model.period_start = element.attrib.get('iso-date')
         
        return element

    '''atributes:
    iso-date:2014-12-31

    tag:period-end'''
    def iati_activities__iati_activity__planned_disbursement__period_end(self,element):
        model = self.get_func_parent_model()
        model.period_end = element.attrib.get('iso-date')
         
        return element

    '''atributes:
    currency:EUR
    value-date:2014-01-01

    tag:value'''
    def iati_activities__iati_activity__planned_disbursement__value(self,element):
        model = self.get_func_parent_model()
        value = element.text
        value = self.guess_number(value)
        model.value = value
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        model.currency  = self.cached_db_call(models.Currency,element.attrib.get('currency'))
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
        # TODO: transaction models changed, parse accordingly
        model = self.get_func_parent_model()
        transaction = models.Transaction()
        transaction.activity = model
        transaction.ref = element.attrib.get('ref')
        transaction.value = 0
        self.set_func_model(transaction)
         
        return element

    '''atributes:
    code:1

    tag:transaction-type'''
    def iati_activities__iati_activity__transaction__transaction_type(self,element):
        model = self.get_func_parent_model()
        model.transaction_type= self.cached_db_call(models.TransactionType,element.attrib.get('code'))
         
        return element

    '''atributes:
    iso-date:2012-01-01

    tag:transaction-date'''
    def iati_activities__iati_activity__transaction__transaction_date(self,element):
        model = self.get_func_parent_model()
        model.transaction_date = self.validate_date(element.attrib.get('iso-date'))
         
        return element

    '''atributes:
    currency:EUR
    value-date:2012-01-01

    tag:value'''
    def iati_activities__iati_activity__transaction__value(self,element):
        model = self.get_func_parent_model()
        value = self.guess_number(element.text)
        model.value = value
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        model.currency  = self.cached_db_call(models.Currency,element.attrib.get('currency'))
         
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__transaction__description(self,element):
        model = self.get_func_parent_model()
        description = models.TransactionDescription()
        description.transaction = model
        self.set_func_model(description)
         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__transaction__description__narrative(self, element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
         
        return element

    '''atributes:
    provider-activity-id:BB-BBB-123456789-1234AA
    ref:BB-BBB-123456789

    tag:provider-org'''
    def iati_activities__iati_activity__transaction__provider_org(self, element):
        model = self.get_func_parent_model()
        model.provider_activity = element.attrib.get('provider-activity-id')

        provider_org = self.get_or_create_organisation(element)
        transaction_provider = models.TransactionProvider()
        transaction_provider.transaction = model
        transaction_provider.organisation = provider_org
        self.set_func_model(transaction_provider)
        model.provider_organisation = transaction_provider
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__transaction__provider_org__narrative(self, element):
        model = self.get_func_parent_model()
        self.add_narrative(element, model)

        return element

    '''atributes:
    receiver-activity-id:AA-AAA-123456789-1234
    ref:AA-AAA-123456789

    tag:receiver-org'''
    def iati_activities__iati_activity__transaction__receiver_org(self,element):
        model = self.get_func_parent_model()
        model.receiver_activity = element.attrib.get('receiver-activity-id')

        receiver_org = self.get_or_create_organisation(element)
        model.receiver_organisation = receiver_org
        transaction_receiver = models.TransactionReceiver()
        transaction_receiver.transaction = model
        transaction_receiver.organisation = receiver_org
        self.set_func_model(transaction_receiver)
        model.receiver_organisation = transaction_receiver
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__transaction__receiver_org__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
        return element

    '''atributes:
    code:1

    tag:disbursement-channel'''
    def iati_activities__iati_activity__transaction__disbursement_channel(self,element):
        model = self.get_func_parent_model()
        model.disbursement_channel = self.cached_db_call(models.DisbursementChannel,element.attrib.get('code'))
        return element

    '''atributes:
    vocabulary:2
    code:111

    tag:sector'''
    def iati_activities__iati_activity__transaction__sector(self,element):
        model = self.get_func_parent_model()
        # TO DO; fix this, a sector has a vocabulary, so filter by code + filter
        model.sector = self.cached_db_call(models.Sector,element.attrib.get('code'))
        # sector.vocabulary = self.cached_db_call(models.SectorVocabulary,element.attrib.get('vocabulary'))
        self.set_func_model(model)
        return element

    '''atributes:
    code:AF

    tag:recipient-country'''
    def iati_activities__iati_activity__transaction__recipient_country(self,element):
        model = self.get_func_parent_model()
        model.recipient_country = self.cached_db_call_no_version(Country, element.attrib.get('code'))
        return element

    '''atributes:
    code:456
    vocabulary:1

    tag:recipient-region'''
    def iati_activities__iati_activity__transaction__recipient_region(self,element):
        model = self.get_func_parent_model()

        # TO DO; fix this, a recipient_region has a vocabulary, so filter by code + filter
        model.recipient_region = self.cached_db_call(models.Region, element.attrib.get('code'))
        # model.recipient_region_vocabulary = self.cached_db_call(models.RegionVocabulary,element.attrib.get('vocabulary'))
        return element

    '''atributes:
    code:10

    tag:flow-type'''
    def iati_activities__iati_activity__transaction__flow_type(self,element):
        model = self.get_func_parent_model()
        model.flow_type = self.cached_db_call(models.FlowType,element.attrib.get('code'))
        return element

    '''atributes:
    code:110

    tag:finance-type'''
    def iati_activities__iati_activity__transaction__finance_type(self,element):
        model = self.get_func_parent_model()
        model.finance_type = self.cached_db_call(models.FinanceType,element.attrib.get('code'))
        return element

    '''atributes:
    code:A01

    tag:aid-type'''
    def iati_activities__iati_activity__transaction__aid_type(self,element):
        model = self.get_func_parent_model()
        model.aid_type =  self.cached_db_call(models.AidType,element.attrib.get('code'))
        return element

    '''atributes:
    code:3

    tag:tied-status'''
    def iati_activities__iati_activity__transaction__tied_status(self,element):
        model = self.get_func_parent_model()
        model.tied_status = self.cached_db_call(models.TiedStatus,element.attrib.get('code'))
        return element

    '''atributes:
    format:application/vnd.oasis.opendocument.text
    url:http:www.example.org/docs/report_en.odt

    tag:document-link'''
    def iati_activities__iati_activity__document_link(self,element):
        model = self.get_func_parent_model()
        document_link = models.DocumentLink()
        document_link.activity = model
        document_link.url = element.attrib.get('url')
        document_link.file_format = self.cached_db_call(models.FileFormat,element.attrib.get('format'),createNew=True)
        self.set_func_model(document_link)
        return element

    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__document_link__title(self,element):
        model = self.get_func_parent_model()
        document_link_title = models.DocumentLinkTitle()
        document_link_title.document_link = model
        self.set_func_model(document_link_title)
         
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__document_link__title__narrative(self,element):
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
        return element

    '''atributes:
    code:A01

    tag:category'''
    def iati_activities__iati_activity__document_link__category(self,element):

        model = self.get_func_parent_model()
        document_category = self.cached_db_call(models.DocumentCategory, element.attrib.get('code'))
        model.categories.add(document_category)
        return element


    '''atributes:
    code:en

    tag:language'''
    def iati_activities__iati_activity__document_link__language(self,element):
        model = self.get_func_parent_model()
        model.language = self.cached_db_call(models.Language,element.attrib.get('code'))
        return element

    '''atributes:
    ref:AA-AAA-123456789-6789
    type:1

    tag:related-activity'''
    def iati_activities__iati_activity__related_activity(self,element):
        model = self.get_func_parent_model()
        related_activity = models.RelatedActivity()
        related_activity.current_activity = model
        related_activity.type = self.cached_db_call(models.RelatedActivityType, element.attrib.get('type'))
        related_activity.ref = element.attrib.get('ref')
        ref = element.attrib.get('ref')
        try:
            related_activity_temp = models.Activity.objects.get(iati_identifier=ref)
        except :
            related_activity_temp = None

        # update existing related activitiy foreign keys
        try:
            ref_activities = models.RelatedActivity.objects.filter(ref=model.iati_identifier).update(related_activity=model)
        except:
            pass
        related_activity.related_activity = related_activity_temp
        related_activity.save()
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
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
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
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
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
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
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
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
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
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
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
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
        #store element 
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
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
        #store element 
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
        model = self.get_func_parent_model()
        self.add_narrative(element,model)
        #store element 
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

