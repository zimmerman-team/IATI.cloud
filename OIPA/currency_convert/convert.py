from currency_convert.models import MonthlyAverage
from django.core.exceptions import ObjectDoesNotExist


def get_monthly_average(currency_iso, value_date):
    try:
        ma = MonthlyAverage.objects.get(year=value_date.year, month=value_date.month, currency=currency_iso)
        return ma.value
    except ObjectDoesNotExist:
        # print 'exchange rate for %s does not exist for year %s and month %s' % (
        #     currency_iso,
        #     value_date.year,
        #     value_date.month)
        return False

def to_xdr(currency_iso, value_date, value):
    exchange_rate_to_xdr = get_monthly_average(currency_iso, value_date)
    if exchange_rate_to_xdr:
        return value * exchange_rate_to_xdr
    else:
        return 0

def from_xdr(currency_iso, value_date, value):
    exchange_rate_to_xdr = get_monthly_average(currency_iso, value_date)
    if exchange_rate_to_xdr:
        return value / exchange_rate_to_xdr
    else:
        return 0
