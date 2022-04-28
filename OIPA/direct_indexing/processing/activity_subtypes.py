from django.conf import settings

from direct_indexing.custom_fields.indexing_manytomany_relations import index_many_to_many_relations

AVAILABLE_SUBTYPES = {
    'transaction': settings.SOLR_TRANSACTION_URL,
    'budget': settings.SOLR_BUDGET_URL,
    'result': settings.SOLR_RESULT_URL
}


def extract_subtype(activity, subtype):
    """
    We extract the specified field and index that field.

    Decision:
        Drop all fields that are not transaction, budget or result for every list element.
        Do this because we have separate cores that deepen out these fields.

    :param activity: the parent activity
    :param subtype: the subtype to extract
    :return: the extracted subtype as a list
    """
    if subtype not in AVAILABLE_SUBTYPES or subtype not in activity:
        return []  # Make sure we do not return any data when there is none.

    # Add custom fields to result core
    activity = index_many_to_many_relations(activity)

    # Create a list of the extracted subtypes
    subtype_list = []
    exclude_fields = []
    for each_subtype in AVAILABLE_SUBTYPES:
        if each_subtype == subtype:
            continue
        # Create a list of custom added fields to remove from the eventual dataset
        exclude_fields += [
            f'{each_subtype}.value-usd',
            f'{each_subtype}.value-usd.sum',
            f'{each_subtype}.value-usd.conversion-rate',
            f'{each_subtype}.value-usd.conversion-currency',
            f'{each_subtype}.value-usd-type'
        ]
    # Define the list of custom fields which relate to a specific subtype
    include_fields = [
        f'{subtype}.value-usd',
        f'{subtype}.value-usd.conversion-rate',
        f'{subtype}.value-usd.conversion-currency'
    ]

    # get subtype
    subtype_in_data = activity[subtype]
    if type(subtype_in_data) is dict:
        subtype_in_data = [subtype_in_data]
    # traverse subtype list
    for i, subtype_element in enumerate(list(subtype_in_data)):
        if not type(subtype_element) == dict:
            continue  # skip if the element is broken
        # Get the value of the subtype element into a new dict with the key being the subtype.
        subtype_dict = {subtype: dict(subtype_element)}
        for key in activity:
            subtype_dict = process_subtype_dict(subtype_dict, key, i, activity, exclude_fields, include_fields)
        subtype_list.append(subtype_dict)

    return subtype_list


def process_subtype_dict(subtype_dict, key, i, activity, exclude_fields, include_fields):
    """
    Process the subtype dict.

    :param subtype_dict: the subtype dict
    :param key: the key of the field to look for
    :param i: the index of the current subtype list
    :param activity: the parent activity
    :param exclude_fields: the fields to exclude
    :param include_fields: the fields to include
    """
    if key in AVAILABLE_SUBTYPES:
        pass  # Drop the other subtypes, in case of transaction we drop result and budget.
    elif key in exclude_fields:
        pass  # drop the customized other fields
    elif key in include_fields:
        # extract the single value for the current index of the subtype from the multivalued content field
        if type(activity[key]) is list:
            if i <= len(activity[key]):  # ensure we are not out of bounds
                subtype_dict[key] = activity[key][i]
        else:
            subtype_dict[key] = activity[key]
    else:
        subtype_dict[key] = activity[key]  # keep additional activity fields for querying and filtering

    return subtype_dict


def extract_all_subtypes(subtypes, data):
    """
    Extract all subtypes from the data.

    :param subtypes: the subtypes to extract
    :param data: the activities to extract the subtypes from.
    :return: the extracted subtypes
    """
    if type(data) is list:
        for activity in data:
            for key in subtypes:
                subtypes[key] += extract_subtype(activity, key)
    else:
        for key in subtypes:
            subtypes[key] += extract_subtype(data, key)

    return subtypes
