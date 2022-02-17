from collections import OrderedDict


def recursive_attribute_cleaning(data):
    """
    Recursively clean the attributes of the dataset.

    :param data: either a dict, list of ordered dicts or an ordered dict.
    :return: the cleaned dataset.
    """
    if type(data) in [OrderedDict, dict]:
        # Filter out any @ symbols in the keys. (@attribute to attribute)
        data = {key.replace('@', ''): item for key, item in data.items()}
        # Remove the lang xml tag
        data = {key.replace('{http://www.w3.org/XML/1998/namespace}lang', 'lang'): item for key, item in data.items()}
        # A list of fields that need to be appended to the dataset
        add_fields = {}
        for key, value in data.items():
            # These fields always contain a single value, but can be in a list
            if key in [
                'iati-identifier', 'telephone', 'email', 'website', 'pos', 'channel-code', 'organisation-identifier'
            ]:
                extract_literal_values(value, key, data)
            elif key in ['value', 'forecast', 'narrative']:
                # A value is always single value,
                # but narrative and forecast can be multiple values.
                if type(value) == list:
                    add_fields = extract_list_values(add_fields, value, key, data)

                else:  # if there is only a single entry
                    add_fields = extract_single_values(add_fields, value, key, data)
            # If the fields are not yet at the lowest level of key-value pair,
            # process the underlying field.
            elif type(value) in [OrderedDict, list]:
                data[key] = recursive_attribute_cleaning(value)
        # Add the fields to be appended to the dataset
        for key in add_fields:
            data[key] = add_fields[key]
    # If a dataset is a list, it will contain multiple dicts, so loop over and
    # process the individual dicts.
    elif type(data) == list:
        for i in range(len(data)):
            data[i] = recursive_attribute_cleaning(data[i])

    return data


def extract_literal_values(value, key, data):
    """
    Supplied is a key:value pair, as well as the overarching data.
    Data is a reference, so that the value can be updated.

    Take the value out of var-name.$ = 42 and save it as var-name = 42.

    :param value: the value of the key:value pair.
    :param key: the key of the key:value pair.
    :param data: the overarching data.
    :return: None, as data is a reference
    """
    if type(value) == list:
        # initialize array and add each element to the array
        data[key] = []
        for element in value:
            if '$' in element.keys():
                data[key].append(element['$'])
    else:
        # Retrieve the single value if the field is not a list
        if '$' in value.keys():
            data[key] = value['$']


def extract_list_values(add_fields, value, key, data):
    """
    Extract all of the list items to the additional fields
    Data is a reference and thus the value can be updated.

    Take the values out of, for example:
        var-name.narrative.$ = ["This is a narrative", "This is another narrative"]
        var-name.narrative.@lang = ["en", "fr"]
    and save it as:
        var-name.narrative = ["This is a narrative", "This is another narrative"]
        var-name.narrative.lang = ["en", "fr"]

    :param add_fields: the additional fields to be appended to the dataset.
    :param value: the value of the key:value pair.
    :param key: the key of the key:value pair.
    :param data: the overarching data.
    :return: the additional fields to be appended to the dataset.
    """
    # initialize array and add each element to the array
    data[key] = []  # the actual value.
    for item in ['currency', 'value_date', 'year', 'lang']:
        add_fields[f'{key}.{item}'] = []
    for element in value:
        if len(element) == 0:  # Skip empty elements.
            continue
        if '$' in element.keys():
            data[key].append(element['$'])
        else:
            data[key].append(' ')
        if '@currency' in element.keys():
            add_fields['%s.currency' % element].append(element['@currency'])
        if '@value-date' in element.keys():
            add_fields['%s.value-date' % element].append(element['@value-date'])
        if '@year' in element.keys():
            add_fields['%s.year' % key].append(element['@year'])
        if '@{http://www.w3.org/XML/1998/namespace}lang' in element.keys():
            add_fields['%s.lang' % key].append(
                element['@{http://www.w3.org/XML/1998/namespace}lang'])
        else:  # Avoid having an inconsistent length between narrative lang and value
            if key is not 'value':
                add_fields['%s.lang' % key].append(' ')

    return add_fields


def extract_single_values(add_fields, value, key, data):
    """
    Extract single values to the additional fields.
    Data is a reference and thus the value can be updated.

    Take the values out of, for example:
        var-name.value.value-date.$ = "This is a narrative"
        var-name.narrative.@lang = "en"
    and save it as:
        var-name.narrative = "This is a narrative"
        var-name.narrative.lang = "en"

    :param add_fields: the additional fields to be appended to the dataset.
    :param value: the value of the key:value pair.
    :param key: the key of the key:value pair.
    :param data: the overarching data.
    :return: the additional fields to be appended to the dataset.
    """
    if type(value) == list and len(value) == 0:
        # Skip empty elements.
        pass
    if type(value) in [int, str, float]:  # if the value is directly available
        data[key] = value
        pass
    if '$' in value.keys():
        data[key] = value['$']
    else:
        data[key] = ' '
    if '@currency' in value.keys():
        add_fields['%s.currency' % key] = value['@currency']
    if '@value-date' in value.keys():
        add_fields['%s.value-date' % key] = value['@value-date']
    if '@year' in value.keys():
        add_fields['%s.year' % key] = value['@year']
    # The language can still be a child element which has not
    # yet been converted within recursion.
    if '@{http://www.w3.org/XML/1998/namespace}lang' in value.keys():
        add_fields['%s.lang' % key] = value[
            '@{http://www.w3.org/XML/1998/namespace}lang']
    else:
        if key is not 'value':
            add_fields['%s.lang' % key] = ' '

    return add_fields
