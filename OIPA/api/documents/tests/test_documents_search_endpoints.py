from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestDocumentsSearchEndpoints(APITestCase):
    def test_documents_search_endpoint(self):
        url = reverse('documents:document-list')
        expect_url = '/api/documents/'
        assert url == expect_url, msg.format('Documents Search endpoint should be located at {0}')
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
