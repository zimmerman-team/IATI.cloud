from django.test import TestCase
from iati.factory import iati_factory
from iati.transaction import factories as transaction_factory
from rest_framework.test import APIClient
from decimal import Decimal

class ActivityAggregationTestCase(TestCase):
    def setUp(self):
        # set up 2 activities with the shown specs,
        # then create individual tests to check most used aggregation / group by combinations
        # 2 activities
        # both in sector 11000, second also in 11001 for 50 perc


        first_activity = iati_factory.ActivityFactory.create()
        second_activity = iati_factory.ActivityFactory.create(
            id='IATI-0002',
            iati_identifier='IATI-0002',
            iati_standard_version=first_activity.iati_standard_version)
        first_sector = iati_factory.SectorFactory.build(code=11000, name='Sector 1')
        first_activity_sector = iati_factory.ActivitySectorFactory.create(
            activity=first_activity,
            sector=first_sector,
            percentage=100
        )
        second_activity_sector = iati_factory.ActivitySectorFactory.create(
            activity=second_activity,
            sector=first_sector,
            percentage=50,
            vocabulary=first_activity_sector.vocabulary
        )

        second_sector = iati_factory.SectorFactory.build(code=11001, name='Sector 2')
        second_activity_second_sector = iati_factory.ActivitySectorFactory.create(
            activity=second_activity,
            sector=second_sector,
            percentage=50,
            vocabulary=first_activity_sector.vocabulary
        )

        country = iati_factory.CountryFactory.build() # code = AD, name = andorra
        first_activity_country = iati_factory.ActivityRecipientCountryFactory.create(
            activity=first_activity,
            country=country,
            percentage=100
        )
        second_activity_country = iati_factory.ActivityRecipientCountryFactory.create(
            activity=second_activity,
            country=country,
            percentage=50
        )

        second_country = iati_factory.CountryFactory.build(code="KE", name="Kenya")
        third_activity_country = iati_factory.ActivityRecipientCountryFactory.create(
            activity=second_activity,
            country=second_country,
            percentage=50
        )

        first_budget = iati_factory.BudgetFactory.create(activity=first_activity, value=20000)
        second_budget = iati_factory.BudgetFactory.create(activity=first_activity, value=50000)
        third_budget = iati_factory.BudgetFactory.create(activity=second_activity, value=80000)

        # transaction type = 1 (incoming funds), works the same for disbursements etc. so no need to change
        first_transaction = transaction_factory.TransactionFactory.create(activity=first_activity, value=50000)
        second_transaction = transaction_factory.TransactionFactory.create(activity=second_activity, value=10000, transaction_type=first_transaction.transaction_type)
        third_transaction = transaction_factory.TransactionFactory.create(activity=second_activity, value=25000, transaction_type=first_transaction.transaction_type)

        self.api_client = APIClient()


    def test_sector_incoming_fund_group_by(self):
        """
            group by sector, this is the non percentage aware sector aggregation
        """
        response = self.api_client.get('/api/activities/aggregations/?format=json&group_by=sector&aggregations=incoming_fund&order_by=sector')

        results = list(response.data['results'])
        self.assertTrue(len(results) == 2)
        self.assertEqual(results[0]['incoming_fund'], Decimal(85000))
        self.assertEqual(results[1]['incoming_fund'], Decimal(35000))

    def test_sector_budget_group_by(self):
        """
            group by sector, this is the non percentage aware sector aggregation
            sector 11000 = 70000 + 80000 = 150000
            sector 11001 = 80000
        """
        response = self.api_client.get('/api/activities/aggregations/?format=json&group_by=sector&aggregations=budget&order_by=sector', format='json')

        results = list(response.data['results'])

        self.assertTrue(len(results) == 2)
        self.assertEqual(results[0]['budget'], Decimal(150000))
        self.assertEqual(results[1]['budget'], Decimal(80000))

    def test_sector_weighted_budget_aggregation(self):
        """
            group by sector, aggregate by sector weighted budget
            this makes budgets percentage aware
            sector 11000 = 70000 * 100% + 80000 * 50% = 110000
            sector 11001 = 80000 * 50% = 40000
        """
        response = self.api_client.get('/api/activities/aggregations/?format=json&group_by=sector&aggregations=sector_percentage_weighted_budget&order_by=sector', format='json')

        results = list(response.data['results'])
        
        self.assertTrue(len(results) == 2)
        self.assertEqual(results[0]['budget'], Decimal(110000))
        self.assertEqual(results[1]['budget'], Decimal(40000))

    def test_recipient_country_incoming_fund_group_by(self):
        """
            group budget by recipient country, this is the non percentage aware sector aggregation
        """
        response = self.api_client.get('/api/activities/aggregations/?format=json&group_by=recipient_country&aggregations=incoming_fund&order_by=recipient_country')

        results = list(response.data['results'])
        
        self.assertTrue(len(results) == 2)
        self.assertEqual(results[0]['incoming_fund'], Decimal(85000))
        self.assertEqual(results[1]['incoming_fund'], Decimal(35000))

    def test_recipient_country_budget_group_by(self):
        """
            group budget by recipient country, this is the non percentage aware sector aggregation
            sector 11000 = 70000 + 80000 = 150000
            sector 11001 = 80000
        """
        response = self.api_client.get('/api/activities/aggregations/?format=json&group_by=recipient_country&aggregations=budget&order_by=recipient_country', format='json')

        results = list(response.data['results'])

        self.assertTrue(len(results) == 2)
        self.assertEqual(results[0]['budget'], Decimal(150000))
        self.assertEqual(results[1]['budget'], Decimal(80000))
