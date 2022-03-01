CODELIST_POSTFIX = '.name'


def add_codelist_fields(data, codelists):
    """
    Can be single or multivalued.
    Add codelist fields as described above.

    :param data: reference to the activity in the data
    :param codelists: an initialized codelist object.
    :return: the updated dataset.
    """
    # reporting-org.type.name
    data = extract_single_field(data, 'reporting-org', 'type', 'OrganisationType', codelists)

    # recipient-country.name
    data = extract_list_field(data, 'recipient-country', 'code', 'Country', codelists)

    # recipient-region.name
    data = extract_list_field(data, 'recipient-region', 'code', 'Region', codelists)

    # default-aid-type.name
    data = extract_list_field(data, 'default-aid-type', 'code', 'AidType', codelists)

    # transaction.receiver-org.type.name
    data = extract_nested_list_field(data, 'transaction', 'receiver-org', 'type', 'OrganisationType', codelists)
    return data


def extract_single_field(data, field_name, field_type, codelist_name, codelists):
    if field_name not in data:
        return data
    if field_type not in data[field_name]:
        return data

    data[f'{field_name}.{field_type}{CODELIST_POSTFIX}'] = codelists.get_value(
        codelist_name,
        str(data[field_name][field_type]),  # Convert numeric to string
    )
    return data


def extract_list_field(data, field_name, field_type, codelist_name, codelists):
    postfixed_field_name = f'{field_name}{CODELIST_POSTFIX}'
    data[postfixed_field_name] = []
    if field_name not in data:
        return data

    if type(data[field_name]) is list:
        for rc in data[field_name]:
            check_and_get(field_type, rc, data, postfixed_field_name, codelists, codelist_name)
    else:
        check_and_get(field_type, data[field_name], data, postfixed_field_name, codelists, codelist_name)

    return data


def extract_nested_list_field(data, parent_field_name, field_name, field_type, codelist_name, codelists):
    postfixed_field_name = f'{parent_field_name}.{field_name}.{field_type}{CODELIST_POSTFIX}'
    data[postfixed_field_name] = []
    if parent_field_name not in data:
        return data
    if type(data[parent_field_name]) is list:
        for tr in data[parent_field_name]:
            if field_name in tr:
                check_and_get(field_type, tr[field_name], data, postfixed_field_name, codelists, codelist_name)
    else:
        if field_name in data[parent_field_name]:
            check_and_get(field_type, data[parent_field_name][field_name],
                          data, postfixed_field_name, codelists, codelist_name)

    return data


def check_and_get(field_type, codelist_field, data, postfixed_field_name, codelists, codelist_name):
    """
    Uses input information related to codelist item, to retrieve codelist value for relevant field
    """
    if field_type in codelist_field:
        data[postfixed_field_name].append(
            codelists.get_value(codelist_name, str(codelist_field[field_type]))
        )
