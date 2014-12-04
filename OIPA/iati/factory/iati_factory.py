import iati
import geodata
import factory


class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Budget
    type_id = 1
    period_start = '2011-01-01 00:00:00'
    period_end = '2011-12-30 00:00:00'
    value = 100
    value_date = '2013-06-28'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class CurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Currency
    code = 'USD'
    name = 'us dolar'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class CollaborationTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.CollaborationType
    code = 1
    name = 'Bilateral'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class ActivityStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.ActivityStatus
    code = 1
    name = 'Pipeline/identification'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class FlowTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.FlowType
    code = 1
    name = 'test-flowtype'
    description = 'test-flowtype-description'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class AidTypeCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.AidTypeCategory
    code = 1
    name = 'test-category'
    description = 'test-category-description'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class AidTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.AidType

    code = 1
    name = 'test'
    description = 'test'
    category = factory.SubFactory(AidTypeCategoryFactory)

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class TitleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Title

    title = 'title factory'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class DescriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Description

    description = 'description factory'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Activity

    id = 'IATI-0001'
    total_budget = 50
    iati_identifier = 'IATI-0001'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = geodata.models.Region
        django_get_or_create = ('code',)

    code = 1
    name = 'World'


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = geodata.models.Country
        django_get_or_create = ('code',)

    code = 'AD'
    name = 'andorra'
    iso3 = 'and'


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = geodata.models.City
        django_get_or_create = ('id',)

    id = 1
    name = 'Colonia del Sacramento'
    geoname_id = 3443013


class SectorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Sector
        django_get_or_create = ('code',)

    code = 200
    name = 'advice'
    description = ''


class OrganisationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Organisation
        django_get_or_create = ('code',)

    code = 'GB-COH-03580586'
    name = 'PWC'


class ActivitySectorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.ActivitySector
        django_get_or_create = ('id',)

    id = 1
    sector = factory.SubFactory(SectorFactory)
    activity = factory.SubFactory(ActivityFactory)
    percentage = 100


class ParticipatingOrganisationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.ActivityParticipatingOrganisation
        django_get_or_create = ('id',)

    id = 1
    activity = factory.SubFactory(ActivityFactory)
    organisation = factory.SubFactory(OrganisationFactory)


class RecipientCountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.ActivityRecipientCountry
        django_get_or_create = ('id',)

    id = 1
    activity = factory.SubFactory(ActivityFactory)
    country = factory.SubFactory(CountryFactory)
    percentage = 50


class PolicyMarkerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.PolicyMarker
    code = 1
    name = 'Gender Equality'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class VocabularyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Vocabulary
    code = 1
    name = 'OECD DAC CRS'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class PolicySignificanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.PolicySignificance
    code = 0
    name = 'not targeted'
    description = 'test description'

    @classmethod
    def _setup_next_sequence(cls):
        return 0


class ActivityPolicyMarkerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.ActivityPolicyMarker

    @classmethod
    def _setup_next_sequence(cls):
        return 0

    policy_marker = PolicyMarkerFactory.build()
    alt_policy_marker = 'alt_policy_marker'
    vocabulary = VocabularyFactory.build()
    policy_significance = PolicySignificanceFactory.build()
    activity = ActivityFactory.build()
