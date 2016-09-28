
# TODO: no need to test codelist fields separately; instead test the whole serializer in once along with the code and vocabulary fields. Or is testing the fields separately preferable?

from django.test import TestCase # Runs each test in a transaction and flushes database
from unittest import skip
import datetime

from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from iati.factory import iati_factory
from iati_codelists.factory import codelist_factory
from api.activity import serializers
from iati import models as iati_models
from django.core.exceptions import ObjectDoesNotExist

# TODO: separate into several test cases
class ActivitySaveSerializerTestCase(TestCase):

    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_reporting_org(self):

        activity = iati_factory.ActivityFactory.create()
        organisation = iati_factory.OrganisationFactory.create()
        iati_factory.OrganisationTypeFactory.create(code=9)
        iati_factory.OrganisationRoleFactory.create(code=1)

        data = {
            "ref": 'GB-COH-03580586',
            "activity": activity.id,
            "organisation": organisation.id,
            "type": {
                "code": '9',
                "name": 'irrelevant',
            },
            "secondary_reporter": 1,
        }

        res = self.c.post(
                "/api/activities/{}/reporting_organisations/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.ActivityReportingOrganisation.objects.get(ref=data['ref'])

        self.assertEqual(instance.ref, data['ref'])
        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.type.code, data['type']['code'])
        self.assertEqual(instance.secondary_reporter, bool(data['secondary_reporter']))

    def test_update_reporting_org(self):
        reporting_org = iati_factory.ReportingOrganisationFactory.create()
        iati_factory.OrganisationTypeFactory.create(code=9)

        data = {
            "ref": 'GB-COH-03580586',
            "activity": reporting_org.activity.id,
            "organisation": reporting_org.organisation.id,
            "type": {
                "code": '9',
                "name": 'irrelevant',
            },
            "secondary_reporter": 1,
        }

        res = self.c.put(
                "/api/activities/{}/reporting_organisations/{}?format=json".format(reporting_org.activity.id, reporting_org.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.ActivityReportingOrganisation.objects.get(ref=data['ref'])

        self.assertEqual(instance.ref, data['ref'])
        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.type.code, data['type']['code'])
        self.assertEqual(instance.secondary_reporter, bool(data['secondary_reporter']))


    def test_delete_reporting_org(self):
        reporting_org = iati_factory.ReportingOrganisationFactory.create()

        res = self.c.delete(
                "/api/activities/{}/reporting_organisations/{}?format=json".format(reporting_org.activity.id, reporting_org.id), 
                format='json'
                )

        print(res.status_code)
        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.ActivityReportingOrganisation.objects.get(ref=reporting_org.ref)

