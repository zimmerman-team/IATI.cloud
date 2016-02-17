from django.test import TestCase
from django.core.urlresolvers import reverse


class TestPublisherEndpoints(TestCase):

    def test_publishers_endpoint(self):
        url = reverse('publishers:publisher-list')

        msg = 'publishers endpoint should be localed at {0}'
        expect_url = '/api/publishers/'
        assert url == expect_url, msg.format(expect_url)

    def test_publisher_detail_endpoint(self):
        url = reverse('publishers:publisher-detail', args={'id'})

        msg = 'publisher detail endpoint should be localed at {0}'
        expect_url = '/api/publishers/id/'
        assert url == expect_url, msg.format(expect_url)
