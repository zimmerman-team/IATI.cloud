def add_codelist_fields(data, codelists):
    """
    Can be single or multivalued.
    Add codelist fields as described above.

    :param data: reference to the activity in the data
    :param codelists: an initialized codelist object.
    :return: the updated dataset.
    """

    # reporting-org.type.name
    if 'reporting-org' in data.keys():
        data['reporting-org.type.name'] = codelists.get_value(
            'OrganisationType',
            str(data['reporting-org']['type']),  # Convert numeric to string
        )

    # recipient-country.name
    data['recipient-country.name'] = []
    if 'recipient-country' in data.keys():
        if type(data['recipient-country']) == list:
            for rc in data['recipient-country']:
                data['recipient-country.name'].append(
                    codelists.get_value('Country', str(rc['code']))
                )
        else:
            data['recipient-country.name'].append(
                codelists.get_value('Country',
                                    str(data['recipient-country']['code']))
            )

    # recipient-region.name
    data['recipient-region.name'] = []
    if 'recipient-region' in data.keys():
        if type(data['recipient-region']) == list:
            for rr in data['recipient-region']:
                data['recipient-region.name'].append(
                    codelists.get_value('Region', rr['code'])
                )
        else:
            data['recipient-region.name'].append(
                codelists.get_value('Region',
                                    str(data['recipient-region']['code']))
            )

    # default-aid-type.name
    data['default-aid-type.name'] = []
    if 'default-aid-type' in data.keys():
        if type(data['default-aid-type']) == list:
            for dt in data['default-aid-type']:
                data['default-aid-type.name'].append(
                    codelists.get_value('AidType', dt['code'])
                )
        else:
            data['default-aid-type.name'].append(
                codelists.get_value('AidType',
                                    str(data['default-aid-type']['code']))
            )

    # transaction-receiver-org.type.name
    data['transaction.receiver-org.type.name'] = []
    if 'transaction' in data.keys():
        if type(data['transaction']) == list:
            for tr in data['transaction']:
                if 'receiver-org' in tr.keys():
                    data['transaction.receiver-org.type.name'].append(
                        codelists.get_value('OrganisationType', tr['receiver-org']['type'])  # NOQA
                    )
        else:
            if 'receiver-org' in data['transaction'].keys():
                data['transaction.receiver-org.type.name'].append(
                    codelists.get_value('OrganisationType',
                                        str(data['transaction']['receiver-org']['type']))  # NOQA
                )

    return data
