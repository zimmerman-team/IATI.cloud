# TODO: separate files per logical element (as represented in the API)
# TODO: also, separate for codelists
import iati
import iati_organisation
import datetime

from iati_codelists import models as codelist_models
from iati_vocabulary import models as vocabulary_models
from iati_codelists.factory.codelist_factory import *

import geodata
from django.contrib.gis.geos import GEOSGeometry, Point

import factory
from factory import SubFactory, RelatedFactory
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
        # django_get_or_create = ('iati_standard_version')

    id = 'IATI-0001'
    iati_identifier = 'IATI-0001'

    iati_standard_version = SubFactory(VersionFactory)
    # iati_standard_version = VersionFactory()

class ActivityDummyFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Activity
        django_get_or_create = ('id', 'iati_identifier')

    id = 'IATI-0001'
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

    def __init__(self, related_factory=NarrativeFactory, factory_related_name='related_object', 
            activity_dummy=factory.LazyAttribute(lambda obj: ActivityDummyFactory()), **defaults):

        

        super(NarrativeRelatedFactory, self).__init__(related_factory,
                factory_related_name,
                activity=activity_dummy,
                **defaults)


class TitleFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Title

    activity = SubFactory(ActivityDummyFactory)
    narrative1 = NarrativeRelatedFactory(content="title test")
    narrative2 = NarrativeRelatedFactory(content="title test2")

class DescriptionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Description

    activity = SubFactory(ActivityFactory)
    type = DescriptionTypeFactory.build()

    narrative1 = NarrativeRelatedFactory(content="title test")
    narrative2 = NarrativeRelatedFactory(content="title test2")

class ContactInfoFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ContactInfo

    activity = SubFactory(ActivityFactory)

class RelatedActivityFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.RelatedActivity

    ref_activity = SubFactory(ActivityFactory)
    current_activity = SubFactory(ActivityFactory, id="IATI-0002", iati_identifier="IATI-0002")
    ref = "IATI-0001"

    narrative1 = NarrativeRelatedFactory(content="title test")
    narrative2 = NarrativeRelatedFactory(content="title test2")

class DocumentLinkFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DocumentLink

    activity = SubFactory(ActivityFactory)
    url = 'http://someuri.com'
    file_format = SubFactory(FileFormatFactory)
    # title = 'some title'

class DocumentLinkTitleFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DocumentLinkTitle

    document_link = SubFactory(DocumentLinkFactory)
    # narratives = SubFactory(NarrativeFactory)

class DocumentLinkCategoryFactory(NoDatabaseFactory):
    # TODO: eliminate need for this element
    class Meta:
        model = iati.models.DocumentLinkCategory

    document_link = SubFactory(DocumentLinkFactory)
    category = SubFactory(DocumentCategoryFactory)


class BudgetTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.BudgetType

    code = 1
    name = 'Original'


class BudgetFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Budget

    activity = SubFactory(ActivityFactory)
    period_start = '2011-01-01'
    period_end = '2011-12-30'
    value = 100
    value_date = '2013-06-28'


class ActivityDateFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityDate

    activity = SubFactory(ActivityFactory)
    iso_date = datetime.datetime.now()
    type = SubFactory(ActivityDateTypeFactory)

class RegionFactory(NoDatabaseFactory):
    class Meta:
        model = geodata.models.Region

    code = 1
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


class ParticipatingOrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityParticipatingOrganisation

    activity = SubFactory(ActivityFactory)
    ref = "some-ref"
    normalized_ref = "some_ref"
    type = SubFactory(OrganisationTypeFactory)
    role = SubFactory(OrganisationRoleFactory)

    narrative1 = NarrativeRelatedFactory(content="title test")
    narrative2 = NarrativeRelatedFactory(content="title test2")

class OrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati_organisation.models.Organisation
        django_get_or_create = ('id',)

    id = 'GB-COH-03580586'
    organisation_identifier = 'GB-COH-03580586'
    iati_standard_version = SubFactory(VersionFactory)

class ReportingOrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityReportingOrganisation

    ref = 'GB-COH-03580586'
    normalized_ref = 'GB-COH-03580586'
    activity = SubFactory(ActivityFactory)
    type = SubFactory(OrganisationTypeFactory)
    secondary_reporter = False

    organisation = SubFactory(OrganisationFactory)

    narrative1 = NarrativeRelatedFactory(content="title test")
    narrative2 = NarrativeRelatedFactory(content="title test2")

class ActivitySectorFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivitySector

    sector = SubFactory(SectorFactory)
    activity = SubFactory(ActivityFactory)
    vocabulary = SubFactory(SectorVocabularyFactory)
    percentage = 100

    narrative1 = NarrativeRelatedFactory(content="title test")
    narrative2 = NarrativeRelatedFactory(content="title test2")

class ActivityRecipientCountryFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityRecipientCountry

    activity = SubFactory(ActivityFactory)
    country = SubFactory(CountryFactory)
    percentage = 50

    narrative1 = NarrativeRelatedFactory(content="title test")
    narrative2 = NarrativeRelatedFactory(content="title test2")

class ActivityRecipientRegionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityRecipientRegion

    percentage = 100
    region = RegionFactory.build()
    vocabulary = RegionVocabularyFactory.build()
    activity = ActivityFactory.build()

    narrative1 = NarrativeRelatedFactory(content="title test")
    narrative2 = NarrativeRelatedFactory(content="title test2")

class CountryBudgetItemFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.CountryBudgetItem

    id = 1
    activity = SubFactory(ActivityFactory)
    vocabulary = SubFactory(BudgetIdentifierVocabularyFactory)
    percentage = 50.2

class BudgetItemFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.BudgetItem

    code = SubFactory(BudgetIdentifierFactory) # Executive - executive
    country_budget_item = SubFactory(CountryBudgetItemFactory)
    percentage = 50.2

class ActivityPolicyMarkerFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityPolicyMarker

    activity = ActivityFactory.build()
    code = PolicyMarkerFactory.build()
    # alt_policy_marker = 'alt_policy_marker' # ?
    vocabulary = PolicyMarkerVocabularyFactory.build()
    significance = PolicySignificanceFactory.build()

class ResultFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Result

    activity = ActivityFactory.build()
    type = ResultTypeFactory.build()
    aggregation_status = False

class ResultIndicatorFactory(NoDatabaseFactory):
    class Meta: model = iati.models.ResultIndicator

    result = ResultFactory.build()

class ResultIndicatorTitleFactory(NoDatabaseFactory):
    class Meta: model = iati.models.ResultIndicatorTitle

    result_indicator = ResultIndicatorFactory.build()
    primary_name = 'title'

class ResultIndicatorPeriodFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicatorPeriod

    result_indicator = ResultIndicatorFactory.build()

class ResultIndicatorPeriodTargetFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicatorPeriodTargetComment

    result_period = ResultIndicatorPeriodFactory.build()

class ResultIndicatorPeriodActualFactory(NoDatabaseFactory):
    class Meta: 
        model = iati.models.ResultIndicatorPeriodActualComment

    result_period = ResultIndicatorPeriodFactory.build()

class LocationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Location

    activity = ActivityFactory.build()
    ref = 'AF-KAN'
    location_reach = SubFactory(GeographicLocationReachFactory)
    location_id_vocabulary = SubFactory(GeographicVocabularyFactory)
    location_id_code = '23213'
    point_pos = GEOSGeometry(Point(20.22, 45.22), srid=4326)
    point_srs_name = "http://www.opengis.net/def/crs/EPSG/0/4326"
    exactness = SubFactory(GeographicExactnessFactory)
    location_class = SubFactory(GeographicLocationClassFactory)
    feature_designation = SubFactory(LocationTypeFactory)

class LocationAdministrativeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.LocationAdministrative

    location = SubFactory(LocationFactory)
    code = "code"
    vocabulary = SubFactory(GeographicVocabularyFactory)
    level = 1

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
    
