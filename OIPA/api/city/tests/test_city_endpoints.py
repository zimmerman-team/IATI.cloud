from django.core.urlresolvers import reverse


class TestCityEndpoints():

    def test_cities_endpoint(self):
        url = reverse('city-list')

        msg = 'cities endpoint should be localed at {0}'
        expect_url = '/api/cities/'
        assert url == expect_url, msg.format(expect_url)

    def test_city_detail_endpoint(self):
        url = reverse('city-detail', args={'1'})

        msg = 'city detail endpoint should be localed at {0}'
        expect_url = '/api/cities/1/'
        assert url == expect_url, msg.format(expect_url)
