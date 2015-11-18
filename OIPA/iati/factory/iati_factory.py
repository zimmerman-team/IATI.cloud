# TODO: separate files per logical element (as represented in the API)
# TODO: also, separate for codelists
import iati
import datetime
from iati_codelists import models as codelist_models
from iati_vocabulary import models as vocabulary_models
import geodata
from django.contrib.gis.geos import GEOSGeometry, Point
from factory import SubFactory
from factory.django import DjangoModelFactory

class NoDatabaseFactory(DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0

class VersionFactory(NoDatabaseFactory):
    class Meta:
        model = codelist_models.Version

    code = '2.01'
    name = 'IATI version 2.01'

class ActivityFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Activity

    id = 'IATI-0001'
    iati_identifier = 'IATI-0001'

    iati_standard_version = SubFactory(VersionFactory)

class LanguageFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Language

    code = 'fr'
    name = 'french'

class NarrativeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Narrative

    activity = SubFactory(ActivityFactory) # overwrite this for the required behaviour
    language = SubFactory(LanguageFactory)
    content = "Some name or description"

class RelatedActivityFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.RelatedActivity

    ref_activity = SubFactory(ActivityFactory)
    current_activity = SubFactory(ActivityFactory, id="IATI-0002", iati_identifier="IATI-0002")
    ref = "IATI-0001"

class FileFormatFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.FileFormat

    code = 'application/json'
    name = ''

class DocumentCategoryCategoryFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DocumentCategoryCategory

    code = 'A'
    name = 'Activity Level'

class DocumentCategoryFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DocumentCategory

    code = 'A04'
    name = 'Conditions'
    category = SubFactory(DocumentCategoryCategoryFactory)


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

    period_start = '2011-01-01'
    period_end = '2011-12-30'
    value = 100
    value_date = '2013-06-28'


class ActivityDateTypeFactory(NoDatabaseFactory):
    class Meta:
        model = codelist_models.ActivityDateType

    code = '1'
    name = 'Planned start'

class ActivityDateFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityDate

    activity = SubFactory(ActivityFactory)
    iso_date = datetime.datetime.now()
    type = SubFactory(ActivityDateTypeFactory)

class CurrencyFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Currency

    code = 'USD'
    name = 'us dolar'


class CollaborationTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.CollaborationType

    code = 1
    name = 'Bilateral'


class ActivityStatusFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityStatus

    code = 1
    name = 'Pipeline/identification'


class FlowTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.FlowType

    code = 1
    name = 'test-flowtype'
    description = 'test-flowtype-description'


class AidTypeCategoryFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.AidTypeCategory

    code = 1
    name = 'test-category'
    description = 'test-category-description'


class AidTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.AidType

    code = 1
    name = 'test'
    description = 'test'
    category = SubFactory(AidTypeCategoryFactory)


class TitleFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Title

    activity = SubFactory(ActivityFactory)
    # language = LanguageFactory.build()

class DescriptionTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DescriptionType

    code = "1"
    name = 'General'
    description = 'description here'

class DescriptionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Description

    activity = SubFactory(ActivityFactory)
    type = DescriptionTypeFactory.build()


class ContactInfoFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ContactInfo

    activity = SubFactory(ActivityFactory)

class RegionFactory(NoDatabaseFactory):
    class Meta:
        model = geodata.models.Region

    code = 1
    name = 'World'


class CountryFactory(NoDatabaseFactory):
    class Meta:
        model = geodata.models.Country

    code = 'AD'
    name = 'andorra'
    iso3 = 'and'


class CityFactory(NoDatabaseFactory):
    class Meta:
        model = geodata.models.City

    id = 1
    name = 'Colonia del Sacramento'
    geoname_id = 3443013


class SectorFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Sector

    code = 200
    name = 'advice'
    description = ''


class SectorCategoryFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.SectorCategory

    code = 200
    name = 'education'
    description = 'education description'


class OrganisationTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.OrganisationType

    code = '10'
    name = 'Government'

class OrganisationRoleFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.OrganisationRole

    code = '1'
    name = 'Funding'

class ParticipatingOrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityParticipatingOrganisation

    activity = SubFactory(ActivityFactory)
    ref = "some-ref"
    normalized_ref = "some_ref"
    type = SubFactory(OrganisationTypeFactory)
    role = SubFactory(OrganisationRoleFactory)

class ReportingOrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityReportingOrganisation

    ref = 'GB-COH-03580586'
    normalized_ref = 'GB-COH-03580586'
    activity = SubFactory(ActivityFactory)
    type = SubFactory(OrganisationTypeFactory)
    secondary_reporter = False

class OrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Organisation

    code = 'GB-COH-03580586'
    name = 'PWC'

class SectorVocabularyFactory(NoDatabaseFactory):
    class Meta:
        model = vocabulary_models.SectorVocabulary

    code = "1"
    name = "OECD DAC CRS (5 digit)"

class ActivitySectorFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivitySector

    sector = SubFactory(SectorFactory)
    activity = SubFactory(ActivityFactory)
    vocabulary = SubFactory(SectorVocabularyFactory)
    percentage = 100

class RecipientCountryFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityRecipientCountry

    id = "1.1.1"
    activity = SubFactory(ActivityFactory)
    country = SubFactory(CountryFactory)
    percentage = 50

class BudgetIdentifierVocabularyFactory(NoDatabaseFactory):
    class Meta:
        model = codelist_models.BudgetIdentifierVocabulary

    code = "1"
    name = "IATI"

class BudgetIdentifierFactory(NoDatabaseFactory):
    class Meta:
        model = codelist_models.BudgetIdentifier

    code = "1"
    name = "IATI"

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

class PolicyMarkerFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.PolicyMarker

    code = "1"
    name = 'Gender Equality'

class PolicyMarkerVocabularyFactory(NoDatabaseFactory):
    class Meta:
        model = vocabulary_models.PolicyMarkerVocabulary

    code = "1"
    name = "OECD DAC CRS"

class PolicySignificanceFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.PolicySignificance

    code = "0"
    name = 'not targeted'
    description = 'test description'

class ActivityPolicyMarkerFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityPolicyMarker

    activity = ActivityFactory.build()
    code = PolicyMarkerFactory.build()
    # alt_policy_marker = 'alt_policy_marker' # ?
    vocabulary = PolicyMarkerVocabularyFactory.build()
    significance = PolicySignificanceFactory.build()

class RegionVocabularyFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.RegionVocabulary

    code = "1"
    name = 'test vocabulary'


class ActivityRecipientRegionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityRecipientRegion

    percentage = 100
    region = RegionFactory.build()
    vocabulary = RegionVocabularyFactory.build()
    activity = ActivityFactory.build()


class ActivityScopeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityScope

    code = "1"
    name = 'example scope'


class FinanceTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.FinanceType

    code = "110"
    name = 'Aid grant excluding debt reorganisation'


class TiedStatusFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.TiedStatus

    code = "3"
    name = 'Partially tied'


class ResultTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ResultType

    code = "2"
    name = 'ResultType'

class ResultFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Result

    activity = ActivityFactory.build()
    result_type = ResultTypeFactory.build()
    aggregation_status = False

class GeographicLocationClassFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.GeographicLocationClass

    code = "2"
    name = 'Populated place'


class GeographicLocationReachFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.GeographicLocationReach

    code = "1"
    name = 'Activity'


class GeographicExactnessFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.GeographicExactness

    code = "1"
    name = 'Exact'


class LocationTypeCategoryFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.LocationTypeCategory

    code = 'S'
    name = 'Spot Features'


class LocationTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.LocationType

    code = 'AIRQ'
    name = 'abandoned airfield'
    description = 'abandoned airfield'
    category = LocationTypeCategoryFactory.build()


class GeographicVocabularyFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.GeographicVocabulary

    code = 'A1'
    name = 'Global Admininistrative Unit Layers'
    description = 'description'

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

