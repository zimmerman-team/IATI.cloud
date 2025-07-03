import datetime


def currency_conversion(data, currencies):
    """
    For the following fields the currency converted value is expected:
    budget_value_usd, planned_disbursement_value_usd and transaction_value_usd.
    Along with the conversion rate. Lastly, we provide the sum of each activity.

    :param data: reference to the activity in the data
    :param currencies: an initialized currencies object.
    """
    default_currency = data.get('default-currency')

    # Fields to process for currency conversion
    fields = ['budget', 'planned-disbursement', 'transaction']
    target_currencies = ['USD', 'GBP']

    for field in fields:
        if field not in data:
            continue

        for target_currency in target_currencies:
            process_currency_conversion(
                data, field, currencies, default_currency, target_currency
            )

    return data


def process_currency_conversion(
    data, field, currencies, default_currency, target_currency
):
    """
    Process currency conversion for a specific field and target currency.

    :param data: reference to the activity data dictionary
    :param field: the field to process ('budget', 'planned-disbursement', or 'transaction')
    :param currencies: an initialized currencies object
    :param default_currency: the default currency to use if no currency is specified
    :param target_currency: the target currency to convert to ('USD' or 'GBP')
    """
    if field not in data:
        return

    # Results to collect
    values = []
    rates = []
    transaction_types = []
    first_currency = ""

    # Process field based on its type
    if isinstance(data[field], list):
        for item in data[field]:
            process_item(
                item,
                currencies,
                default_currency,
                target_currency,
                field,
                values,
                rates,
                transaction_types,
                first_currency,
            )
    else:
        process_item(
            data[field],
            currencies,
            default_currency,
            target_currency,
            field,
            values,
            rates,
            transaction_types,
            first_currency,
        )

    # Save results back to data structure
    if values:
        target_key = target_currency.lower()
        summed_value = sum(v for v in values if v is not None)

        data[f'{field}.value-{target_key}'] = values
        data[f'{field}.value-{target_key}.sum'] = summed_value
        data[f'{field}.value-{target_key}.conversion-rate'] = rates
        data[f'{field}.value-{target_key}.conversion-currency'] = first_currency

        if field == 'transaction' and transaction_types:
            data[f'{field}.value-{target_key}-type'] = transaction_types


def process_item(
    item,
    currencies,
    default_currency,
    target_currency,
    field,
    values,
    rates,
    transaction_types,
    first_currency,
):
    """
    Process a single item for currency conversion.

    :param item: the item to process
    :param currencies: an initialized currencies object
    :param default_currency: the default currency to use if no currency is specified
    :param target_currency: the target currency to convert to
    :param field: the field being processed
    :param values: list to collect converted values
    :param rates: list to collect conversion rates
    :param transaction_types: list to collect transaction types (for transaction field)
    :param first_currency: variable to store the first currency encountered
    """
    value, rate, currency = convert(item, currencies, default_currency, target_currency)

    if value is not None:
        values.append(value)
        rates.append(rate)

        # Store the first currency we encounter
        if not first_currency and currency:
            first_currency = currency

        # Process transaction type if this is a transaction
        if field == 'transaction':
            transaction_type = 0
            if 'transaction-type' in item and 'code' in item['transaction-type']:
                transaction_type = item['transaction-type']['code']
            transaction_types.append(transaction_type)


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

    currency = data.get('value.currency', default_currency)

    if not currency:
        return None, None, None

    year, month = get_ym(data)
    if not year or not month:
        return None, None, None

    converted_value, rate = currencies.convert_currency(
        currency, target_currency, data['value'], month, year
    )
    return converted_value, rate, currency


def get_ym(data):
    """
    value-dates are reported as XSD:Date which is always yyyy-mm-dd.

    :param data: reference to the value in the data
    :return: year and month or None if not found
    """
    date_str = data.get('value.value-date')
    if not date_str:
        return None, None

    try:
        if '-' in date_str[:4] or '-' in date_str[5:7]:  # Exclude malformed dates
            return None, None
        # Extract year and month from date string
        year = int(date_str[:4])
        month = int(date_str[5:7])

        # Ensure date is not in the future
        now = datetime.datetime.now()
        if year > now.year:
            year = now.year
            month = now.month
        elif year == now.year and month > now.month:
            month = now.month

        return year, month
    except (ValueError, IndexError):
        # Handle malformed dates
        return None, None
