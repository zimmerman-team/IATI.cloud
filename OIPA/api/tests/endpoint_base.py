import pytest
from iati.factory import iati_factory
from rest_framework.test import APIClient


class EndpointBase:

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def activity(self):
        return iati_factory.ActivityFactory()

    @pytest.fixture
    def region(self):
        return iati_factory.RegionFactory()

    @pytest.fixture
    def country(self):
        return iati_factory.CountryFactory()

    @pytest.fixture
    def city(self):
        return iati_factory.CityFactory()

    @pytest.fixture
    def organisation(self):
        return iati_factory.OrganisationFactory()

    @pytest.fixture
    def sector(self):
        return iati_factory.SectorFactory()

    @pytest.fixture
    def activitysector(self):
        return iati_factory.ActivitySectorFactory()

    @pytest.fixture
    def recipientcountry(self):
        return iati_factory.RecipientCountryFactory()

    @pytest.fixture
    def participatingorg(self):
        return iati_factory.ParticipatingOrganisationFactory()
