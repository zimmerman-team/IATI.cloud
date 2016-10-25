

from collections import OrderedDict
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from iati_synchroniser.factory import synchroniser_factory
from iati.permissions.factories import OrganisationAdminGroupFactory, UserFactory
from rest_framework.authtoken.models import Token

from iati_synchroniser.models import Publisher
from iati.permissions.models import OrganisationAdminGroup

class TestVerifyApiKey(APITestCase):
    rf = RequestFactory()
    c = APIClient()

    def test_verify_api_key_success(self):
        """
        An organization admin should be able to verify an API key
        """
        admin_group = OrganisationAdminGroupFactory.create()
        user = UserFactory.create(username='test1')

        admin_group.user_set.add(user)

        self.c.force_authenticate(user)

        res = self.c.post(
                "/api/publishers/{}/verify-api-key/?format=json".format(admin_group.publisher.id), 
                data={
                    "apiKey": "",
                    "userId": "",
                },
                format='json'
                )

        print(res.status_code)


