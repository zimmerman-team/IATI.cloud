import json
from functools import lru_cache

from django.conf import settings


class Currencies(object):
    """
    An object instantiating and containing the currencies
    """

    def __init__(self):
        self.currencies_list = self.read_currencies()

    def read_currencies(self):
        path = settings.CURRENCIES_JSON
        with open(path) as file:
            return json.load(file)

    @lru_cache(maxsize=100)  # Cache the last 100 results
    def get_currency(self, month, year, currency_id):
        """
        Get the currency for a given month and year.
        Rudimentary approach proved to be the fastest,
        compared to several pandas approaches.

        :param month: the month
        :param year: the year
        :param currency_id: the currency id
        :return: a dict containing the currency converted monthly average.
        """
        if None in (month, year, currency_id):
            return None

        return next(
            (
                item
                for item
                in self.currencies_list
                if item['month'] == month and item['year'] == year and item['currency_id'] == currency_id  # noqa
            ), None
        )

    def convert_currency(self, source, target, value, month, year):
        """
        Convert a given currency from a source, to a target, for a given
        month and year. For example: 5 Euro to USD at 2022-02

        Steps:
        Check if source == target, return value
        Convert the source to the XDR.
        Return the XDR if the XDR is the target.
        Convert the XDR to the target.

        Testing the implementation against existing IATI.cloud:
        https://datastore.iati.cloud/api/v2/transaction/?q=iati_identifier:NL-KVK-32092131-2060  # noqa
        has "transaction_value": 32720.0, "transaction_value_usd": 35676.43,
        and transaction_value_currency": "EUR".

        calling this function with the above example, the result is: 35676.43128806548  # noqa

        :param source: the source currency
        :param target: the target currency
        :param value: float: the value to convert
        :param month: int: the month
        :param year: int: the year
        :return: the converted value and the exchange rate from source to target
        """
        if None in (source, target, value, month, year):
            return None, None

        if source == target:
            return value, 1  # 1 on 1 relation

        source_conversion = self.get_currency(month, year, source)
        target_conversion = self.get_currency(month, year, target)
        if not source_conversion or not target_conversion:
            return None, None
        source_to_xdr_rate = source_conversion['value']
        xdr_to_target_rate = target_conversion['value']

        converted_value = value * source_to_xdr_rate
        if target == 'XDR':
            return converted_value, source_to_xdr_rate

        exchange_rate = xdr_to_target_rate / source_to_xdr_rate

        return converted_value / xdr_to_target_rate, exchange_rate
