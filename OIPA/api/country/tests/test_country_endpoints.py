from django.core.urlresolvers import reverse


class TestRegionEndpoints():

    def test_countries_endpoint(self):
        url = reverse('country-list')

        msg = 'countries endpoint should be localed at {0}'
        expect_url = '/api/countries/'
        assert url == expect_url, msg.format(expect_url)

    def test_country_detail_endpoint(self):
        url = reverse('country-detail', args={'id'})

        msg = 'country detail endpoint should be localed at {0}'
        expect_url = '/api/countries/id/'
        assert url == expect_url, msg.format(expect_url)
