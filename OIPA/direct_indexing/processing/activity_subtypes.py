import logging

from django.conf import settings

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
    if subtype not in AVAILABLE_SUBTYPES.keys() or subtype not in activity.keys():
        return []  # Make sure we do not return any data when there is none.
    # Create a list of the extracted subtypes
    subtype_list = []
    try:
        # get subtype
        subtype_in_data = activity[subtype]
        if type(subtype_in_data) is dict:
            subtype_in_data = [subtype_in_data]
        # traverse subtype list
        for subtype_element in list(subtype_in_data):
            if not type(subtype_element) == dict:
                continue
            # Get the value of the subtype element into a new dict with the key being the subtype.
            subtype_dict = {subtype: dict(subtype_element)}
            for key in activity.keys():
                if key in AVAILABLE_SUBTYPES.keys():
                    continue
                subtype_dict[key] = activity[key]
            subtype_list.append(subtype_dict)
    except Exception as e:
        print(f'Exception in processing subtype {subtype}')
        print(e)

    return subtype_list


def extract_all_subtypes(subtypes, data):
    """
    Extract all subtypes from the data.

    :param subtypes: the subtypes to extract
    :param data: the activities to extract the subtypes from.
    :return: the extracted subtypes
    """
    try:
        if type(data) is list:
            for activity in data:
                for key in subtypes.keys():
                    subtypes[key] += extract_subtype(activity, key)
        else:
            for key in subtypes.keys():
                subtypes[key] += extract_subtype(data, key)

        return subtypes
    except Exception as e:
        logging.warning('Exception in extracting the subtypes')
        logging.warning(e)

    return subtypes
