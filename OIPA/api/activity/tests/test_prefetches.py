# TODO: no need to test codelist fields separately; instead test the whole
# serializer in once along with the code and vocabulary fields. Or is
# testing the fields separately preferable?

# Runs each test in a transaction and flushes database
from django.test import RequestFactory, TestCase
from rest_framework.test import APIClient

from api.activity.serializers import ActivitySerializer
from iati.factory.utils import _create_test_activity
from iati.models import Activity


class ActivitySaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        self.activity1 = _create_test_activity(
            id="0001",
            iati_identifier="0001"
        )
        self.activity2 = _create_test_activity(
            id="0002",
            iati_identifier="0002"
        )
        self.activity3 = _create_test_activity(
            id="0003",
            iati_identifier="0003"
        )

    def test_prefetch_reporting_organisations(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 3 queries:
        1. Fetch Activity objects
        2. Fetch ReportingOrganisation objects
        3. Fetch corresponding narratives
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all()\
                .prefetch_reporting_organisations()
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
            queryset = Activity.objects.all()\
                .prefetch_participating_organisations()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('participating_organisations',))

            list(serializer.data)

    def test_prefetch_other_identifiers(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 3 queries:
        1. Fetch Activity objects
        2. Fetch otheridentifier objects
        3. Fetch Narrative objects
        """

        with self.assertNumQueries(3):
            queryset = Activity.objects.all().prefetch_other_identifiers()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('other_identifiers',))

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

    def test_prefetch_contact_info(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch ContactInfo objects
        3. Fetch organisation__narratives objects
        4. Fetch department__narratives objects
        5. Fetch person_name__narratives objects
        6. Fetch job_title__narratives objects
        7. Fetch mailing_address__narratives objects
        """

        with self.assertNumQueries(7):
            queryset = Activity.objects.all().prefetch_contact_info()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('contact_info',))

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

    def test_prefetch_locations(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch Location objects
        6. Fetch LocationAdministrative objects
        3. Fetch LocationNameNarrative objects
        4. Fetch LocationDescriptionNarrative objects
        5. Fetch LocationActivityDescriptionNarrative objects
        TODO: Reduce queries number 09-01-2017
        """

        # TODO: should be 6 queries, LocationAdministrative gets
        # duplicated - 2017-03-27
        with self.assertNumQueries(7):
            queryset = Activity.objects.all().prefetch_locations()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('locations',))

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

    def test_prefetch_country_budget_items(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch CountryBudgetItem objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_country_budget_items()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('country_budget_items',))

            list(serializer.data)

    def test_prefetch_humanitarian_scope(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch HumanitarianScope objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_humanitarian_scope()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('humanitarian_scope',))

            list(serializer.data)

    def test_prefetch_policy_markers(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 4 queries:
        1. Fetch Activity objects
        2. Fetch ActivityPolicyMarker objects
        3. Fetch content_type objects
        4. Fetch narrative objects
        """

        with self.assertNumQueries(4):
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

    def test_prefetch_planned_disbursement(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch PlannedDisbursement objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_planned_disbursement()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('planned_disbursement',))

            list(serializer.data)

    def test_prefetch_document_links(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 7 queries:
        1. Fetch Activity objects.
        2. Fetch DocumentLink objects.
        3. Fetch DocumentLinkLanguage objects.
        4. Fetch DocumentLinkCategory objects.
        5. Fetch Narrative objects.
        6. Fetch DocumentLinkCategory objects.
        7. Fetch DocumentLinkLanguage objects.
        TODO: Verify if the queries 6 and 7 can be deleted.
        """

        with self.assertNumQueries(7):
            queryset = Activity.objects.all().prefetch_document_links()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('document_links',))

            list(serializer.data)

    def test_prefetch_related_activities(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch RelatedActivity objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_related_activities()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('related_activities',))

            list(serializer.data)

    def test_prefetch_legacy_data(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch LegacyData objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_legacy_data()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('legacy_data',))

            list(serializer.data)

    def test_prefetch_conditions(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch conditions objects
        """

        with self.assertNumQueries(1):
            queryset = Activity.objects.all().prefetch_conditions()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('conditions',))

            list(serializer.data)

    def test_prefetch_results(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 16 queries:
        1. Fetch Activity objects
        2. Fetch Result objects
        3. Fetch ResultTitleNarrative objects
        4. Fetch ResultDescriptionNarrative objects
        5. Fetch ResultIndicator objects
        6. Fetch ResultIndicatorReference objects
        7. Fetch ResultIndicatorTitleNarrative objects
        8. Fetch ResultIndicatorDescriptionNarrative objects
        9. Fetch ResultIndicatorBaselineComment objects
        10. Fetch ResultIndicatorPeriod objects
        11. Fetch ResultIndicatorPeriodTargetLocation objects
        12. Fetch ResultIndicatorPeriodActualLocation objects
        13. Fetch ResultIndicatorPeriodTargetDimension objects
        14. Fetch ResultIndicatorPeriodActualDimension objects
        15. Fetch ResultIndicatorPeriodTargetCommentNarrative objects
        16. Fetch ResultIndicatorPeriodActualCommentNarrative objects
        """

        # TODO: this should be 16 - 2017-03-27
        with self.assertNumQueries(60):
            queryset = Activity.objects.all().prefetch_results()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('results',))

            list(serializer.data)

    def test_prefetch_crs_add(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch CrsAdd objects
        3. Fetch crsaddotherflags objects
        """

        with self.assertNumQueries(3):
            queryset = Activity.objects.all().prefetch_crs_add()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('crs_add',))

            list(serializer.data)

    def test_prefetch_fss(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        2. Fetch Fss objects
        """

        with self.assertNumQueries(2):
            queryset = Activity.objects.all().prefetch_fss()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('fss',))

            list(serializer.data)

    def test_prefetch_default_aid_type(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        """

        with self.assertNumQueries(1):
            queryset = Activity.objects.all().prefetch_default_aid_type()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('default_aid_type',))

            list(serializer.data)

    def test_prefetch_default_finance_type(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 2 queries:
        1. Fetch Activity objects
        """

        with self.assertNumQueries(1):
            queryset = Activity.objects.all().prefetch_default_finance_type()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('default_finance_type',))

            list(serializer.data)

    def test_prefetch_aggregations(self):
        """
        Test if the prefetches are applied correctly
        Here we expect 1 queries:
        1. Fetch Activity objects
        """

        with self.assertNumQueries(1):
            queryset = Activity.objects.all().prefetch_aggregations()
            serializer = ActivitySerializer(
                queryset,
                many=True,
                context={'request': self.request_dummy},
                fields=('related_aggregations',))

            list(serializer.data)
