from django.test import TestCase
from currency_convert.factory import currency_convert_factory
from decimal import Decimal
from currency_convert.imf_rate_parser import RateParser
from lxml.etree import Element
import unittest
from mock import MagicMock
from lxml.builder import E


class RateParserTestCase(TestCase):
    def setUp(self):
        self.rate_parser = RateParser()
        effective_date = E('EFFECTIVE_DATE')
        rate_value = E('RATE_VALUE', 100, CURRENCY_CODE='Euro', ISO_CHAR_CODE='EUR')
        effective_date.append(rate_value)
        rate_value = E('RATE_VALUE', 10, CURRENCY_CODE='Dollar', ISO_CHAR_CODE='USD')
        effective_date.append(rate_value)
        self.effective_date = effective_date

        self.root_elem =

    def test_prepare_url(self):
        self.rate_parser.min_tick = 8888
        self.rate_parser.max_tick = 7777
        url = self.rate_parser.prepare_url()

        self.assertTrue('8888' in url,
            "From not set in url")
        self.assertTrue('7777' in url,
            "To not set in url")


    def test_parse_day_rates(self):


        self.rate_parser.parse_day_rates(effective_date)
        self.assertEqual(2, len(self.rate_parser.rates))
        self.assertTrue('EUR' in self.rate_parser.rates)
        self.assertTrue('USD' in self.rate_parser.rates)

    def test_parse_data(self):


    def test_save_averages(self):


    def test_ticks(self):


    def test_set_tick_rates(self):

    def test_reset_data(self):

    def test_update_rates(self):