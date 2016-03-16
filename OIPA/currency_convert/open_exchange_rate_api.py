from openexchangerates.exchange import Exchange
from django.conf import settings
from datetime import date


app_id = settings.OPENEXCHANGERATES_APP_ID
local_dir = "~/.openexchangerates"
exchange = Exchange(local_dir, app_id)


def to_xdr(currency_iso, value_date, value):
    first_day_of_month = date(value_date.year, value_date.month, 1)
    rates = exchange.historical_rates(first_day_of_month)
    return exchange.exchange(float(value), currency_iso, "XDR", rates)



def from_xsd(currency_iso, value_date, value):
    first_day_of_month = date(value_date.year, value_date.month, 1)
    rates = exchange.historical_rates(first_day_of_month)
    return exchange.exchange(value, "XDR", currency_iso, rates)
