# TODO: separate files per logical element (as represented in the API)
# TODO: also, separate for codelists
import iati
import iati_organisation
import datetime

from iati_codelists import models as codelist_models
from iati_vocabulary import models as vocabulary_models

from iati_vocabulary.factory.vocabulary_factory import *
from iati_codelists.factory.codelist_factory import *

import geodata
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point

import factory
from factory import SubFactory, RelatedFactory, LazyAttribute, SelfAttribute
from factory.django import DjangoModelFactory


class NoDatabaseFactory(DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0


class NarrativeMixin(NoDatabaseFactory):
    @classmethod
    def _generate(cls, create, attrs):
        instance = super(NarrativeMixin, cls)._generate(create, attrs)
        
        narrative = iati.models.Narrative()
        narrative.related_object = instance
        narrative.activity = iati.models.Activity.objects.all()[0] # need a dummy activity (else cyclic)
        narrative.language = LanguageFactory()

        print(attrs)

        narrative.save()


class ActivityFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Activity
        django_get_or_create = ('iati_identifier',)

    iati_identifier = 'IATI-0001'

    iati_standard_version = SubFactory(VersionFactory)
    default_lang = SubFactory(LanguageFactory)

    collaboration_type = SubFactory(CollaborationTypeFactory)
    default_flow_type = SubFactory(FlowTypeFactory)
    default_finance_type = SubFactory(FinanceTypeFactory)
    default_aid_type = SubFactory(AidTypeFactory)
    default_tied_status = SubFactory(TiedStatusFactory)
    scope = SubFactory(ActivityScopeFactory)
    activity_status = SubFactory(ActivityStatusFactory)

    publisher = SubFactory('iati_synchroniser.factory.synchroniser_factory.PublisherFactory')
    
    # iati_standard_version = VersionFactory()

    # title = RelatedFactory('iati.factory.iati_factory.TitleFactory', 'activity')

class ActivityDummyFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Activity
        django_get_or_create = ('iati_identifier')

    iati_identifier = 'IATI-0001'

    iati_standard_version = SubFactory(VersionFactory)


class NarrativeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Narrative

    related_object = SubFactory(ActivityDummyFactory) # default, change by calling with related_object

    activity = SubFactory(ActivityDummyFactory) # overwrite this for the required behaviour
    language = SubFactory(LanguageFactory)
    content = "Some name or description"


class NarrativeRelatedFactory(RelatedFactory):

    def __init__(self, related_factory=NarrativeFactory, factory_related_name='related_object', **defaults):
        print(self)
        # activity_dummy = factory.LazyAttribute(lambda obj: ActivityDummyFactory())

        super(NarrativeRelatedFactory, self).__init__(related_factory,
                factory_related_name,
                # activity=activity_dummy,
                **defaults)


class TitleFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Title

    activity = SubFactory(ActivityFactory)
    # narrative1 = NarrativeRelatedFactory(content="title test", activity=SelfAttribute('..activity'))
    # narrative2 = NarrativeRelatedFactory(content="title test2", activity=SelfAttribute('..activity'))
    # narrative1 = NarrativeRelatedFactory(content="title test")
    # narrative2 = NarrativeRelatedFactory(content="title test2")

    # narrative1 = RelatedFactory(NarrativeFactory, content="title test", activity=SelfAttribute('..activity'))

class DescriptionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Description

    activity = SubFactory(ActivityFactory)
    type = SubFactory(DescriptionTypeFactory)

    # narrative1 = NarrativeRelatedFactory(content="title description")
    # narrative2 = NarrativeRelatedFactory(content="title description2")



class ContactInfoOrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ContactInfoOrganisation

class ContactInfoDepartmentFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ContactInfoDepartment

class ContactInfoPersonNameFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ContactInfoPersonName

class ContactInfoJobTitleFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ContactInfoJobTitle

class ContactInfoMailingAddressFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ContactInfoMailingAddress

class ContactInfoFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ContactInfo

    activity = SubFactory(ActivityFactory)
    type = SubFactory(ContactTypeFactory)
    telephone = "0044111222333444"
    email = "transparency@example.org"
    website = "http://www.example.org"

    # organisation = RelatedFactory(ContactInfoOrganisationFactory, 'contact_info')
    # department = RelatedFactory(ContactInfoDepartmentFactory, 'contact_info')
    # person_name = RelatedFactory(ContactInfoPersonNameFactory, 'contact_info')
    # job_title = RelatedFactory(ContactInfoJobTitleFactory, 'contact_info')
    # mailing_address = RelatedFactory(ContactInfoMailingAddressFactory, 'contact_info')



class RelatedActivityFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.RelatedActivity

    ref_activity = SubFactory(ActivityFactory)
    current_activity = SubFactory(ActivityFactory, iati_identifier="IATI-0002")
    ref = "IATI-0001"
    type = SubFactory(RelatedActivityTypeFactory)

    # narrative1 = NarrativeRelatedFactory(content="title test")
    # narrative2 = NarrativeRelatedFactory(content="title test2")

class LegacyDataFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.LegacyData

    activity = SubFactory(ActivityFactory)
    name = "value"
    value = "value"
    iati_equivalent = "activity-id"



class DocumentLinkTitleFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DocumentLinkTitle

    # document_link = SubFactory(DocumentLinkFactory)
    # narratives = SubFactory(NarrativeFactory)


class DocumentLinkFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DocumentLink

    activity = SubFactory(ActivityFactory)
    url = 'http://someuri.com'
    file_format = SubFactory(FileFormatFactory)

    documentlinktitle = RelatedFactory(DocumentLinkTitleFactory, 'document_link')
    iso_date = datetime.datetime.now()
    # title = 'some title'

class DocumentLinkCategoryFactory(NoDatabaseFactory):
    # TODO: eliminate need for this element
    class Meta:
        model = iati.models.DocumentLinkCategory

    document_link = SubFactory(DocumentLinkFactory)
    category = SubFactory(DocumentCategoryFactory)

class DocumentLinkLanguageFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DocumentLinkLanguage

    document_link = SubFactory(DocumentLinkFactory)
    language = SubFactory(LanguageFactory)


class DocumentFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Document

    document_link = SubFactory(DocumentLinkFactory)
    long_url = 'http://someuri.com'

class DocumentSearchFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DocumentSearch

    document = SubFactory(DocumentFactory)
    last_reindexed = datetime.datetime.now()

class BudgetFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Budget

    activity = SubFactory(ActivityFactory)
    type = SubFactory(BudgetTypeFactory)
    status = SubFactory(BudgetStatusFactory)
    currency = SubFactory(CurrencyFactory)
    period_start = '2011-01-01'
    period_end = '2011-12-30'
    value = 100
    value_date = '2013-06-28'


class PlannedDisbursementFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.PlannedDisbursement

    activity = SubFactory(ActivityFactory)
    type = SubFactory(BudgetTypeFactory)
    period_start = '2014-01-01'
    period_end = '2014-12-31'
    value = 100
    currency = SubFactory(CurrencyFactory)
    value_date = '2014-01-01'


class PlannedDisbursementProviderFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.PlannedDisbursementProvider

    planned_disbursement = SubFactory(PlannedDisbursementFactory)

    provider_activity_ref = "BB-BBB-123456789-1234AA"
    type = SubFactory(OrganisationTypeFactory)
    ref = "BB-BBB-123456789"

class PlannedDisbursementReceiverFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.PlannedDisbursementReceiver

    planned_disbursement = SubFactory(PlannedDisbursementFactory)

    receiver_activity_ref = "AA-AAA-123456789-1234"
    type = SubFactory(OrganisationTypeFactory)
    ref = "AA-AAA-123456789"


class ActivityDateFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityDate

    activity = SubFactory(ActivityFactory)
    iso_date = datetime.datetime.now()
    type = SubFactory(ActivityDateTypeFactory)


class RegionFactory(NoDatabaseFactory):
    class Meta:
        model = geodata.models.Region
        django_get_or_create = ('code', )

    code = "1"
    name = 'World'


class CountryFactory(NoDatabaseFactory):
    class Meta:
        model = geodata.models.Country
        django_get_or_create = ('code', )

    code = 'AD'
    name = 'andorra'
    iso3 = 'and'


class CityFactory(NoDatabaseFactory):
    class Meta:
        model = geodata.models.City

    id = 1
    name = 'Colonia del Sacramento'
    geoname_id = 3443013

class OrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati_organisation.models.Organisation
        django_get_or_create = ('id',)

    id = 'GB-COH-03580586'
    organisation_identifier = 'GB-COH-03580586'
    iati_standard_version = SubFactory(VersionFactory)

class OrganisationReportingOrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati_organisation.models.OrganisationReportingOrganisation
        django_get_or_create = ('id',)

    id = '123123'
    org_type = SubFactory(OrganisationTypeFactory)
    secondary_reporter = False

    organisation = SubFactory(OrganisationFactory)
    # organisation = RelatedFactory(OrganisationFactory, 'reporting_org')


class OrganisationNarrativeFactory(NoDatabaseFactory):
    class Meta:
        model = iati_organisation.models.OrganisationNarrative

    related_object = SubFactory(ActivityDummyFactory) # default, change by calling with related_object

    organisation = SubFactory(OrganisationFactory) # overwrite this for the required behaviour
    language = SubFactory(LanguageFactory)
    content = "Some name or description"


class ParticipatingOrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityParticipatingOrganisation

    activity = SubFactory(ActivityFactory)
    organisation = SubFactory(OrganisationFactory)
    ref = "some-ref"
    normalized_ref = "some_ref"
    type = SubFactory(OrganisationTypeFactory)
    role = SubFactory(OrganisationRoleFactory)
    org_activity_id = "some-id"

    # narrative1 = NarrativeRelatedFactory(content="title test")
    # narrative2 = NarrativeRelatedFactory(content="title test2")

class OtherIdentifierFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.OtherIdentifier

    identifier = "some-id"
    owner_ref = "123"
    type = SubFactory(OtherIdentifierTypeFactory)
    activity = SubFactory(ActivityFactory)

    # narrative1 = NarrativeRelatedFactory(content="other_identifier test")
    # narrative2 = NarrativeRelatedFactory(content="other_identifier test2")

class ReportingOrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityReportingOrganisation

    ref = 'GB-COH-03580586'
    normalized_ref = 'GB-COH-03580586'
    activity = SubFactory(ActivityFactory)
    type = SubFactory(OrganisationTypeFactory)
    secondary_reporter = False

    organisation = SubFactory(OrganisationFactory)

    # narrative1 = NarrativeRelatedFactory(content="title test")
    # narrative2 = NarrativeRelatedFactory(content="title test2")

class ActivitySectorFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivitySector

    sector = SubFactory(SectorFactory)
    activity = SubFactory(ActivityFactory)
    vocabulary = SubFactory(SectorVocabularyFactory)
    vocabulary_uri = "https://twitter.com"
    percentage = 100

    # narrative1 = NarrativeRelatedFactory(content="title test")
    # narrative2 = NarrativeRelatedFactory(content="title test2")


class ActivityRecipientCountryFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityRecipientCountry

    activity = SubFactory(ActivityFactory)
    country = SubFactory(CountryFactory)
    percentage = 50

    # narrative1 = NarrativeRelatedFactory(content="title test")
    # narrative2 = NarrativeRelatedFactory(content="title test2")


class ActivityRecipientRegionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityRecipientRegion

    percentage = 100
    region = SubFactory(RegionFactory)
    vocabulary = SubFactory(RegionVocabularyFactory)
    vocabulary_uri = "https://twitter.com"
    activity = SubFactory(ActivityFactory)

    # narrative1 = NarrativeRelatedFactory(content="title test")
    # narrative2 = NarrativeRelatedFactory(content="title test2")


class CountryBudgetItemFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.CountryBudgetItem

    #id = 1
    activity = SubFactory(ActivityFactory)
    vocabulary = SubFactory(BudgetIdentifierVocabularyFactory)


class BudgetItemDescriptionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.BudgetItemDescription

    
    # narrative1 = NarrativeRelatedFactory(content="title test")
    # narrative2 = NarrativeRelatedFactory(content="title test2")

class BudgetItemFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.BudgetItem

    code = SubFactory(BudgetIdentifierFactory) # Executive - executive
    country_budget_item = SubFactory(CountryBudgetItemFactory)
    description = RelatedFactory(BudgetItemDescriptionFactory, 'budget_item')

    percentage = 50.2


class ActivityPolicyMarkerFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityPolicyMarker

    activity = SubFactory(ActivityFactory)
    code = SubFactory(PolicyMarkerFactory)
    # alt_policy_marker = 'alt_policy_marker' # ?
    vocabulary = SubFactory(PolicyMarkerVocabularyFactory)
    significance = SubFactory(PolicySignificanceFactory)


class ResultTitleFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ResultTitle

    # narrative1 = NarrativeRelatedFactory(content="title test")
    # narrative2 = NarrativeRelatedFactory(content="title test2")

class ResultDescriptionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ResultDescription

    # narrative1 = NarrativeRelatedFactory(content="description test")
    # narrative2 = NarrativeRelatedFactory(content="description test2")

class LocationNameFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.LocationName

    # location = SubFactory(LocationFactory)

class LocationDescriptionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.LocationDescription

    # location = SubFactory(LocationFactory)

class LocationActivityDescriptionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.LocationActivityDescription

    # location = SubFactory(LocationFactory)

class LocationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Location

    activity = SubFactory(ActivityFactory)
    ref = 'AF-KAN'
    location_reach = SubFactory(GeographicLocationReachFactory)
    location_id_vocabulary = SubFactory(GeographicVocabularyFactory)
    location_id_code = '23213'
    point_pos = GEOSGeometry(Point(20.22, 45.22), srid=4326)
    point_srs_name = "http://www.opengis.net/def/crs/EPSG/0/4326"
    exactness = SubFactory(GeographicExactnessFactory)
    location_class = SubFactory(GeographicLocationClassFactory)
    feature_designation = SubFactory(LocationTypeFactory)

    name = RelatedFactory(LocationNameFactory, 'location')
    description = RelatedFactory(LocationDescriptionFactory, 'location')
    activity_description = RelatedFactory(LocationActivityDescriptionFactory, 'location')



class LocationAdministrativeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.LocationAdministrative

    location = SubFactory(LocationFactory)
    code = "code"
    vocabulary = SubFactory(GeographicVocabularyFactory)
    level = 1

class ResultFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Result

    activity = SubFactory(ActivityFactory)
    type = SubFactory(ResultTypeFactory)
    aggregation_status = False

    resulttitle = RelatedFactory(ResultTitleFactory, 'result')
    resultdescription = RelatedFactory(ResultDescriptionFactory, 'result')


class ResultIndicatorTitleFactory(NoDatabaseFactory):
    class Meta: model = iati.models.ResultIndicatorTitle

    # result_indicator = SubFactory(ResultIndicatorFactory)

class ResultIndicatorDescriptionFactory(NoDatabaseFactory):
    class Meta: model = iati.models.ResultIndicatorDescription

    # result_indicator = SubFactory(ResultIndicatorFactory)

class ResultIndicatorBaselineCommentFactory(NoDatabaseFactory):
    class Meta: model = iati.models.ResultIndicatorBaselineComment

    # result_indicator = SubFactory(ResultIndicatorFactory)

class ResultIndicatorFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicator

    result = SubFactory(ResultFactory)
    resultindicatortitle = RelatedFactory(ResultIndicatorTitleFactory, 'result_indicator')
    resultindicatordescription = RelatedFactory(ResultIndicatorDescriptionFactory, 'result_indicator')
    resultindicatorbaselinecomment = RelatedFactory(ResultIndicatorBaselineCommentFactory, 'result_indicator')

    measure = SubFactory(IndicatorMeasureFactory)
    ascending = True
    baseline_year = 2012
    baseline_value = "10"

class ResultIndicatorReferenceFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicatorReference

    result_indicator = SubFactory(ResultIndicatorFactory)
    code = "1"
    vocabulary = SubFactory(IndicatorVocabularyFactory)
    indicator_uri = "https://twitter.com"


class ResultIndicatorPeriodTargetCommentFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicatorPeriodTargetComment

    # result_period = SubFactory(ResultIndicatorPeriodFactory)


class ResultIndicatorPeriodActualCommentFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicatorPeriodActualComment

    # result_period = SubFactory(ResultIndicatorPeriodFactory)
class ResultIndicatorPeriodFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicatorPeriod

    result_indicator = SubFactory(ResultIndicatorFactory)
    resultindicatorperiodactualcomment = RelatedFactory(ResultIndicatorPeriodActualCommentFactory, 'result_indicator_period')
    resultindicatorperiodtargetcomment = RelatedFactory(ResultIndicatorPeriodTargetCommentFactory, 'result_indicator_period')

    period_start = "2013-01-01"
    period_end = "2013-03-31"
    target = "10"
    actual = "11"



class ResultIndicatorPeriodActualLocationFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicatorPeriodActualLocation

    ref = "AF-KAN"
    location = SubFactory(LocationFactory)

    result_indicator_period = SubFactory(ResultIndicatorPeriodFactory)

class ResultIndicatorPeriodTargetLocationFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicatorPeriodTargetLocation

    ref = "AF-KAN"
    location = SubFactory(LocationFactory)

    result_indicator_period = SubFactory(ResultIndicatorPeriodFactory)

class ResultIndicatorPeriodActualDimensionFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicatorPeriodActualDimension

    name = "gender"
    value = "female"
    result_indicator_period = SubFactory(ResultIndicatorPeriodFactory)

class ResultIndicatorPeriodTargetDimensionFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicatorPeriodTargetDimension

    name = "gender"
    value = "female"
    result_indicator_period = SubFactory(ResultIndicatorPeriodFactory)

class HumanitarianScopeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.HumanitarianScope

    activity = SubFactory(ActivityFactory)
    code = "code"
    type = SubFactory(HumanitarianScopeTypeFactory)
    vocabulary = SubFactory(HumanitarianScopeVocabularyFactory)
    vocabulary_uri = "http://iatistandard.org/202/activity-standard/iati-activities/iati-activity/humanitarian-scope/"

class ActivitySearchFactory(ActivityFactory):
    """A complete search field factory for testing search"""
    
    id = 'IATI-search'
    iati_identifier = 'IATI-search'

    title = RelatedFactory(TitleFactory, 'activity')
    description = RelatedFactory(DescriptionFactory, 'activity')
    reporting_organisation = RelatedFactory(ReportingOrganisationFactory, 'activity')
    participating_organisation = RelatedFactory(ParticipatingOrganisationFactory, 'activity')
    recipient_country = RelatedFactory(ActivityRecipientCountryFactory, 'activity')
    recipient_region = RelatedFactory(ActivityRecipientRegionFactory, 'activity')
    sector = RelatedFactory(ActivitySectorFactory, 'activity')
    document_link = RelatedFactory(DocumentLinkFactory, 'activity')

class ConditionsFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.Conditions

    activity = SubFactory(ActivityFactory)
    attached = False

class ConditionFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.Condition

    conditions = SubFactory(ConditionsFactory)
    type = SubFactory(ConditionTypeFactory)

class CrsAddLoanTermsFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.CrsAddLoanTerms

    rate_1 = 20.0
    rate_2 = 30.0
    repayment_type = SubFactory(LoanRepaymentTypeFactory)
    repayment_plan = SubFactory(LoanRepaymentPeriodFactory)
    commitment_date = '2014-01-01'
    repayment_first_date = '2014-01-02'
    repayment_final_date = '2015-01-01'

class CrsAddLoanStatusFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.CrsAddLoanStatus
    
    year = 2014
    currency = SubFactory(CurrencyFactory)
    value_date = '2014-01-01'
    interest_received = 2000
    principal_outstanding = 1000
    principal_arrears = 1000
    interest_arrears = 100

class CrsAddFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.CrsAdd

    activity = SubFactory(ActivityFactory)
    channel_code = "21039"
    loan_terms = RelatedFactory(CrsAddLoanTermsFactory, 'crs_add')
    loan_status = RelatedFactory(CrsAddLoanStatusFactory, 'crs_add')

class CrsAddOtherFlagsFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.CrsAddOtherFlags

    crs_add = SubFactory(CrsAddFactory)
    other_flags = SubFactory(OtherFlagsFactory)
    significance = True


class FssFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.Fss

    activity = SubFactory(ActivityFactory)
    extraction_date = '2014-01-01'
    priority = True
    phaseout_year="2016"

class FssForecastFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.FssForecast

    fss = SubFactory(FssFactory)
    year= "2016"
    value_date = '2014-01-01'
    currency = SubFactory(CurrencyFactory)
    value = 10000
