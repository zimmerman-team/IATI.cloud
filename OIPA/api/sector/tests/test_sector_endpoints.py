from django.core.urlresolvers import reverse


class TestSectorEndpoints():

    def test_sectors_endpoint(self):
        url = reverse('sector-list')

        msg = 'sectors endpoint should be localed at {0}'
        expect_url = '/api/sectors/'
        assert url == expect_url, msg.format(expect_url)

    def test_sector_detail_endpoint(self):
        url = reverse('sector-detail', args={'200'})

        msg = 'sector detail endpoint should be localed at {0}'
        expect_url = '/api/sectors/200/'
        assert url == expect_url, msg.format(expect_url)

    def test_sector_activities_endpoint(self):
        url = reverse('sector-activities', args={'200'})

        msg = 'sector detail endpoint should be localed at {0}'
        expect_url = '/api/sectors/200/activities/'
        assert url == expect_url, msg.format(expect_url)
