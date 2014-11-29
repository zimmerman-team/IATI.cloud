import iati
import geodata
import factory


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


class DescriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Description

    description = 'description factory'


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = iati.models.Activity
        django_get_or_create = ('id',)

    id = 'IATI-0001'
    total_budget = 50
    iati_identifier = 'IATI-0001'
    title_set = factory.RelatedFactory(TitleFactory, 'activity_id',)
    description_set = factory.RelatedFactory(DescriptionFactory, 'activity_id')


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
