from django.core.urlresolvers import reverse


class TestActivityEndpoints:

    def test_root_endpoint(self, client):
        url = reverse('api-root')
        response = client.get(url)
        assert response.status_code == 200
