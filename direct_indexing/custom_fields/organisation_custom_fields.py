def add_all(data):
    """
    Start organisation processing.

    :param data: the cleaned dataset.
    :param codelists: an initialized codelist object.
    :param currencies: an initialized currencies object.
    :return: the updated dataset.
    """
    if type(data) is not list:
        data = [data]

    for organisation in data:
        index_many_to_many_relations(organisation)

    return data


def index_many_to_many_relations(organisation):
    """
    Index many-to-many relations is used to support the use of relational data,
    Currently we use it for the result indicators, which have 0 to N periods and baselines.
    By providing an index for each indicator in for these children, a frontend can access these files as relational
    """
    # if 0, represent with index -1, else represent with index n.
    TE = 'total-expenditure'
    if TE in organisation:
        if type(organisation[TE]) != list:
            organisation[TE] = [organisation[TE]]
        index_total_expenditure(organisation, TE)


def index_total_expenditure(organisation, field):
    """
    Go through the activity participating orgs and index the given child.
    Because this is currently used for results, we directly pass the required children.

    :param field: a dataset containing the initial child of the activity
    :param child: the second level child of the aforementioned field
    """
    # Check if the child exists and make the child a list if it is a dict.
    # total-expenditure.value.currency
    """
    0..*    total-expenditure
    1..1        period-start
    1..1        period-end
    1..1        value
    0..1            currency
    1..1            value-date
    0..*        expense-line
    0..1            ref
    1..1            value
    0..1                currency
    1..1                value-date
    1..*            narrative
    0..*                lang

    we need:
    value
    period-start
    expense-line.ref
    expense-line.value

    value and period start are 1..1, thus we skip

    we need to know: for every total expenditure (we can also see this as for every value,
    as value is 1..1 on total-expenditure),
        how many expense lines are there
        for every expense line, how many children value and ref are there

    -1 indicates there is no ref
    """
    EL_STR = 'expense-line'
    organisation['total-expenditure.expense-line-index'] = []
    organisation['total-expenditure.expense-line.ref-index'] = []
    organisation['total-expenditure.expense-line.val-index'] = []
    for total_expenditure in organisation[field]:
        # count the number of total-expenditures for the total-expenditure
        te_count = 0
        if EL_STR in total_expenditure:
            if type(total_expenditure[EL_STR]) is not list:
                total_expenditure[EL_STR] = [total_expenditure[EL_STR]]
            te_count = len(total_expenditure[EL_STR])

            # if there is at least one expense line, we need to index the expense lines
            for i, expense_line in enumerate(total_expenditure[EL_STR]):
                # there is always 1 value for every expense-line.
                # if there is no ref, indicate with a -1, else indicate with the number.
                ref_val = -1
                if 'ref' in expense_line:
                    ref_val = i

                organisation['total-expenditure.expense-line.ref-index'].append(ref_val)
                organisation['total-expenditure.expense-line.val-index'].append(i)

        organisation['total-expenditure.expense-line-index'].append(te_count)
