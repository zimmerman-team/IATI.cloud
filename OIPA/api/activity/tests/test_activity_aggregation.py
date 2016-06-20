from django.test import TestCase
from iati.factory import iati_factory
from iati.transaction import factories as transaction_factory
from rest_framework.test import APIClient
from decimal import Decimal


class ActivityAggregationTestCase(TestCase):
    def setUp(self):
        """set up 2 activities with the shown specs

        then create individual tests to check most used aggregation / group by combinations.

        activity 1
            id - IATI-0001
            sectors
                sector 1
                    code        - 11000
                    name        - Sector 1
                    percentage  - 100
            recipient countries
                country 1
                    code        - AD
                    name        - Andorra
                    percentage  - 50
            budgets
                budget 1
                    value       - 20000
                budget 2
                    value       - 50000
            transactions
                transaction 1
                    type        - incoming funds
                    value       - 50000

        activity 2
            id - IATI-0002
            sectors
                sector 1
                    code        - 11000
                    name        - Sector 1
                    percentage  - 50
                sector 2
                    code        - 11001
                    name        - Sector 2
                    percentage  - 50
            recipient countries
                country 1
                    code        - AD
                    name        - Andorra
                    percentage  - 50
                country 2
                    code        - KE
                    name        - Kenya
                    percentage  - 50
            budgets
                budget 1
                    value       - 80000
            transactions
                transaction 1
                    type        - incoming funds
                    value       - 10000
                transaction 1
                    type        - incoming funds
                    value       - 25000

        """

        first_activity = iati_factory.ActivityFactory.create()
        second_activity = iati_factory.ActivityFactory.create(
            id='IATI-0002',
            iati_identifier='IATI-0002',
            iati_standard_version=first_activity.iati_standard_version)
        first_sector = iati_factory.SectorFactory.build(code=11000, name='Sector 1')
        activity_sector = iati_factory.ActivitySectorFactory.create(
            activity=first_activity,
            sector=first_sector,
            percentage=100
        )
        iati_factory.ActivitySectorFactory.create(
            activity=second_activity,
            sector=first_sector,
            percentage=50,
            vocabulary=activity_sector.vocabulary
        )

        second_sector = iati_factory.SectorFactory.build(code=11001, name='Sector 2')
        iati_factory.ActivitySectorFactory.create(
            activity=second_activity,
            sector=second_sector,
            percentage=50,
            vocabulary=activity_sector.vocabulary
        )

        country = iati_factory.CountryFactory.build(code="AD", name="Andorra")
        iati_factory.ActivityRecipientCountryFactory.create(
            activity=first_activity,
            country=country,
            percentage=100
        )
        iati_factory.ActivityRecipientCountryFactory.create(
            activity=second_activity,
            country=country,
            percentage=50
        )

        second_country = iati_factory.CountryFactory.build(code="KE", name="Kenya")
        iati_factory.ActivityRecipientCountryFactory.create(
            activity=second_activity,
            country=second_country,
            percentage=50
        )

        iati_factory.BudgetFactory.create(activity=first_activity, value=20000)
        iati_factory.BudgetFactory.create(activity=first_activity, value=50000)
        iati_factory.BudgetFactory.create(activity=second_activity, value=80000)

        # transaction type = 1 (incoming funds), works the same for disbursements etc.
        first_transaction = transaction_factory.TransactionFactory.create(
            activity=first_activity,
            value=50000)
        transaction_factory.TransactionFactory.create(
            activity=second_activity,
            value=10000,
            transaction_type=first_transaction.transaction_type)
        transaction_factory.TransactionFactory.create(
            activity=second_activity,
            value=25000,
            transaction_type=first_transaction.transaction_type)

        self.api_client = APIClient()

    def get_results(self, group_by, aggregations, order_by):
        url = ''.join([
            '/api/activities/aggregations/?format=json&group_by=',
            group_by,
            '&aggregations=',
            aggregations,
            '&order_by=',
            order_by
        ])
        response = self.api_client.get(url)
        return list(response.data['results'])


    # def test_sector_budget_group_by(self):
    #     """group budget by sector, this is the non percentage aware sector aggregation

    #     expected results:
    #         sector 11000 = 150000 (70000 + 80000)
    #         sector 11001 = 80000
    #     """
    #     results = self.get_results(
    #         group_by='sector',
    #         aggregations='budget',
    #         order_by='sector')

    #     self.assertTrue(len(results) == 2)
    #     self.assertEqual(results[0]['budget'], Decimal(150000))
    #     self.assertEqual(results[1]['budget'], Decimal(80000))

    # def test_sector_weighted_budget_aggregation(self):
    #     """group sector weighted budget by sector, this makes budgets percentage aware

    #     expected results:
    #         sector 11000 = 110000 (70000 * 100% + 80000 * 50%)
    #         sector 11001 = 40000 (80000 * 50%)
    #     """
    #     results = self.get_results(
    #         group_by='sector',
    #         aggregations='sector_percentage_weighted_budget',
    #         order_by='sector')
        
    #     self.assertTrue(len(results) == 2)
    #     self.assertEqual(results[0]['budget'], Decimal(110000))
    #     self.assertEqual(results[1]['budget'], Decimal(40000))

    # def test_recipient_country_budget_group_by(self):
    #     """group budget by recipient country, this is the non percentage aware sector aggregation

    #     expected results:
    #         sector 11000 = 150000 (70000 + 80000)
    #         sector 11001 = 80000
    #     """
    #     results = self.get_results(
    #         group_by='recipient_country',
    #         aggregations='budget',
    #         order_by='recipient_country')

    #     self.assertTrue(len(results) == 2)
    #     self.assertEqual(results[0]['budget'], Decimal(150000))
    #     self.assertEqual(results[1]['budget'], Decimal(80000))
