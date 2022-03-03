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
    if 'default-currency' in data:
        default_currency = data['default-currency']

    for field in ['budget', 'planned-disbursement', 'transaction']:
        if field not in data:
            continue

        value = []
        rate = []
        t_type = []
        first_currency = ""
        if type(data[field]) is list:
            value, rate, first_currency, t_type = \
                convert_currencies_from_list(data, field, currencies, default_currency,
                                             value, rate, first_currency, t_type)
        else:  # data is a reference thus not assigned
            value, rate, first_currency, t_type = \
                convert_currencies_from_dict(data, field, currencies, default_currency, value, rate, t_type)

        data = save_converted_value_to_data(data, value, field, rate, first_currency, t_type)
    return data


def convert_currencies_from_list(data, field, currencies, default_currency, value, rate, first_currency, t_type):
    for item in data[field]:
        c_value, c_rate, currency = convert(item, currencies,
                                            default_currency=default_currency)
        value.append(c_value)
        rate.append(c_rate)
        if field == 'transaction':
            app = 0  # Transaction type/code are 1..1 in the standard, therefore app should always be non-zero.
            if 'transaction-type' in item and 'code' in item['transaction-type']:
                app = item['transaction-type']['code']
            t_type.append(app)
        if first_currency == "":
            first_currency = currency

    return value, rate, first_currency, t_type


def convert_currencies_from_dict(data, field, currencies, default_currency, value, rate, t_type):
    c_value, c_rate, first_currency = convert(data[field], currencies,
                                              default_currency=default_currency)
    value.append(c_value)
    rate.append(c_rate)
    if field == 'transaction':
        app = 0  # Transaction type/code are 1..1 in the standard, therefore app should always be non-zero.
        if 'transaction-type' in data[field] and 'code' in data[field]['transaction-type']:
            app = data['transaction']['transaction-type']['code']
        t_type.append(app)
    return value, rate, first_currency, t_type


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
    if 'value' not in data:
        return None, None, None

    currency = None
    if 'value.currency' in data:
        currency = data['value.currency']

    if not currency and default_currency:
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
    if 'value.value-date' not in data:
        return None, None
    date = data['value.value-date']
    if date is None or date == '':
        return None, None
    if '-' in date[:4] or '-' in date[5:7]:  # Exclude malformed dates
        return None, None
    year = int(date[:4])
    month = int(date[5:7])

    # If the month is in the future, pick current year/month
    now = datetime.datetime.now()
    if year > now.year:
        year = now.year

    if year == now.year and month > now.month:
        month = now.month

    return year, month


def save_converted_value_to_data(data, value, field, rate, first_currency, t_type):
    if len(value) > 0:
        summed_value = sum([0 if v is None else v for v in value])
        data[f'{field}.value-usd'] = value
        data[f'{field}.value-usd.sum'] = summed_value
        data[f'{field}.value-usd.conversion-rate'] = rate
        data[f'{field}.value-usd.conversion-currency'] = first_currency
        if field == 'transaction':
            data[f'{field}.value-usd-type'] = t_type
    return data
