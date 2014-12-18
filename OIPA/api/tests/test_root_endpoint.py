from django.core.urlresolvers import reverse


class TestRootEndpoint:

    def test_root_endpoint(self):
        url = reverse('api-root')

        expect_url = '/api/'
        msg = 'root endpoint should be localed at {0}'
        assert url == expect_url, msg.format(expect_url)
