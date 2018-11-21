from datetime import datetime
from decimal import Decimal
from urllib.error import URLError

import mechanicalsoup
from django.test import TestCase
from lxml.builder import E
from mock import MagicMock, Mock

from currency_convert import convert
from currency_convert.factory.currency_convert_factory import (
    MonthlyAverageFactory
)
from currency_convert.imf_rate_parser import RateBrowser, RateParser
from currency_convert.models import MonthlyAverage
from iati_codelists.models import Currency


class RateBrowserTestCase(TestCase):

    def setUp(self):
        """

        """
        self.rate_browser = RateBrowser()

    def test_prepare_browser(self):
        """
        test if returns a browser
        """
        self.assertTrue(isinstance(
            self.rate_browser.browser, mechanicalsoup.Browser))

    def test_retry_on_urlerror(self):
        """
        should retry 2 times when receiving an URL error
        """
        self.rate_browser.browser.open = Mock(
            side_effect=URLError('cant connect...'))


class RateParserTestCase(TestCase):

    def create_rate_value_elem(self, value, currency_name, currency_iso):
        return E(
            'RATE_VALUE', str(value), CURRENCY_CODE=currency_name,
            ISO_CHAR_CODE=currency_iso)

    def create_effective_date_elem(self, date_value, rate_values):
        effective_date = E('EFFECTIVE_DATE', VALUE=date_value)
        effective_date.append(
            self.create_rate_value_elem(rate_values, 'Euro', 'EUR'))
        effective_date.append(self.create_rate_value_elem(
            rate_values, 'Dollar', 'USD'))
        return effective_date

    def setUp(self):
        """
        create 1 root element, which contains
        2 effective date elements, which contains
        2 rate value elements, 1st with exchange rates 1.5, second with rate
        2.0
        """
        effective_date = self.create_effective_date_elem(
            '02-Jan-1997', Decimal(1.5))
        effective_date_2 = self.create_effective_date_elem(
            '03-Jan-1997', Decimal(2.00000))
        root_elem = E('EXCHANGE_RATE_REPORT')
        root_elem.append(effective_date)
        root_elem.append(effective_date_2)

        self.rate_parser = RateParser()
        self.rate_parser.now = datetime(1995, 1, 31)
        self.effective_date = effective_date
        self.root_elem = root_elem

    def test_prepare_url(self):
        self.rate_parser.min_tick = 8888
        self.rate_parser.max_tick = 7777
        url = self.rate_parser.prepare_url()

        self.assertTrue('8888' in url,
                        "From not set in url")
        self.assertTrue('7777' in url,
                        "To not set in url")

    def test_parse_day_rates(self):
        self.rate_parser.parse_day_rates(self.effective_date)
        self.assertEqual(2, len(self.rate_parser.rates))
        self.assertTrue('EUR' in self.rate_parser.rates)
        self.assertTrue('USD' in self.rate_parser.rates)
        self.assertTrue(self.rate_parser.rates['EUR'].get('values')[0] == 1.5)

    def test_parse_data(self):
        """

        """
        self.rate_parser.parse_day_rates = MagicMock()
        self.rate_parser.parse_data(self.root_elem)
        self.assertEqual(self.rate_parser.parse_day_rates.call_count, 2)

    def test_save_averages(self):
        self.rate_parser.parse_data(self.root_elem)
        self.rate_parser.save_averages()
        average_item = MonthlyAverage.objects.filter(
            month=12, year=1993, currency='EUR')[0]
        self.assertTrue(average_item.value == 1.75)

    def test_ticks(self):
        dt = datetime(1994, 1, 1)
        ticks = self.rate_parser.ticks(dt)
        self.assertEqual(ticks, 628929792000000000)

    def test_set_tick_rates(self):
        self.rate_parser.year = 1994
        self.rate_parser.month = 1
        self.rate_parser.set_tick_rates()
        self.assertEqual(self.rate_parser.min_tick, 628929792000000000)
        self.assertEqual(self.rate_parser.max_tick, 628955712000000000)

    def test_reset_data(self):
        self.rate_parser.rates = {'currencies': 'averages'}
        self.rate_parser.reset_data()
        self.assertEqual(self.rate_parser.rates, {})

    def test_create_browser(self):
        browser = self.rate_parser.create_browser()
        self.assertTrue(isinstance(browser, RateBrowser))

    def test_update_rates(self):
        currency, created = Currency.objects.get_or_create(
            code='EUR', name='Euro')
        MonthlyAverageFactory.create(
            year=1994, month=1, currency=currency, value=1)
        self.rate_parser.create_browser = MagicMock()
        self.rate_parser.parse_data = MagicMock()
        self.rate_parser.save_averages = MagicMock()
        self.rate_parser.update_rates(force=False)

        self.assertEqual(12, self.rate_parser.parse_data.call_count)

    def test_force_update_rates(self):
        currency, created = Currency.objects.get_or_create(
            code='EUR', name='Euro')
        MonthlyAverageFactory.create(
            year=1994, month=1, currency=currency, value=1)
        self.rate_parser.create_browser = MagicMock()
        self.rate_parser.parse_data = MagicMock()
        self.rate_parser.save_averages = MagicMock()
        self.rate_parser.update_rates(force=True)

        self.assertEqual(13, self.rate_parser.create_browser.call_count)
        self.assertEqual(13, self.rate_parser.parse_data.call_count)
        self.assertEqual(13, self.rate_parser.save_averages.call_count)


class ConvertTestCase(TestCase):

    def setUp(self):
        currency, created = Currency.objects.get_or_create(
            code='EUR', name='Euro')
        MonthlyAverageFactory.create(
            year=1994, month=1, currency=currency, value=1.5)
        usd_currency, created = Currency.objects.get_or_create(
            code='USD', name='USD')
        MonthlyAverageFactory.create(
            year=1994, month=1, currency=usd_currency, value=3)

    def test_currency_from_to(self):
        """

        """
        value_date = datetime(1994, 1, 1)
        rate = convert.currency_from_to('USD', 'EUR', value_date, 200)
        self.assertEqual(rate, 400)

    def test_currency_from_to_xdr(self):
        """
            when converted to xdr, only to_xdr should be called.
        """
        value_date = datetime(1994, 1, 1)
        rate = convert.currency_from_to('USD', 'XDR', value_date, 100)
        self.assertEqual(rate, 300)

    def test_currency_from_to_does_not_exist(self):
        """

        """
        value_date = datetime(1995, 1, 1)
        rate = convert.currency_from_to('USD', 'UGX', value_date, 100)
        self.assertEqual(rate, 0)

    def test_to_xdr(self):
        """

        """
        value_date = datetime(1994, 1, 1)
        rate = convert.to_xdr('EUR', value_date, 100)
        self.assertEqual(rate, 150)

    def test_to_xdr_does_not_exist(self):
        """

        """
        value_date = datetime(1995, 1, 1)
        rate = convert.to_xdr('EUR', value_date, 100)
        self.assertEqual(rate, 0)

    def test_from_xdr(self):
        """

        """
        value_date = datetime(1994, 1, 1)
        rate = convert.from_xdr('EUR', value_date, 150)
        self.assertEqual(rate, 100)

    def test_from_xdr_does_not_exist(self):
        """

        """
        value_date = datetime(1995, 1, 1)
        rate = convert.from_xdr('EUR', value_date, 100)
        self.assertEqual(rate, 0)
