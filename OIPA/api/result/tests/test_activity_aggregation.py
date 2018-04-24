from django.test import TestCase
from iati.factory import iati_factory
from iati.transaction import factories as transaction_factory
from rest_framework.test import APIClient
from decimal import Decimal
import datetime


class ResultAggregationTestCase(TestCase):
    def setUp(self):
        """set up 2 rsults

        then create individual tests to check most used aggregation / group by combinations.

        """
        activity = iati_factory.ActivityFactory.create()
        result_type = iati_factory.ResultTypeFactory.create()

        first_result = iati_factory.ResultFactory.create(activity=activity, type=result_type)
        second_result = iati_factory.ResultFactory.create(activity=activity, type=result_type)

        first_result_indicator = iati_factory.ResultIndicatorFactory.create(
            result=first_result,
        )
        second_result_indicator = iati_factory.ResultIndicatorFactory.create(
            result=second_result,
        )

        date_now = datetime.datetime.now()

        first_result_indicator_period = iati_factory.ResultIndicatorPeriodFactory.create(
            result_indicator=first_result_indicator,
            period_start=date_now,
            period_end=date_now,
            target="10",
            actual=None
        )

        second_result_indicator_period = iati_factory.ResultIndicatorPeriodFactory.create(
            result_indicator=first_result_indicator,
            period_start=date_now,
            period_end=date_now,
            target="100",
            actual="30"
        )

        third_result_indicator_period = iati_factory.ResultIndicatorPeriodFactory.create(
            result_indicator=second_result_indicator,
            period_start=date_now,
            period_end=date_now,
            target="20",
            actual="10"
        )

        self.api_client = APIClient()

    def get_results(self, group_by, aggregations, order_by):
        url = ''.join([
            '/api/results/aggregations/?format=json&group_by=',
            group_by,
            '&aggregations=',
            aggregations,
            '&order_by=',
            order_by
        ])
        response = self.api_client.get(url)
        return list(response.data['results'])

    def test_sector_budget_group_by(self):
        """group actual and target by result_indicator_title

        expected results:
            target 130 = 10 + 100 + 20
            actual 40 = 0 + 30 + 10
        """
        results = self.get_results(
            group_by='result_indicator_title',
            aggregations='actual,target',
            order_by='result_indicator_title')
        self.assertTrue(len(results) == 1)
        # self.assertEqual(results[0]['result_indicator_title'], 'a')
        self.assertEqual(results[0]['target'], Decimal(130))
        self.assertEqual(results[0]['actual'], Decimal(40))
