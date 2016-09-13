
# TODO: no need to test codelist fields separately; instead test the whole serializer in once along with the code and vocabulary fields. Or is testing the fields separately preferable?

from django.test import TestCase # Runs each test in a transaction and flushes database
from unittest import skip
import datetime

from django.test import RequestFactory
from iati.factory import iati_factory
from iati_codelists.factory import codelist_factory
from api.activity import serializers


# TODO: separate into several test cases
class ActivitySaveSerializerTestCase(TestCase):

    request_dummy = RequestFactory().get('/')

    def test_partial_update(self):
        """
        Test if a non-nested element can partially be saved
        """
        activity = iati_factory.ActivityFactory.create()

        data={ 'humanitarian': True }
        activity_serializer = serializers.ActivitySerializer(activity, data=data, partial=True)

        self.assertTrue(activity_serializer.is_valid(raise_exception=True))

        activity_serializer.save()

    def test_nested_partial_update(self):
        activity = iati_factory.ActivityFactory.create()
        participating_org = iati_factory.ParticipatingOrganisationFactory.create(activity=activity)

        data={ 'participating_organisations': [
            {"id": participating_org.id, "ref":"GB","type":{"code":"9","name":"Government"},"role":{"code":"1","name":"Funding"}}
            ]}
        activity_serializer = serializers.ActivitySerializer(activity, data=data, partial=True)

        self.assertTrue(activity_serializer.is_valid(raise_exception=True))

        activity_serializer.save()

        # print(activity.participating_organisations.all()[0].type)

