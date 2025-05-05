from django.core.exceptions import ObjectDoesNotExist

from legacy_currency_convert.models import MonthlyAverage


def get_imf_url_and_exchange_rate(from_currency_iso, value_date):
    try:
        ma = MonthlyAverage.objects.get(
            year=value_date.year,
            month=value_date.month,
            currency='USD'
        )
        exchange_rate_to_xdr = get_monthly_average(from_currency_iso,
                                                   value_date)
        if exchange_rate_to_xdr:
            exchange_rate_from_currency_to_usd = exchange_rate_to_xdr/ma.value
            return ma.imf_url, exchange_rate_from_currency_to_usd
        else:
            return ma.imf_url, None
    except ObjectDoesNotExist:
        return None, None


def get_monthly_average(currency_iso, value_date):
    try:
        ma = MonthlyAverage.objects.get(
            year=value_date.year,
            month=value_date.month,
            currency=currency_iso)
        return ma.value
    except ObjectDoesNotExist:
        return False


def currency_from_to(from_currency_iso, to_currency_iso, value_date, value):
    if from_currency_iso is to_currency_iso:
        return value

    xdr_value = to_xdr(from_currency_iso, value_date, value)

    if to_currency_iso == 'XDR':
        return xdr_value

    requested_value = from_xdr(to_currency_iso, value_date, xdr_value)
    return requested_value


def to_xdr(currency_iso, value_date, value):
    if None in (currency_iso, value_date, value):
        return 0

    exchange_rate_to_xdr = get_monthly_average(currency_iso, value_date)
    if exchange_rate_to_xdr:
        return value * exchange_rate_to_xdr
    else:
        return 0


def from_xdr(currency_iso, value_date, value):
    if None in (currency_iso, value_date, value):
        return 0

    exchange_rate_from_xdr = get_monthly_average(currency_iso, value_date)
    if exchange_rate_from_xdr:
        return value / exchange_rate_from_xdr
    else:
        return 0
