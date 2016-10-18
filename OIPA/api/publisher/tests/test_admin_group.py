
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from iati_synchroniser.factory import synchroniser_factory
from iati.permissions.factories import AdminGroupFactory, UserFactory
from rest_framework.authtoken.models import Token

from iati_synchroniser.models import Publisher
from iati.permissions.models import AdminGroup

class TestAdminGroupAPI(APITestCase):
    rf = RequestFactory()
    c = APIClient()

    def test_add_user_to_admin_group_fail(self):
        """
        Make sure adding a user to admin group fails when the user is not in the admin group
        """
        admin_group = AdminGroupFactory.create()
        user = UserFactory.create(username='test1')
        new_user = UserFactory.create(username='test2')

        # admin_group.user_set.add(user)

        self.c.force_authenticate(user)

        data = {
            "user_id": new_user.id,
        }

        res = self.c.post(
                "/api/publishers/{}/admin-group/?format=json".format(admin_group.publisher.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 403)


    def test_add_user_to_admin_group_success(self):
        """
        Adding a user to an admin group when the user is in the admin group
        """
        admin_group = AdminGroupFactory.create()
        user = UserFactory.create(username='test1')
        new_user = UserFactory.create(username='test2')

        admin_group.user_set.add(user)

        self.c.force_authenticate(user)

        data = {
            "user_id": new_user.id,
        }

        res = self.c.post(
                "/api/publishers/{}/admin-group/?format=json".format(admin_group.publisher.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200)
        self.assertEquals(len(AdminGroup.objects.get(pk=admin_group.id).user_set.all()), 2)

    def test_user_cant_remove_owner(self):
        """
        Make sure the initial creator of the admin group can't be removed from the admin group
        """
        admin_group = AdminGroupFactory.create()
        user = UserFactory.create(username='test1')
        new_user = UserFactory.create(username='test2')

        admin_group.user_set.add(new_user)
        admin_group.user_set.add(user)
        admin_group.owner = new_user
        admin_group.save()

        self.c.force_authenticate(user)

        data = {
            "user_id": new_user.id,
        }

        res = self.c.post(
                "/api/publishers/{}/admin-group/?format=json".format(admin_group.publisher.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 401)

