import pytest
from django.core.urlresolvers import reverse
from api.tests.endpoint_base import EndpointBase
from rest_framework import status


@pytest.mark.django_db
class TestOrganisationEndpoints(EndpointBase):

    def test_organisations_endpoint(self, client, organisation):
        url = reverse('organisation-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)

    def test_organisation_detail_endpoint(self, client, organisation):
        url = reverse('organisation-detail', args={'GB-COH-03580586'})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)
