import iati
import geodata
import factory


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
