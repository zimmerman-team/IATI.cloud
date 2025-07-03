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
    data = extract_single_field(
        data, 'reporting-org', 'type', 'OrganisationType', codelists
    )

    # recipient-country.name
    data = extract_list_field(data, 'recipient-country', 'code', 'Country', codelists)

    # recipient-region.name
    data = extract_list_field(data, 'recipient-region', 'code', 'Region', codelists)

    # default-aid-type.name
    data = extract_list_field(data, 'default-aid-type', 'code', 'AidType', codelists)

    # policy-marker.name
    data = extract_list_field(data, 'policy-marker', 'code', 'PolicyMarker', codelists)

    # policy-marker.significance.name
    data = extract_list_field(
        data,
        'policy-marker',
        'significance',
        'PolicySignificance',
        codelists,
        'policy-marker.significance',
    )
    # policy-marker.vocabulary.name
    data = extract_list_field(
        data,
        'policy-marker',
        'vocabulary',
        'PolicyMarkerVocabulary',
        codelists,
        'policy-marker.vocabulary',
    )

    # budget.type.name and budget.status.name
    data = extract_list_field(
        data, 'budget', 'type', 'BudgetType', codelists, 'budget.type'
    )
    data = extract_list_field(
        data, 'budget', 'status', 'BudgetStatus', codelists, 'budget.status'
    )

    # sector.name
    data = extract_list_field(data, 'sector', 'code', 'SectorCategory', codelists)

    # tag.vocabulary.name
    data = extract_list_field(
        data, 'tag', 'vocabulary', 'TagVocabulary', codelists, 'tag.vocabulary'
    )

    # transaction.receiver-org.type.name
    data = extract_nested_list_field(
        data, 'transaction', 'receiver-org', 'type', 'OrganisationType', codelists
    )
    return data


def extract_single_field(data, field_name, field_type, codelist_name, codelists):
    """
    Extract a single field's codelist value and add it to the data.

    :param data: the data dictionary
    :param field_name: name of the field containing the code
    :param field_type: the attribute in the field that contains the code value
    :param codelist_name: name of the codelist to lookup
    :param codelists: codelist object with get_value() method
    :return: updated data dictionary
    """
    if field_name not in data:
        return data
    if field_type not in data[field_name]:
        return data

    data[f'{field_name}.{field_type}{CODELIST_POSTFIX}'] = codelists.get_value(
        codelist_name,
        str(data[field_name][field_type]),  # Convert numeric to string
    )
    return data


def extract_list_field(
    data, field_name, field_type, codelist_name, codelists, custom_field_name=None
):
    """
    Extract codelist values from a list field and add them to the data.

    :param data: the data dictionary
    :param field_name: name of the field containing codes
    :param field_type: the attribute in each list item that contains the code value
    :param codelist_name: name of the codelist to lookup
    :param codelists: codelist object with get_value() method
    :param custom_field_name: optional custom field name for the result
    :return: updated data dictionary
    """
    if custom_field_name:
        postfixed_field_name = f'{custom_field_name}{CODELIST_POSTFIX}'
    else:
        postfixed_field_name = f'{field_name}{CODELIST_POSTFIX}'
    data[postfixed_field_name] = []
    if field_name not in data:
        return data

    if isinstance(data[field_name], list):
        for rc in data[field_name]:
            check_and_get(
                field_type, rc, data, postfixed_field_name, codelists, codelist_name
            )
    else:
        check_and_get(
            field_type,
            data[field_name],
            data,
            postfixed_field_name,
            codelists,
            codelist_name,
        )

    return data


def extract_nested_list_field(
    data, parent_field_name, field_name, field_type, codelist_name, codelists
):
    """
    Extract codelist values from a nested list field and add them to the data.

    :param data: the data dictionary
    :param parent_field_name: name of the parent field (e.g., 'transaction')
    :param field_name: name of the nested field (e.g., 'receiver-org')
    :param field_type: the attribute in the nested field that contains the code value
    :param codelist_name: name of the codelist to lookup
    :param codelists: codelist object with get_value() method
    :return: updated data dictionary
    """
    postfixed_field_name = (
        f'{parent_field_name}.{field_name}.{field_type}{CODELIST_POSTFIX}'
    )
    data[postfixed_field_name] = []
    if parent_field_name not in data:
        return data
    if isinstance(data[parent_field_name], list):
        for tr in data[parent_field_name]:
            if field_name in tr:
                check_and_get(
                    field_type,
                    tr[field_name],
                    data,
                    postfixed_field_name,
                    codelists,
                    codelist_name,
                )
    else:
        if field_name in data[parent_field_name]:
            check_and_get(
                field_type,
                data[parent_field_name][field_name],
                data,
                postfixed_field_name,
                codelists,
                codelist_name,
            )

    return data


def check_and_get(
    field_type, codelist_field, data, postfixed_field_name, codelists, codelist_name
):
    """
    Uses input information related to codelist item, to retrieve codelist value for relevant field

    :param field_type: the attribute containing the code value
    :param codelist_field: the field containing the codelist code
    :param data: the data dictionary to update
    :param postfixed_field_name: the field name to store the result in
    :param codelists: codelist object with get_value() method
    :param codelist_name: name of the codelist to lookup
    """
    if field_type in codelist_field:
        data[postfixed_field_name].append(
            codelists.get_value(codelist_name, str(codelist_field[field_type]))
        )
