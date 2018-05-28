

from collections import OrderedDict
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from iati_synchroniser.factory import synchroniser_factory
from iati.permissions.factories import OrganisationAdminGroupFactory, OrganisationUserFactory
from rest_framework.authtoken.models import Token

from iati_synchroniser.models import Publisher
from iati.permissions.models import OrganisationAdminGroup

from iati_synchroniser.factory.synchroniser_factory import PublisherFactory

from iati_codelists.factory import codelist_factory
from iati.factory import iati_factory


class TestActivityPermissions(APITestCase):
    rf = RequestFactory()
    c = APIClient()

    def test_post_activity_success(self):
        """
        Test the user can only POST activities as a publisher of which he is in the admin Group
        """
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.c.force_authenticate(user.user)

        iati_version = codelist_factory.VersionFactory.create(code="2.02")

        data = {
            "iati_identifier": "WOPA",
            "publisher_id": admin_group.publisher.id
        }

        res = self.c.post(
            "/api/publishers/{}/activities/?format=json".format(admin_group.publisher.id),
            data,
            format='json'
        )

        self.assertEquals(res.status_code, 201)

    def test_post_activity_fail_if_not_in_admin_group(self):
        """
        Test the user can only POST activities as a publisher of which he is in the admin Group
        """
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        # admin_group.organisationuser_set.add(user)

        self.c.force_authenticate(user.user)

        publisher = PublisherFactory.create()

        iati_version = codelist_factory.VersionFactory.create(code="2.02")

        data = {
            "iati_identifier": "WOPA",
            "publisher_id": admin_group.publisher.id
        }

        res = self.c.post(
            "/api/publishers/{}/activities/?format=json".format(admin_group.publisher.id),
            data,
            format='json'
        )

        self.assertEquals(res.status_code, 403)

    def test_update_activity_success(self):
        """
        Test the user can only PUT activities as a publisher of which he is in the admin Group
        """
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.c.force_authenticate(user.user)

        activity = iati_factory.ActivityFactory.create(publisher=admin_group.publisher)

        data = {
            "iati_identifier": "WOPA",
            "publisher_id": activity.publisher.id
        }

        res = self.c.put(
            "/api/publishers/{}/activities/{}/?format=json".format(
                activity.publisher.id, activity.id),
            data,
            format='json'
        )

        self.assertEquals(res.status_code, 200)

    def test_update_activity_fail_if_not_in_admin_group(self):
        """
        Test the user can only PUT activities as a publisher of which he is in the admin Group
        """
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        # admin_group.organisationuser_set.add(user)

        self.c.force_authenticate(user.user)

        activity = iati_factory.ActivityFactory.create(publisher=admin_group.publisher)

        data = {
            "iati_identifier": "WOPA",
            "publisher_id": activity.publisher.id
        }

        res = self.c.put(
            "/api/publishers/{}/activities/{}/?format=json".format(
                activity.publisher.id, activity.id),
            data,
            format='json'
        )

        self.assertEquals(res.status_code, 403)

    def test_get_activity_success(self):
        """
        Test the user can GET any activity that is not on "draft" status
        """
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.c.force_authenticate(user.user)

        activity = iati_factory.ActivityFactory.create(publisher=admin_group.publisher)

        data = {
            "iati_identifier": "WOPA",
            "publisher_id": activity.publisher.id
        }

        res = self.c.put(
            "/api/publishers/{}/activities/{}/?format=json".format(
                activity.publisher.id, activity.id),
            data,
            format='json'
        )

        self.assertEquals(res.status_code, 200)
