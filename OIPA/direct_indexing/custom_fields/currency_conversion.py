import datetime


def currency_conversion(data, currencies):
    """
    For the following fields the currency converted value is expected:
    budget_value_usd, planned_disbursement_value_usd and transaction_value_usd.
    Along with the conversion rate. Lastly, we provide the sum of each activity.

    :param data: reference to the activity in the data
    :param currencies: an initialized currencies object.
    """
    default_currency = None
    if 'default-currency' in data.keys():
        default_currency = data['default-currency']

    for field in ['budget', 'planned-disbursement', 'transaction']:
        if field not in data.keys():
            continue

        value = []
        rate = []
        t_type = []
        first_currency = ""
        if type(data[field]) == list:
            for item in data[field]:
                c_value, c_rate, currency = convert(item, currencies,
                                                    default_currency=default_currency)
                value.append(c_value)
                rate.append(c_rate)
                if field == 'transaction':
                    t_type.append(item['transaction-type']['code'])
                if first_currency == "":
                    first_currency = currency
        else:  # data is a reference thus not assigned
            c_value, c_rate, first_currency = convert(data[field], currencies,
                                                      default_currency=default_currency)
            value.append(c_value)
            rate.append(c_rate)
            if field == 'transaction':
                t_type.append(data['transaction']['transaction-type']['code'])

        if len(value) > 0:
            data[f'{field}.value-usd'] = value
            data[f'{field}.value-usd.sum'] = sum(value)
            data[f'{field}.value-usd.conversion-rate'] = rate
            data[f'{field}.value-usd.conversion-currency'] = first_currency
            if field == 'transaction':
                data[f'{field}.value-usd-type'] = t_type
    return data


def convert(data, currencies, default_currency=None, target_currency='USD'):
    """
    Convert a value from a source to a target currency based on the input.
    Make sure we have the currencies and the fields all exist.

    :param data: reference to the activity in the data
    :param currencies: an initialized currencies object.
    :param default_currency: the default currency to use if no currency is found.
    :param target_currency: the target currency to convert to, defaults to USD.
    :return: the converted value and the conversion rate and the currency, or None, None, None.
    """
    if 'value' not in data.keys():
        return None, None, None

    currency = None
    if 'value.currency' in data.keys():
        currency = data['value.currency']

    if not currency:
        if default_currency:
            currency = default_currency

    if not currency:
        return None, None, None

    year, month = get_ym(data)
    if not year or not month:
        return None, None, None

    converted_value, rate = currencies.convert_currency(
        currency, target_currency, data['value'], month, year)
    return converted_value, rate, currency


def get_ym(data):
    """
    value-dates are reported as XSD:Date which is always yyyy-mm-dd.

    :param data: reference to the value in the data
    :return: year and month or None if not found
    """
    try:
        if 'value.value-date' in data.keys():
            date = data['value.value-date']
            year = int(date[:4])
            month = int(date[5:7])

            # If the month is in the future, pick current year/month
            now = datetime.datetime.now()
            if year > now.year:
                year = now.year

            if year == now.year and month > now.month:
                month = now.month

            return year, month
        else:
            return None, None
    except:  # NOQA
        return None, None  # No valid date was found
