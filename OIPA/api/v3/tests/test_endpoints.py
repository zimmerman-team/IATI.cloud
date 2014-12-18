import pytest
from api.v3.tests.endpoint_base import EndpointBase


@pytest.mark.django_db
class TestEndpoints(EndpointBase):

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

    def test_activity_aggregate_any_endpoint(self, client):
        response = client.get('/api/v3/activity-aggregate-any/')
        assert response.status_code == 200

    def test_activity_filter_orpions_endpoint(
            self, client, region, sector, country):
        response = client.get('/api/v3/activity-filter-options/')
        assert response.status_code == 200

    def test_activity_list_vis_endpoint(self, client, region):
        response = client.get('/api/v3/activity-list-vis/')
        assert response.status_code == 200

    def test_country_activity_endpoint(self, client, country):
        response = client.get('/api/v3/country-activities/')
        assert response.status_code == 200

    def test_country_geojson_endpoint(self, client, country):
        response = client.get('/api/v3/country-geojson/')
        assert response.status_code == 200

    def test_donor_activities_endpoint(self, client, organisation):
        response = client.get('/api/v3/donor-activities/')
        assert response.status_code == 200

    def test_region_activities_endpoint(self, client, region):
        response = client.get('/api/v3/region-activities/')
        assert response.status_code == 200

    def test_sector_activities_endpoint(self, client, sector):
        response = client.get('/api/v3/sector-activities/')
        assert response.status_code == 200

    def test_indicator_filter_option_endpoint(self, client):
        response = client.get('/api/v3/indicator-filter-options/')
        assert response.status_code == 200

    def test_adm1_region_geojson_endpoint(self, client):
        response = client.get('/api/v3/adm1-region-geojson/?country_id=NL')
        assert response.status_code == 200

    def test_global_activities_endpoint(self, client):
        response = client.get('/api/v3/global-activities/')
        assert response.status_code == 200
