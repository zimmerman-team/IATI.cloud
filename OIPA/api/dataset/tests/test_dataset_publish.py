import unittest

from django.test import RequestFactory, TestCase

from iati.permissions.factories import (
    OrganisationAdminGroupFactory, UserFactory
)


class TestDatasetPublish(TestCase):
    request_dummy = RequestFactory().get('/')

    @unittest.skip("Not implemented")
    def test_publish_dataset_success(self):
        """
        Publish a publisher's activities in one file when the user is in the
        corresponding admin group
        """
        admin_group = OrganisationAdminGroupFactory.create()
        user = UserFactory.create(username='test1')
        new_user = UserFactory.create(username='test2')

        admin_group.user_set.add(user)
        admin_group.user_set.add(new_user)

        self.c.force_authenticate(user)

        self.c.get(
            "/api/publishers/{}/admin-group/?format=json".format(
                admin_group.publisher.id
            ),
        )
