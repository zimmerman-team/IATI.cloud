import pytest
from django.core.urlresolvers import reverse
from api.tests.endpoint_base import EndpointBase
from rest_framework import status

from iati.factory import iati_factory
from api.activity import serializers


@pytest.mark.django_db
class TestActivityEndpoints(EndpointBase):

    def test_activities_endpoint(self, client, activity):
        url = reverse('activity-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)

    def test_activity_detail_endpoint(self, client, activity):
        url = reverse('activity-detail', args={'IATI-0001'})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)

    def test_activity_sectors_endpoint(self, client, activitysector):
        url = reverse('activity-sectors', args={'IATI-0001'})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)

    def test_participating_orgs_endpoint(self, client, participatingorg):
        url = reverse(
            'activity-participating-organisations',
            args={'IATI-0001'})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)

    def test_recipient_countries_endpoint(self, client, recipientcountry):
        url = reverse('activity-recipient-countries', args={'IATI-0001'})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)


class TestActivitySerializers:

    def test_AidTypeSerializer(self):
        aidtype_category = iati_factory.AidTypeCategoryFactory.build(
            code=1,
            name='aid_category',
            description='a category',
        )
        aidtype = iati_factory.AidTypeFactory.build(
            code=10,
            name='aid type',
            description='a description',
            category=aidtype_category,
        )
        s = serializers.DefaultAidTypeSerializer(aidtype)
        assert s.data == 10001
