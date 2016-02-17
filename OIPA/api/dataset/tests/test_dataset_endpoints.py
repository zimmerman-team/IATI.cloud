from django.test import TestCase
from django.core.urlresolvers import reverse


class TestDatasetEndpoints(TestCase):

    def test_datasets_endpoint(self):
        url = reverse('datasets:dataset-list')

        msg = 'datasets endpoint should be localed at {0}'
        expect_url = '/api/datasets/'
        assert url == expect_url, msg.format(expect_url)

    def test_dataset_detail_endpoint(self):
        url = reverse('datasets:dataset-detail', args={'id'})

        msg = 'dataset detail endpoint should be localed at {0}'
        expect_url = '/api/datasets/id/'
        assert url == expect_url, msg.format(expect_url)

