import iati
import geodata
import factory


class NoDatabaseFactory(factory.django.DjangoModelFactory):
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
    category = factory.SubFactory(AidTypeCategoryFactory)


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


class OrganisationFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.Organisation

    code = 'GB-COH-03580586'
    name = 'PWC'


class ActivitySectorFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivitySector

    id = 1
    sector = factory.SubFactory(SectorFactory)
    activity = factory.SubFactory(ActivityFactory)
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
    activity = factory.SubFactory(ActivityFactory)
    organisation = factory.SubFactory(OrganisationFactory)


class RecipientCountryFactory(NoDatabaseFactory):
    class Meta:
        model = iati.models.ActivityRecipientCountry

    id = 1
    activity = factory.SubFactory(ActivityFactory)
    country = factory.SubFactory(CountryFactory)
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
