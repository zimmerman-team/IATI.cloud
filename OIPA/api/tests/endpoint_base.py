import pytest
from iati.factory import iati_factory
from rest_framework.test import APIClient


class EndpointBase:

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def basic_activity(self):
        return iati_factory.ActivityFactory()

    @pytest.fixture
    def basic_region(self):
        return iati_factory.RegionFactory()

    @pytest.fixture
    def basic_country(self):
        return iati_factory.CountryFactory()

    @pytest.fixture
    def basic_city(self):
        return iati_factory.CityFactory()

    @pytest.fixture
    def basic_organisation(self):
        return iati_factory.OrganisationFactory()

    @pytest.fixture
    def basic_sector(self):
        return iati_factory.SectorFactory()
