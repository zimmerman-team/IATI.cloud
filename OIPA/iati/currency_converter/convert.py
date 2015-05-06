import json
month_file = open('iati/currency_converter/json/xdr_month.json')
month_data = json.load(month_file)


def to_xdr(currency, date, value):
    date_key = _get_date_key(date)
    rate = month_data[date_key][currency.code]
    return float(value) * rate


def to_currency(currency, date, value):
    date_key = _get_date_key(date)
    rate = month_data[date_key][currency]
    return '{0:0.2f}'.format(float(value) / rate)


def _get_date_key(date):
    return '{0}-{1:02d}'.format(date.year, date.month)
