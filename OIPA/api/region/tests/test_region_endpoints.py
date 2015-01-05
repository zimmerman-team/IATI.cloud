from django.core.urlresolvers import reverse


class TestRegionEndpoints():

    def test_regions_endpoint(self):
        url = reverse('region-list')

        msg = 'regions endpoint should be localed at {0}'
        expect_url = '/api/regions/'
        assert url == expect_url, msg.format(expect_url)

    def test_region_detail_endpoint(self):
        url = reverse('region-detail', args={'1'})

        msg = 'region detail endpoint should be localed at {0}'
        expect_url = '/api/regions/1/'
        assert url == expect_url, msg.format(expect_url)

    def test_region_countries_endpoint(self):
        url = reverse('region-countries', args={'1'})

        msg = 'region detail endpoint should be localed at {0}'
        expect_url = '/api/regions/1/countries/'
        assert url == expect_url, msg.format(expect_url)

    def test_region_activities_endpoint(self):
        url = reverse('region-activities', args={'1'})

        msg = 'region detail endpoint should be localed at {0}'
        expect_url = '/api/regions/1/activities/'
        assert url == expect_url, msg.format(expect_url)
