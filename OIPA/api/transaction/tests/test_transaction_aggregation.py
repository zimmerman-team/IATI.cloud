from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from iati.factory import iati_factory
from iati.transaction import factories as transaction_factory


class TransactionAggregationTestCase(TestCase):
    
    def setUp(self):
        """
        set up 2 activities. then create individual tests to check most used aggregation / group by combinations.
        """

        first_activity = iati_factory.ActivityFactory.create()
        second_activity = iati_factory.ActivityFactory.create(
            id='IATI-0002',
            iati_identifier='IATI-0002',
            iati_standard_version=first_activity.iati_standard_version)

        # transaction type = 1 (incoming funds), works the same for disbursements etc.
        first_transaction = transaction_factory.TransactionFactory.create(
            activity=first_activity,
            value=50000)
        second_transaction = transaction_factory.TransactionFactory.create(
            activity=second_activity,
            value=10000,
            transaction_type=first_transaction.transaction_type)
        third_transaction = transaction_factory.TransactionFactory.create(
            activity=second_activity,
            value=25000,
            transaction_type=first_transaction.transaction_type)

        first_sector = iati_factory.SectorFactory.create(code=11000, name='Sector 1')
        second_sector = iati_factory.SectorFactory.create(code=11001, name='Sector 2')

        # TODO: Create appropriate objects here - 2016-04-18
        transaction_sector = transaction_factory.TransactionSectorFactory.create(
            transaction=first_transaction,
            sector=first_sector,
            percentage=100
        )
        transaction_factory.TransactionSectorFactory.create(
            transaction=second_transaction,
            sector=first_sector,
            percentage=50,
            vocabulary=transaction_sector.vocabulary
        )
        transaction_factory.TransactionSectorFactory.create(
            transaction=third_transaction,
            sector=first_sector,
            percentage=50,
            vocabulary=transaction_sector.vocabulary
        )
        transaction_factory.TransactionSectorFactory.create(
            transaction=second_transaction,
            sector=second_sector,
            percentage=50,
            vocabulary=transaction_sector.vocabulary
        )
        transaction_factory.TransactionSectorFactory.create(
            transaction=third_transaction,
            sector=second_sector,
            percentage=50,
            vocabulary=transaction_sector.vocabulary
        )

        country = iati_factory.CountryFactory.build(code="AD", name="Andorra")
        second_country = iati_factory.CountryFactory.build(code="KE", name="Kenya")

        transaction_factory.TransactionRecipientCountryFactory.create(
            transaction=first_transaction,
            country=country,
            percentage=100
        )
        transaction_factory.TransactionRecipientCountryFactory.create(
            transaction=second_transaction,
            country=country,
            percentage=50
        )
        transaction_factory.TransactionRecipientCountryFactory.create(
            transaction=third_transaction,
            country=country,
            percentage=50
        )
        transaction_factory.TransactionRecipientCountryFactory.create(
            transaction=second_transaction,
            country=second_country,
            percentage=50
        )
        transaction_factory.TransactionRecipientCountryFactory.create(
            transaction=third_transaction,
            country=second_country,
            percentage=50
        )

        self.api_client = APIClient()

    def get_results(self, group_by, aggregations, order_by):
        url = ''.join([
            '/api/transactions/aggregations/?format=json&group_by=',
            group_by,
            '&aggregations=',
            aggregations,
            '&order_by=',
            order_by
        ])
        response = self.api_client.get(url)

        return list(response.data['results'])

    def test_sector_incoming_fund_group_by(self):
        """group incoming funds by sector (percentage weighted)

        expected results:
            sector 11000 = 67500 (t1 50000 + t2 5000 + t3 12500)
            sector 11001 = 17500 (t2 5000 + t3 12500)
        """
        results = self.get_results(
            group_by='sector',
            aggregations='incoming_fund',
            order_by='sector')
        
        self.assertTrue(len(results) == 2)

        self.assertEqual(results[0]['incoming_fund'], Decimal(67500))
        self.assertEqual(results[1]['incoming_fund'], Decimal(17500))

    def test_recipient_country_incoming_fund_group_by(self):
        """group incoming funds by recipient country (percentage weighted)

        expected results:
            country AD = 67500 (t1 50000 + t2 5000 + t3 12500)
            country KE = 17500 (t2 5000 + t3 12500)
        """
        results = self.get_results(
            group_by='recipient_country',
            aggregations='incoming_fund',
            order_by='recipient_country')

        self.assertTrue(len(results) == 2)
        self.assertEqual(results[0]['incoming_fund'], Decimal(67500))
        self.assertEqual(results[1]['incoming_fund'], Decimal(17500))

