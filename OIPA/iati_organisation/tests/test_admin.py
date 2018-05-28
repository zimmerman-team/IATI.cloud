from mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from iati.factory.iati_factory import OrganisationFactory
from iati_organisation.models import Organisation
from iati_organisation.admin import OrganisationAdmin


class MockRequest(object):
    pass


class MockSuperUser(object):
    def has_perm(self, perm):
        return True


request = MockRequest()
request.user = MockSuperUser()


class OrganisationAdminTestCase(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.organisation = OrganisationFactory.create(
            organisation_identifier='org-12345')

    def test_get_urls(self):

        organisation_admin = OrganisationAdmin(self.organisation, self.site)
        patterns = []
        for url in organisation_admin.get_urls():
            patterns.append(url.pattern.regex.pattern)

        added_patterns = ['^update-primary-names/$']

        for pattern in added_patterns:
            self.assertIn(pattern, patterns)

    def test_update_primary_names(self):
        organisation_admin = OrganisationAdmin(self.organisation, self.site)

        data = {
            "org-12345": "Org. name",
        }
        organisation_admin.get_json_data = MagicMock(return_value=data)
        organisation_admin.update_primary_names(request)

        org = Organisation.objects.last()
        self.assertEqual(org.primary_name, "Org. name")
