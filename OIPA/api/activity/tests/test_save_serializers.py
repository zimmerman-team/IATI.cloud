
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
            "ref": 'a-ref',
            "activity": activity.id,
            "organisation": organisation.id,
            "type": {
                "code": 9,
                "name": 'irrelevant',
            },
            "secondary_reporter": True,
        }

        res = self.c.post(
                "/api/activities/{}/reporting_organisations/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201)

        print(iati_models.ActivityReportingOrganisation.objects.all())
        instance = iati_models.ActivityReportingOrganisation.objects.get(ref="a-ref")

        self.assertEqual(instance.ref, data['ref'])
        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.type.code, data['type']['code'])
        self.assertEqual(instance.secondary_reporter, data['secondary_reporter'])

        # print(res)
        # print(res.json())


    def test_partial_update(self):
        """
        Test if a non-nested element can partially be saved
        """
        activity = iati_factory.ActivityFactory.create()

        data={ 'humanitarian': True }
        activity_serializer = serializers.ActivitySerializer(activity, context={'request': self.request_dummy}, data=data, partial=True)

        self.assertTrue(activity_serializer.is_valid(raise_exception=True))
        activity_serializer.save()

        activity.refresh_from_db()
        self.assertEqual(activity.humanitarian, True)

        

    def test_nested_partial_update(self):
        activity = iati_factory.ActivityFactory.create()
        participating_org = iati_factory.ParticipatingOrganisationFactory.create(activity=activity)

        iati_factory.OrganisationTypeFactory.create(code=9)
        iati_factory.OrganisationRoleFactory.create(code=1)

        data={ 'participating_organisations': [
            {"id": participating_org.id, "ref":"GB","type":{"code":"9","name":"Government"},"role":{"code":"1","name":"Funding"}}
            ]}
        activity_serializer = serializers.ActivitySerializer(activity, context={'request': self.request_dummy}, data=data, partial=True)


        self.assertTrue(activity_serializer.is_valid(raise_exception=True))
        activity_serializer.save()

        # print(activity_serializer.data)

        participating_org.refresh_from_db()
        self.assertEqual(participating_org.normalized_ref, "GB")
        self.assertEqual(participating_org.type.code, "9")
        self.assertEqual(participating_org.role.code, "1")

        # print(activity.participating_organisations.all()[0].type)

    def test_nested_partial_add(self):
        activity = iati_factory.ActivityFactory.create()
        iati_factory.OrganisationTypeFactory.create(code=9)
        iati_factory.OrganisationRoleFactory.create(code=1)

        data={ 'participating_organisations': [
            {"ref":"GB","type":{"code":"9","name":"Government"},"role":{"code":"1","name":"Funding"}}
            ]}
        activity_serializer = serializers.ActivitySerializer(activity, context={'request': self.request_dummy}, data=data, partial=True)

        self.assertTrue(activity_serializer.is_valid(raise_exception=True))
        activity_serializer.save()

        # print(activity_serializer.data)

        participating_org.refresh_from_db()

        participating_org = iati_models.ActivityParticipatingOrganisation.get(ref="GB")
        self.assertEqual(participating_org.normalized_ref, "GB")
        self.assertEqual(participating_org.type.code, "9")
        self.assertEqual(participating_org.role.code, "1")
    def test_nested_codelist_update(self):
        """
        Test updating a codelist code, only updates the fk code
        """
        pass
