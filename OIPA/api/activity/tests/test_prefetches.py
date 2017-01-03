

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

    def test_prefetch_reporting_organisations(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 3 queries:
        1. Fetch Activity objects
        2. Fetch ReportingOrganisation objects
        3. Fetch corresponding narratives
        """


        with self.assertNumQueries(3):
            queryset = Activity.objects.all().prefetch_reporting_organisations()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('reporting_organisations',))

            list(serializer.data)


    def test_prefetch_title(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 3 queries:
        1. Fetch Activity objects
        2. Fetch title narratives
        """


        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_title()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('title',))

            list(serializer.data)

    def test_prefetch_descriptions(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 3 queries:
        1. Fetch Activity objects
        2. Fetch Description objects
        3. Fetch corresponding narratives
        """


        with self.assertNumQueries(3):
            queryset = Activity.objects.all().prefetch_descriptions()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('descriptions',))

            list(serializer.data)


    def test_prefetch_participating_organisations(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 3 queries:
        1. Fetch Activity objects
        2. Fetch ParticipatingOrganisation objects
        3. Fetch corresponding narratives objects
        """


        with self.assertNumQueries(3):
            queryset = Activity.objects.all().prefetch_participating_organisations()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('participating_organisations',))

            list(serializer.data)


    def test_prefetch_recipient_countries(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 3 queries:
        1. Fetch Activity objects
        2. Fetch ActivityRecipientCountry objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_recipient_countries()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('recipient_countries',))

            list(serializer.data)

    def test_prefetch_recipient_regions(self):

        """
        Test if the prefetches are applied correctly
        Here we expect 8 queries:
        1. Fetch Activity objects
        2. Fetch ActivityRecipientRegion objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_recipient_regions()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('recipient_regions',))

            list(serializer.data)

    def test_prefetch_sectors(self):

        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch ActivitySector objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_sectors()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('sectors',))

            list(serializer.data)

    def test_prefetch_activity_dates(self):

        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch ActivityDate objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_activity_dates()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('activity_dates',))

            list(serializer.data)

    def test_prefetch_policy_markers(self):

        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch ActivityPolicyMarker objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_policy_markers()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('policy_markers',))

            list(serializer.data)

    def test_prefetch_budgets(self):

        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch Budget objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_budgets()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('budgets',))

            list(serializer.data)

    def test_prefetch_document_links(self):

        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch DocumentLink objects
        3. Fetch DocumentLinkCategory objects
        4. Fetch DocumentLinkCategory objects
        5. Fetch DocumentLinkLanguage objects
        6. Fetch Language objects
        7. Fetch DocumentLinkTitle objects
        8. Fetch Narrative objects
        9. Fetch Language objects
        10. Fetch Language objects
        11. Fetch DocumentLinkLanguage objects
        12. Fetch Language objects
        13. Fetch DocumentLinkTitle objects
        14. Fetch Narrative objects
        15. Fetch Language objects
        16. Fetch Language objects
        17. Fetch DocumentLinkLanguage objects
        18. Fetch Language objects
        19. Fetch DocumentLinkTitle objects
        20. Fetch Narrative objects
        21. Fetch Language objects
        22. Fetch Language objects
        """

        with self.assertNumQueries(22):
            queryset = Activity.objects.all().prefetch_document_links()
            serializer = ActivitySerializer(
                    queryset, 
                    many=True,
                    context={'request': self.request_dummy},
                    fields=('document_links',))

            list(serializer.data)