import iati
import geodata
from factory import SubFactory
from factory.django import DjangoModelFactory


class NoDatabaseFactory(DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0


class FileFormatFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.FileFormat

    code = 'application/json'
    name = ''


class DocumentCategoryFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DocumentCategory

    code = 'A04'
    name = 'Conditions'


class DocumentLinkFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DocumentLink

    url = 'http://someuri.com'
    title = 'some title'


class LanguageFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Language

    code = 'fr'
    name = 'french'


class DescriptionTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.DescriptionType

    code = 1
    name = 'General'
    description = 'description here'


class BudgetTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.BudgetType

    code = 1
    name = 'Original'


class BudgetFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Budget

    period_start = '2011-01-01 00:00:00'
    period_end = '2011-12-30 00:00:00'
    value = 100
    value_date = '2013-06-28'


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

    title = 'title factory'
    language = LanguageFactory.build()


class DescriptionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Description

    description = 'description factory'
    language = LanguageFactory.build()
    type = DescriptionTypeFactory.build()
    rsr_description_type_id = 1


class ActivityFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Activity

    id = 'IATI-0001'
    total_budget = 50
    iati_identifier = 'IATI-0001'


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

    code = 10
    name = 'Government'


class OrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Organisation

    code = 'GB-COH-03580586'
    name = 'PWC'


class ActivitySectorFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivitySector

    id = 1
    sector = SubFactory(SectorFactory)
    activity = SubFactory(ActivityFactory)
    percentage = 100


class OrganisationRoleFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.OrganisationRole

    code = 1
    name = 'funding'
    description = 'role description'


class ParticipatingOrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityParticipatingOrganisation

    id = 1
    activity = SubFactory(ActivityFactory)
    organisation = SubFactory(OrganisationFactory)


class RecipientCountryFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityRecipientCountry

    id = 1
    activity = SubFactory(ActivityFactory)
    country = SubFactory(CountryFactory)
    percentage = 50


class PolicyMarkerFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.PolicyMarker

    code = 1
    name = 'Gender Equality'


class VocabularyFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Vocabulary

    code = 1
    name = 'OECD DAC CRS'


class PolicySignificanceFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.PolicySignificance

    code = 0
    name = 'not targeted'
    description = 'test description'


class ActivityPolicyMarkerFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityPolicyMarker

    policy_marker = PolicyMarkerFactory.build()
    alt_policy_marker = 'alt_policy_marker'
    vocabulary = VocabularyFactory.build()
    policy_significance = PolicySignificanceFactory.build()
    activity = ActivityFactory.build()


class RegionVocabularyFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.RegionVocabulary

    code = 1
    name = 'test vocabulary'


class ActivityRecipientRegionFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityRecipientRegion

    percentage = 100
    region = RegionFactory.build()
    region_vocabulary = RegionVocabularyFactory.build()
    activity = ActivityFactory.build()


class ActivityScopeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityScope

    code = 1
    name = 'example scope'


class FinanceTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.FinanceType

    code = 110
    name = 'Aid grant excluding debt reorganisation'


class TiedStatusFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.TiedStatus

    code = 3
    name = 'Partially tied'


class ResultTypeFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ResultType

    code = 2
    name = 'ResultType'


class ResultFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Result

    activity = ActivityFactory.build()
    result_type = ResultTypeFactory.build()
    title = 'Title'
    description = 'Description'
    aggregation_status = False


class GeographicLocationClassFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.GeographicLocationClass

    code = 2
    name = 'Populated place'


class GeographicLocationReachFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.GeographicLocationReach

    code = 1
    name = 'Activity'


class GeographicExactnessFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.GeographicExactness

    code = 1
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
    category = '1'
    url = 'http://www.fao.org/geonetwork/srv/en/metadata.show?id=12691'


class LocationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Location

    activity = ActivityFactory.build()
    ref = 'AF-KAN'
    name = 'Location name'
    description = 'Location description'
    activity_description = 'A description that qualifies the activity taking place at the location'
    adm_code = '1453782'
    adm_level = 1
    adm_vocabulary = GeographicVocabularyFactory.build()
    location_id_vocabulary = GeographicVocabularyFactory.build()
    location_id_code = '23213'
    location_reach = GeographicLocationReachFactory.build()
    point_pos = '31.616944 65.716944'
    exactness = GeographicExactnessFactory.build()
    feature_designation = LocationTypeFactory.build()
