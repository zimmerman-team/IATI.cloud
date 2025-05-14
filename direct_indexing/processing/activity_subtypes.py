import logging
from copy import deepcopy

from django.conf import settings

from direct_indexing.custom_fields.indexing_manytomany_relations import index_many_to_many_relations

AVAILABLE_SUBTYPES = {
    'transaction': settings.SOLR_TRANSACTION_URL,
    'budget': settings.SOLR_BUDGET_URL,
    'result': settings.SOLR_RESULT_URL,
    'transaction_trimmed': settings.SOLR_TRANSACTION_TRIMMED_URL,
}

AVAILABLE_DRAFT_SUBTYPES = {
    'transaction': settings.SOLR_DRAFT_TRANSACTION_URL,
    'budget': settings.SOLR_DRAFT_BUDGET_URL,
    'result': settings.SOLR_DRAFT_RESULT_URL,
    'transaction_trimmed': settings.SOLR_DRAFT_TRANSACTION_TRIMMED_URL,
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
            f'{each_subtype}.value-usd-type',
            f'json.{each_subtype}'
        ]
    # Define the list of custom fields which relate to a specific subtype
    include_fields = [
        f'{subtype}.value-usd',
        f'{subtype}.value-usd-type',
        f'{subtype}.value-usd.conversion-rate',
        f'{subtype}.value-usd.conversion-currency',
        f'{subtype}.value-gbp',
        f'{subtype}.value-gbp-type',
        f'{subtype}.value-gbp.conversion-rate',
        f'{subtype}.value-gbp.conversion-currency',
        f'{subtype}.receiver-org.type.name',
        f'json.{subtype}'
    ]

    # get subtype
    subtype_in_data = activity[subtype]
    if isinstance(subtype_in_data, dict):
        subtype_in_data = [subtype_in_data]
    # traverse subtype list
    for i, subtype_element in enumerate(list(subtype_in_data)):
        if not isinstance(subtype_element, dict):
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
    if key not in activity:
        return subtype_dict
    if key in AVAILABLE_SUBTYPES:
        pass  # Drop the other subtypes, in case of transaction we drop result and budget.
    elif key in exclude_fields:
        pass  # drop the customized other fields
    elif key in include_fields:
        # extract the single value for the current index of the subtype from the multivalued content field
        try:
            if type(activity[key]) is list:
                if i <= len(activity[key]) and len(activity[key]) > 0:  # ensure we are not out of bounds
                    subtype_dict[key] = activity[key][i]
                else:
                    subtype_dict[key] = []
            else:
                subtype_dict[key] = activity[key]
        except Exception as e:
            logging.error(f"process_subtype_dict::error {e} key: {key} i: {i}, activity[key]: {activity[key]}")
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
    if type(data) is not list:
        data = [data]
    for activity in data:
        index_many_to_many_relations(activity)
        for key in subtypes:
            if key != 'transaction_trimmed':
                subtypes[key] += extract_subtype(activity, key)
    if len(subtypes['transaction']) != 0:
        subtypes['transaction_trimmed'] = _trim_transaction(deepcopy(subtypes['transaction']))
    return subtypes


