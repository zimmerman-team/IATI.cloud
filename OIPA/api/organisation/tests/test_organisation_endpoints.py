from django.core.urlresolvers import reverse


class TestOrganisationEndpoints():

    def test_organisations_endpoint(self):
        url = reverse('organisation-list')

        msg = 'organisations endpoint should be localed at {0}'
        expect_url = '/api/organisations'
        assert url == expect_url, msg.format(expect_url)

    def test_organisation_detail_endpoint(self):
        url = reverse('organisation-detail', args={'organisation-id'})

        msg = 'organisation list endpoint should be localed at {0}'
        expect_url = '/api/organisations/organisation-id'
        assert url == expect_url, msg.format(expect_url)

    def test_reported_activities_endpoint(self):
        url = reverse('organisation-reported-activities', args={'code'})

        msg = 'organisation-reported-activities should be located at {0}'
        expect_url = '/api/organisations/code/reported-activities'
        assert url == expect_url, msg.format(expect_url)

    def test_participated_activities_endpoint(self):
        url = reverse('organisation-participated-activities', args={'code'})

        msg = 'organisation-participated-activities should be located at {0}'
        expect_url = '/api/organisations/code/participated-activities'
        assert url == expect_url, msg.format(expect_url)
