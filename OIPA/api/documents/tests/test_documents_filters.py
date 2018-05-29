from datetime import datetime

from django.conf import settings
from django.test import RequestFactory, TestCase
from rest_framework.test import APIClient

from iati.factory import iati_factory


class TestDocumentsSearchFilters(TestCase):

    request_dummy = RequestFactory().get('/')
    c = APIClient()

    if settings.FTS_ENABLED:
        def test_documents_search_filter(self):
            url = '/api/documents/?document_q=aaaaaaaaaaa&format=json'
            response = self.c.get(url)
            self.assertEquals(response.status_code, 200, response.json())
            self.assertEqual(response.json()['count'], 0)

        def test_documents_indexing(self):
            document_content = "Aid may serve one or more functions: it may\
                be given as a signal of diplomatic approval, or to strengthen\
                a military ally, to reward a government for behaviour desired\
                by the donor, to extend the donor's cultural influence, to\
                provide infrastructure needed by the donor for resource\
                extraction from the recipient country, or to gain other\
                kinds of commercial access. Humanitarian and altruistic\
                purposes are at least partly responsible for the giving of\
                aid."
            iati_factory.DocumentFactory.create(
                document_content=document_content
            )
            document_search = iati_factory.DocumentSearchFactory.create(
                content=document_content
            )
            document_search.text = " ".join([document_search.content, ])
            document_search.last_reindexed = datetime.now()
            document_search.save()

            url = '/api/documents/?document_q=aid&format=json'

            response = self.c.get(url)
            self.assertEquals(response.status_code, 200, response.json())
            self.assertEqual(response.json()['count'], 1)
