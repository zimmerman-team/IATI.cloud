#from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import RequestFactory, Client
from rest_framework.test import APIClient

class TestDocumentsSearchFilters(TestCase):

	request_dummy = RequestFactory().get('/')
	c = APIClient()
	
	def test_documents_search_filter(self):
		url = '/api/document-links/?document_q=azeerereraaaaaaaaaaaaaaaaaaaaaaaaaaaaaa&format=json'
		response = self.c.get(url)
		self.assertEquals(response.status_code, 200, response.json())
		self.assertEqual(response.json()['count'], 0)
