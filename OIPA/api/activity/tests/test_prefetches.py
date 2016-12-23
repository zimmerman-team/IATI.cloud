

# TODO: no need to test codelist fields separately; instead test the whole serializer in once along with the code and vocabulary fields. Or is testing the fields separately preferable?

from django.test import TestCase # Runs each test in a transaction and flushes database
from unittest import skip
import datetime

from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from iati.factory import iati_factory
from iati.transaction import factories as transaction_factory
from iati_codelists.factory import codelist_factory
from iati_vocabulary.factory import vocabulary_factory
from api.activity import serializers
from iati import models as iati_models
from iati.transaction import models as transaction_models
from django.core.exceptions import ObjectDoesNotExist

from decimal import Decimal

from iati.models import Activity
from iati.factory.utils import _create_test_activity
from api.activity.serializers import ActivitySerializer

class ActivitySaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        self.activity1 = _create_test_activity(id="0001", iati_identifier="0001")
        self.activity2 = _create_test_activity(id="0002", iati_identifier="0002")
        self.activity3 = _create_test_activity(id="0003", iati_identifier="0003")

    def test_prefetch_participating_organisations(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 3 queries:
        1. Fetch Activity objects
        2. Fetch ParticipatingOrganisation objects
        2. Fetch corresponding narratives
        3. 
        """


        with self.assertNumQueries(3):
            queryset = Activity.objects.all().prefetch_participating_organisations()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('participating_organisations',))

            list(serializer.data)


    def test_prefetch_reporting_organisations(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 3 queries:
        1. Fetch Activity objects
        2. Fetch ReportingOrganisation objects
        2. Fetch corresponding narratives
        3. 
        """


        with self.assertNumQueries(3):
            queryset = Activity.objects.all().prefetch_reporting_organisations()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('reporting_organisations',))

            list(serializer.data)
