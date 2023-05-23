IATI_DATE_FIELDS = [
    'activity-date',
    'budget.period-start',
    'budget.period-end',
    'planned-disbursement.period-start',
    'planned-disbursement.period-end',
    'transaction.transaction-date',
    'document-link.document-date',
    'result.document-link.document-date',
    'result.indicator.document-link.document-date',
    'result.indicator.baseline',
    'result.indicator.baseline.document-link.document-date',
    'result.indicator.period.period-start',
    'result.indicator.period.period-end',
    'result.indicator.period.target.document-link.document-date',
    'result.indicator.period.actual.document-link.document-date',
    'crs-add.loan-terms.commitment-date',
    'crs-add.loan-terms.repayment-first-date',
    'crs-add.loan-terms.repayment-final-date',
]


def add_date_quarter_fields(data):
    """
    Requested by FCDO. Multi valued fields.
    For:
        activity-date.iso-date
        budget.period-start.iso-date
        budget.period-end.iso-date
        planned-disbursement.period-start.iso-date
        planned-disbursement.period-end.iso-date
        transaction.transaction-date.iso-date
        document-link.document-date.iso-date
        result.document-link.document-date.iso-date
        result.indicator.document-link.document-date.iso-date
        result.indicator.baseline.iso-date
        result.indicator.baseline.document-link.document-date.iso-date
        result.indicator.period.period-start.iso-date
        result.indicator.period.period-end.iso-date
        result.indicator.period.target.document-link.document-date.iso-date
        result.indicator.period.actual.document-link.document-date.iso-date
        crs-add.loan-terms.commitment-date.iso-date
        crs-add.loan-terms.repayment-first-date.iso-date
        crs-add.loan-terms.repayment-final-date.iso-date

    We add a .quarter value as well.
    These will all be multi-valued fields.
    The field will contain the quarter of the year to which the iso-date belongs.

    :param data: reference to the activity in the data
    """
    # For each base field, like budget, transaction, result etc.
    for date_field in IATI_DATE_FIELDS:
        children = date_field.split('.')  # list of all the child elements of the activity leading to the date field.
        quarters = []
        if children[0] in data:
            quarters = recursive_date_fields(data, children[0], children[1:])
            data[date_field + '.quarter'] = quarters
    return data


def recursive_date_fields(data_obj, head, tail):
    """
    This function recursively gets the quarter values for each given child.

    :param data_obj:    data object containing the reference to the object to be checked.
    :param head:        the first child in the list of children in a field that should have quarter data.
    :param tail:        all the remaining children in the list of children in a field that should have quarter data.
    """
    # Ensure the data object is a list
    if head not in data_obj:
        return []
    if type(data_obj[head]) is dict:
        data_obj[head] = [data_obj[head]]

    # initialize the list of quarters
    q = []
    for item in data_obj[head]:
        # If we are at the final child, check if there is an iso-date attribute.
        if len(tail) == 0:
            if 'iso-date' not in item:
                continue
            # if there is an iso-date attribute, get the quarter value and add it to the list.
            q_val = retrieve_date_quarter(item['iso-date'])
            if q_val:
                q.append(q_val)  # iso-date is always the attribute name
        else:
            # if we are not at the final child, recursively continue through the children
            # and combine the resulting lists into the final list of quarters for the field
            q += recursive_date_fields(item, tail[0], tail[1:])
    return q


def retrieve_date_quarter(date):
    """
    The date object will always be a string object in the shape of an ISO date object,
    meaning YYYY-MM-DD
    """
    if isinstance(date, str):
        return ((int(date[5:7]) - 1) // 3) + 1
    if hasattr(date, "strftime") and hasattr(date, "month"):
        return ((date.month - 1) // 3) + 1
    return None
