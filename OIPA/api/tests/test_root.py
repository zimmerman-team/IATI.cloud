from django.core.urlresolvers import reverse
from rest_framework import status


class TestRootEndpoint:

    def test_root_endpoint(self, client):
        url = reverse('api-root')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)
