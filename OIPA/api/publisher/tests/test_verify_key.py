

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
from iati.permissions.models import OrganisationAdminGroup, OrganisationGroup, OrganisationUser

from iati.factory.iati_factory import OrganisationFactory


def fake_call_action(self, arg, whatever):
    if arg is "organization_list_for_user":
        return [{u'image_display_url': u'',
                 u'display_name': u'Zimmerman & Zimmerman',
                 u'description': u'',
                 u'created': u'2014-02-12T06:23:00.548603',
                 u'package_count': 2,
                 u'title': u'Zimmerman & Zimmerman',
                 u'name': u'zimmzimm',
                 u'is_organization': True,
                 u'state': u'active',
                 u'image_url': u'',
                 u'revision_id': u'test',
                 u'type': u'organization',
                 u'id': u'test',
                 u'approval_status': u'approved'}]
    elif arg is "user_show":
        return {}
    elif arg is "organization_show":
        return {
            u'publisher_frequency': u'',
            u'package_count': 2,
            u'publisher_record_exclusions': u'',
            u'num_followers': 1,
            u'publisher_implementation_schedule': u'',
            u'publisher_country': u'NL',
            u'id': u'test',
            u'publisher_refs': u'',
            u'display_name': u'Zimmerman & Zimmerman',
            u'title': u'Zimmerman & Zimmerman',
            u'publisher_units': u'',
            u'publisher_contact': u'Mr. S. Vaessen\r\nOostelijke Handelskade 12H\r\n1019 BM Amsterdam\r\nThe Netherlands',
            u'state': u'active',
            u'publisher_field_exclusions': u'',
            u'publisher_description': u'Developing the OIPA framework for IATI data parsing, data sanitation and visualization.',
            u'license_id': u'cc-zero',
            u'type': u'organization',
            u'publisher_thresholds': u'',
            u'description': u'',
            u'publisher_organization_type': u'70',
            u'tags': [],
            u'groups': [],
            u'publisher_ui_url': u'http://www.openaidsearch.org',
            u'publisher_timeliness': u'',
            u'publisher_source_type': u'primary_source',
            u'publisher_segmentation': u'',
            u'publisher_frequency_select': u'not_specified',
            u'publisher_agencies': u'',
            u'name': u'zimmzimm',
            u'users': [
                {
                    u'capacity': u'admin',
                    u'name': u'zimmzimm'}],
            u'publisher_iati_id': u'NL-KVK-51018586',
            u'publisher_ui': u'www.openaidsearch.org',
            u'image_display_url': u'',
            u'is_organization': True,
            u'image_url': u'',
            u'publisher_constraints': u'',
            u'publisher_data_quality': u''}


from ckanapi import RemoteCKAN, NotAuthorized
RemoteCKAN.call_action = fake_call_action


class TestVerifyApiKey(APITestCase):
    rf = RequestFactory()
    c = APIClient()

    def test_verify_api_key_success(self):
        """
        An organization admin should be able to verify an API key
        """
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        organisation = OrganisationFactory.create(organisation_identifier="NL-KVK-51018586")

        self.c.force_authenticate(user.user)

        data = {
            "apiKey": "this_is_mocked",
            "userId": "this_is_mocked",
        }

        res = self.c.post(
            "/api/publishers/api_key/verify/",
            data=data,
            format='json'
        )

        print(res.status_code)

        # test api key has been set on user
        updated_user = OrganisationUser.objects.get(pk=user.pk)
        self.assertEqual(updated_user.iati_api_key, data['apiKey'])

        # test publisher has been created
        publisher = Publisher.objects.all()[1]

        # test organisation groups have been created
        org_group = OrganisationGroup.objects.get(publisher=publisher)
        self.assertEqual(org_group.organisationuser_set.get(pk=updated_user.id), updated_user)

        org_admin_group = OrganisationAdminGroup.objects.get(publisher=publisher)
        self.assertEqual(
            org_admin_group.organisationuser_set.get(
                pk=updated_user.id), updated_user)
        self.assertEqual(org_admin_group.owner, updated_user)
