from django.contrib.gis.geos import Point
import factory
from geodata import models


class NoDatabaseFactory(factory.django.DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0


class CityFactory(NoDatabaseFactory):
    class Meta:
        model = models.City

    geoname_id = 1000
    name = 'dummy_city'
    location = Point(5, 23)


class CountryFactory(NoDatabaseFactory):
    class Meta:
        model = models.Country

    code = 'OO'
    name = 'dummy_country'
    center_longlat = Point(1, 3)


class RegionFactory(NoDatabaseFactory):
    class Meta:
        model = models.Region

    code = '689'
    name = 'South & Central Asia, regional'
    center_longlat = Point(2,4)


class Adm1RegionFactory(NoDatabaseFactory):
    class Meta:
        model = models.Adm1Region

    adm1_code = 'ABW-5150'
    name = "State in Aruba"


