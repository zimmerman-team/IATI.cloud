from django.urls import reverse
from rest_framework.test import APITestCase

from iati_codelists.factory import codelist_factory


class TestSectorEndpoints(APITestCase):

    def test_sectors_endpoint(self):
        url = reverse('sectors:sector-list')

        msg = 'sectors endpoint should be localed at {0}'
        expect_url = '/api/sectors/'
        assert url == expect_url, msg.format(expect_url)

    def test_sector_detail_endpoint(self):
        codelist_factory.SectorFactory.create(code='200')
        url = reverse('sectors:sector-detail', args={'200'})

        msg = 'sector detail endpoint should be localed at {0}'
        expect_url = '/api/sectors/200/'
        assert url == expect_url, msg.format(expect_url)