def _trim_transaction(transaction):
    """
    Trim the transaction to only include the fields that are needed for the transaction_trimmed core.

    :param transaction: the transaction to trim
    :return: the trimmed transaction
    """
    trimmed_transaction = []
    for t in transaction:
        try:
            lud = t.get('last-updated-datetime', None)
            dc = t.get('default-currency', None)
            hier = t.get('hierarchy', None)
            iati_id = t.get('iati-identifier', None)
            transaction = _trim_transaction_obj(t.get('transaction', None))
            transaction_value_usd = t.get('transaction.value-usd', None)
            recipient_country = _trim_field(t.get('recipient-country', None), ['code'])
            reporting_org = _trim_field(t.get('reporting-org', None),
                                        ['ref', 'type', 'narrative', 'secondary-reporter', 'type.name'])
            activity_status = _trim_field(t.get('activity-status', None), ['code'])
            activity_date_start_planned = t.get('activity-date.start-planned', None)
            activity_date_start_actual = t.get('activity-date.start-actual', None)
            activity_date_end_planned = t.get('activity-date.end-planned', None)
            activity_date_end_actual = t.get('activity-date.end-actual', None)
            activity_date_common_start = t.get('activity-date.common.start', None)
            activity_date_common_end = t.get('activity-date.common.end', None)
            tag = _trim_field(t.get('tag', None), ['code', 'vocabulary'])
            activity_scope = t.get('activity-scope', None)
            document_link = _trim_field(t.get('document-link', None), ['category'])
            humanitarian_scope = _trim_field(t.get('humanitarian-scope', None), ['type', 'vocabulary'])
            other_identifier = _trim_field(t.get('other-identifier', None), ['type'])
            default_aid_type = t.get('default-aid-type', None)
            default_flow_type = t.get('default-flow-type', None)
            lang = t.get('lang', None)
            default_tied_status = t.get('default-tied-status', None)
            collaboration_type = t.get('collaboration-type', None)
            sector = _trim_field(t.get('sector', None), ['code', 'vocabulary', 'narrative'])
            policy_marker = _trim_field(t.get('policy-marker', None), ['code'])
            participating_org = _trim_field(t.get('participating-org', None), ['ref'])
            dataset_id = t.get('dataset.id', None)
            dataset_name = t.get('dataset.name', None)
            dataset_resources_hash = t.get('dataset.resources.hash', None)
            dataset_extras_iati_version = t.get('dataset.extras.iati_version', None)
            _trimmed = {
                'last-updated-datetime': lud,
                'default-currency': dc,
                'hierarchy': hier,
                'iati-identifier': iati_id,
                'transaction': transaction,
                'transaction.value-usd': transaction_value_usd,
                'recipient-country': recipient_country,
                'reporting-org': reporting_org,
                'activity-status': activity_status,
                'activity-date.start-planned': activity_date_start_planned,
                'activity-date.start-actual': activity_date_start_actual,
                'activity-date.end-planned': activity_date_end_planned,
                'activity-date.end-actual': activity_date_end_actual,
                'activity-date.common.start': activity_date_common_start,
                'activity-date.common.end': activity_date_common_end,
                'tag': tag,
                'activity-scope': activity_scope,
                'document-link': document_link,
                'humanitarian-scope': humanitarian_scope,
                'other-identifier': other_identifier,
                'default-aid-type': default_aid_type,
                'default-flow-type': default_flow_type,
                'lang': lang,
                'default-tied-status': default_tied_status,
                'collaboration-type': collaboration_type,
                'sector': sector,
                'policy-marker': policy_marker,
                'participating-org': participating_org,
                'dataset.id': dataset_id,
                'dataset.name': dataset_name,
                'dataset.resources.hash': dataset_resources_hash,
                'dataset.extras.iati_version': dataset_extras_iati_version,
            }
            # remove the empty fields from trimmed
            trimmed = {k: v for k, v in _trimmed.items() if v is not None}
            trimmed_transaction.append(trimmed)
            t['trimmed_transaction'] = True
        except Exception as e:
            logging.error(f"_trim_transaction::error: {e}")
            t['trimmed_transaction'] = False
    return trimmed_transaction


def _trim_transaction_obj(transaction):
    """
    Trim the transaction object to only include the fields that are needed for the transaction_trimmed core.

    :param transaction: the transaction to trim
    :return: the trimmed transaction
    """
    try:
        if transaction is None:
            return None
        _transaction = deepcopy(transaction)
        for key in transaction:
            if key in ['ref', 'disbursement-channel', 'recipient-region', 'finance-type', 'aid-type']:
                del _transaction[key]
                continue
            if key not in ['description', 'provider-org', 'receiver-org', 'sector', 'recipient-country']:
                continue
            to_keep = {
                "description": ['narrative'],
                "provider-org": ['narrative', 'ref'],
                "receiver-org": ['narrative', 'ref'],
                "sector": ['code', 'vocabulary'],
                "recipient-country": ['code'],
            }
            _transaction[key] = _trim_field(_transaction[key], to_keep[key])
        return _transaction
    except Exception as e:
        logging.error(f"_trim_transaction_obj::error {e}")
        raise e


def _trim_field(item, keep_list):
    try:
        # Skip empty items
        if item is None:
            return None
        # create a copy so we can change the length of the keys
        _item = deepcopy(item)
        # if list, recurse
        if isinstance(item, list):
            for i in range(len(item)):
                _item[i] = _trim_field(item[i], keep_list)
        else:
            # if not list, check if the key is in the keep list else remove
            for key in item:
                if key not in keep_list:
                    del _item[key]
        return _item
    except Exception as e:
        logging.error(f"_trim_field::error {e}")
        raise e
