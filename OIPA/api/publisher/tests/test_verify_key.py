

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
from iati.permissions.models import OrganisationAdminGroup, OrganisationGroup, OrganisationUser

class TestVerifyApiKey(APITestCase):
    rf = RequestFactory()
    c = APIClient()

    @unittest.skip("ew! set apiKey and userId manually below")
    def test_verify_api_key_success(self):
        """
        An organization admin should be able to verify an API key
        """
        admin_group = OrganisationAdminGroupFactory.create()
        user = UserFactory.create(username='test1')

        admin_group.user_set.add(user)

        self.c.force_authenticate(user)

        data={
            "apiKey": "",
            "userId": "",
        }

        res = self.c.post(
                "/api/publishers/{}/verify-api-key/?format=json".format(admin_group.publisher.id), 
                data=data,
                format='json'
                )

        # test api key has been set on user
        updated_user = OrganisationUser.objects.get(pk=user.pk)
        self.assertEqual(updated_user.iati_api_key, data['apiKey'])

        # test publisher has been created
        publisher = Publisher.objects.all()[1]

        # test organisation groups have been created
        org_group = OrganisationGroup.objects.get(publisher=publisher)
        self.assertEqual(org_group.user_set.get(pk=updated_user.id), updated_user)

        org_admin_group = OrganisationAdminGroup.objects.get(publisher=publisher)
        self.assertEqual(org_admin_group.user_set.get(pk=updated_user.id), updated_user)
        self.assertEqual(org_admin_group.owner, updated_user)


