from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from iati_synchroniser.factory import synchroniser_factory


class TestPublisherEndpoints(APITestCase):

    def test_publishers_endpoint(self):
        url = reverse('publishers:publisher-list')

        msg = 'publishers endpoint should be localed at {0}'
        expect_url = '/api/publishers/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_publisher_detail_endpoint(self):
        synchroniser_factory.PublisherFactory.create(id=1)
        url = reverse('publishers:publisher-detail', args={1})

        msg = 'publisher detail endpoint should be localed at {0}'
        expect_url = '/api/publishers/1/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
