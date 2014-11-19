import pytest
from django.test.client import Client
from iati.factory import iati_factory


@pytest.mark.django_db
class TestEndpoints:

    @pytest.fixture
    def client(self):
        return Client()

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

    def test_activities_endpoint(self, client, activity):
        response = client.get('/api/v3/activities/')
        assert response.status_code == 200

    def test_activity_detail_endpoint(self, client, activity):
        response = client.get('/api/v3/activities/IATI-0001/')
        assert response.status_code == 200

    def test_region_detail_endpoint(self, client, region):
        response = client.get('/api/v3/regions/1/')
        assert response.status_code == 200

    def test_countries_endpoint(self, client, country):
        response = client.get('/api/v3/countries/')
        assert response.status_code == 200

    def test_country_detail_endpoint(self, client, country):
        response = client.get('/api/v3/countries/AD/')
        assert response.status_code == 200

    def test_cities_endpoint(self, client, city):
        response = client.get('/api/v3/cities/')
        assert response.status_code == 200

    def test_city_detail_endpoint(self, client, city):
        response = client.get('/api/v3/cities/1/')
        assert response.status_code == 200

    def test_organisations_endpoins(self, client, organisation):
        response = client.get('/api/v3/organisations/')
        assert response.status_code == 200

    def test_organisation_detail_endpoint(self, client, organisation):
        response = client.get('/api/v3/organisations/GB-COH-03580586/')
        assert response.status_code == 200

    def test_sectors_endpoint(self, client, sector):
        response = client.get('/api/v3/sectors/')
        assert response.status_code == 200

    def test_sector_detail_endpoint(self, client, sector):
        response = client.get('/api/v3/sectors/200/')
        assert response.status_code == 200
