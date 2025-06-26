import datetime
import logging
import re
from copy import deepcopy

from django.conf import settings

from direct_indexing.custom_fields.indexing_manytomany_relations import index_many_to_many_relations
from direct_indexing.processing.subtypes_util import COUNTRIES, REGIONS, set_default_percentage

AVAILABLE_SUBTYPES = {
    'transaction': settings.SOLR_TRANSACTION_URL,
    'budget': settings.SOLR_BUDGET_URL,
    'result': settings.SOLR_RESULT_URL,
    'transaction_trimmed': settings.SOLR_TRANSACTION_TRIMMED_URL,
    'transaction_sdgs': settings.SOLR_TRANSACTION_SDGS_URL,
    'budget_split_by_sector': settings.SOLR_BUDGET_SPLIT_BY_SECTOR_URL,
}

AVAILABLE_DRAFT_SUBTYPES = {
    'transaction': settings.SOLR_DRAFT_TRANSACTION_URL,
    'budget': settings.SOLR_DRAFT_BUDGET_URL,
    'result': settings.SOLR_DRAFT_RESULT_URL,
    'transaction_trimmed': settings.SOLR_DRAFT_TRANSACTION_TRIMMED_URL,
    'transaction_sdgs': settings.SOLR_DRAFT_TRANSACTION_SDGS_URL,
    'budget_split_by_sector': settings.SOLR_DRAFT_BUDGET_SPLIT_BY_SECTOR_URL,
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
            f'{each_subtype}.type.name',
            f'{each_subtype}.status.name',
            f'{each_subtype}.receiver-org.type.name',
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
                if i <= len(activity[key])-1 and len(activity[key]) > 0:  # ensure we are not out of bounds
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
        subtypes['transaction_trimmed'] = _trim_transactions(deepcopy(subtypes['transaction']))
    if len(subtypes['transaction_trimmed']) != 0:
        subtypes['transaction_sdgs'] = _split_transactions(deepcopy(subtypes['transaction_trimmed']))
    if len(subtypes['budget']) != 0:
        subtypes['budget_split_by_sector'] = _trim_split_budgets(deepcopy(subtypes['budget']))
    return subtypes


def _trim_transactions(transactions):
    """
    Trim the transaction to only include the fields that are needed for the transaction_trimmed core.

    :param transaction: the transaction to trim
    :return: the trimmed transaction
    """
    trimmed_transactions = []
    for t in transactions:
        try:
            lud = t.get('last-updated-datetime', None)
            dc = t.get('default-currency', None)
            hier = t.get('hierarchy', None)
            iati_id = t.get('iati-identifier', None)
            transaction = _trim_transaction_obj(t.get('transaction', None))
            transaction_value_usd = t.get('transaction.value-usd', None)
            recipient_country = _trim_field(t.get('recipient-country', None), ['code'])
            reporting_org = _trim_field(t.get('reporting-org', None),
                                        ['ref', 'type', 'narrative', 'secondary-reporter'])
            reporting_org_type_name = t.get('reporting-org.type.name', None)
            activity_status = _trim_field(t.get('activity-status', None), ['code'])
            activity_date_start_planned = t.get('activity-date.start-planned', None)
            activity_date_start_actual = t.get('activity-date.start-actual', None)
            activity_date_end_planned = t.get('activity-date.end-planned', None)
            activity_date_end_actual = t.get('activity-date.end-actual', None)
            activity_date_common_start = t.get('activity-date.common.start', None)
            activity_date_common_end = t.get('activity-date.common.end', None)
            tag = _trim_field(t.get('tag', None), ['code', 'vocabulary', 'narrative'])
            activity_scope = t.get('activity-scope', None)
            document_link = _trim_field(t.get('document-link', None), ['category'])
            humanitarian_scope = _trim_field(t.get('humanitarian-scope', None), ['type', 'vocabulary'])
            other_identifier = _trim_field(t.get('other-identifier', None), ['type'])
            default_aid_type = t.get('default-aid-type', None)
            default_flow_type = t.get('default-flow-type', None)
            lang = t.get('lang', None)
            default_tied_status = t.get('default-tied-status', None)
            collaboration_type = t.get('collaboration-type', None)
            sector = _trim_field(t.get('sector', None), ['code', 'percentage', 'vocabulary', 'narrative'])
            policy_marker = _trim_field(t.get('policy-marker', None), ['code'])
            policy_marker_combined = t.get('policy-marker.combined', None)
            participating_org = _trim_field(t.get('participating-org', None), ['ref', 'narrative'])
            title = _trim_field(t.get('title', None), ['narrative'])
            recipient_country_name = t.get('recipient-country.name', None)
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
                'reporting-org.type.name': reporting_org_type_name,
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
                'policy-marker.combined': policy_marker_combined,
                'participating-org': participating_org,
                'title': title,
                'recipient-country.name': recipient_country_name,
                'dataset.id': dataset_id,
                'dataset.name': dataset_name,
                'dataset.resources.hash': dataset_resources_hash,
                'dataset.extras.iati_version': dataset_extras_iati_version,
            }
            # remove the empty fields from trimmed
            trimmed = {k: v for k, v in _trimmed.items() if v is not None}
            trimmed_transactions.append(trimmed)
        except Exception as e:
            logging.error(f"_trim_transaction::error: {e}")
    return trimmed_transactions


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
            if key in ['ref', 'disbursement-channel', 'finance-type', 'aid-type']:
                del _transaction[key]
                continue
            if key not in ['description', 'provider-org', 'receiver-org',
                           'sector', 'recipient-country', 'recipient-region']:
                continue
            to_keep = {
                "description": ['narrative'],
                "provider-org": ['narrative', 'ref'],
                "receiver-org": ['narrative', 'ref'],
                "sector": ['code', 'vocabulary', 'percentage'],
                "recipient-country": ['code', 'percentage'],
                "recipient-region": ['code', 'percentage']
            }
            _transaction[key] = _trim_field(_transaction[key], to_keep[key])
        return _transaction
    except Exception as e:
        logging.error(f"_trim_transaction_obj::error {e}")
        raise e


def _trim_split_budgets(budgets):
    """Parent function for trimming and splitting budgets that are SDGs.

    Args:
        budgets (list | None): a list of the budgets to be trimmed and split

    Returns:
        list: list of budgets split by SDG, if they are not related to SDGs they are not included.
    """
    trimmed_budgets = _trim_budgets(budgets)
    split_budgets = _split_budgets(trimmed_budgets)
    return split_budgets


def _trim_budgets(budgets):
    """Trim the budget to only include the fields that are needed for the budget split by sector core.

    Args:
        budgets (list): list of complete budgets

    Returns:
        list: list of trimmed budgets
    """
    _budgets = []
    for b in budgets:
        iati_id = b.get('iati-identifier', None)
        sector = _trim_field(b.get('sector', None), ['code', 'vocabulary'])
        recipient_country = _trim_field(b.get('recipient-country', None), ['code'])
        budget = b.get('budget', None)
        budget_value_usd = b.get('budget.value-usd', None)
        budget_year = _get_budget_year(budget)
        reporting_org = _trim_field(b.get('reporting-org', None), ['ref', 'type', 'secondary-reporter'])
        activity_status = _trim_field(b.get('activity-status', None), ['code'])
        activity_scope = b.get('activity-scope', None)
        document_link = _trim_field(b.get('document-link', None), ['category'])
        hier = b.get('hierarchy', None)
        humanitarian_scope = _trim_field(b.get('humanitarian-scope', None), ['type', 'vocabulary'])
        hum = b.get('humanitarian', None)
        dataset_id = b.get('dataset.id', None)
        dataset_name = b.get('dataset.name', None)
        dataset_resources_hash = b.get('dataset.resources.hash', None)
        dataset_extras_iati_version = b.get('dataset.extras.iati_version', None)
        other_identifier = _trim_field(b.get('other-identifier', None), ['type'])
        tag = _trim_field(b.get('tag', None), ['code', 'vocabulary'])
        default_aid_type = b.get('default-aid-type', None)
        default_currency = b.get('default-currency', None)
        default_finance_type = b.get('default-finance-type', None)
        default_flow_type = b.get('default-flow-type', None)
        lang = b.get('lang', None)
        default_tied_status = b.get('default-tied-status', None)
        collaboration_type = b.get('collaboration-type', None)
        policy_marker = _trim_field(b.get('policy-marker', None), ['code'])
        _trimmed = {
            'iati-identifier': iati_id,
            'sector': sector,
            'recipient-country': recipient_country,
            'budget': budget,
            'budget.value-usd': budget_value_usd,
            'budget.year': budget_year,
            'reporting-org': reporting_org,
            'activity-status': activity_status,
            'activity-scope': activity_scope,
            'document-link': document_link,
            'hierarchy': hier,
            'humanitarian-scope': humanitarian_scope,
            'humanitarian': hum,
            'dataset.id': dataset_id,
            'dataset.name': dataset_name,
            'dataset.resources.hash': dataset_resources_hash,
            'dataset.extras.iati_version': dataset_extras_iati_version,
            'other-identifier': other_identifier,
            'tag': tag,
            'default-aid-type': default_aid_type,
            'default-currency': default_currency,
            'default-finance-type': default_finance_type,
            'default-flow-type': default_flow_type,
            'lang': lang,
            'default-tied-status': default_tied_status,
            'collaboration-type': collaboration_type,
            'policy-marker': policy_marker,
        }
        trimmed = {k: v for k, v in _trimmed.items() if v is not None}
        _budgets.append(trimmed)
    return _budgets


def _split_budgets(budgets):
    """Split budgets on sector, and only keep the budget if the sector or tag is SDG.

    Args:
        budgets (list): list of trimmed budgets

    Returns:
        list: the split budgets list
    """
    if not budgets:
        return None
    _budgets = []
    for budget in budgets:
        sector = budget.get('sector', [])
        if not sector:
            continue
        sector = sector if isinstance(sector, list) else [sector]
        sector = set_default_percentage(sector)
        distributed_budgets = _distribute_budget(budget, sector)
        # Safety catch for empty distributed budgets
        if not distributed_budgets:
            continue
        for distributed_budget in distributed_budgets:
            # create a copy of the budget and add the distributed budget to it
            _budget = deepcopy(budget)
            _budget['budget']['value'] = distributed_budget['amount']
            _budget['budget.value-usd'] = distributed_budget['amount_usd']
            _budget['sector'] = distributed_budget['sector']
            # drop any empty fields, for example budget.value-usd: None in some cases
            _budget = {k: v for k, v in _budget.items() if v is not None}
            _budgets.append(_budget)
    return _budgets


def _distribute_budget(budget, sector):
    """Split the budget by sector.

    Args:
        budget (dict): a budget object
        sector (dict | None): a sector object

    Returns:
        list: a list of distributed budgets
    """
    budget_value = budget.get('budget', {}).get('value', 0)
    budget_value_usd = budget.get('budget.value-usd', None)
    if not sector:
        return None
    sector_list = sector or [{'code': '', 'percentage': 100}]

    distributed_budgets = []
    for sec in sector_list:
        sec_pct = sec.get('percentage', 100) / 100
        amount = round(budget_value * sec_pct, 2)
        amount_usd = None if not budget_value_usd else round(budget_value_usd * sec_pct, 2)
        distributed_budgets.append({
            'sector': sec,
            'amount': amount,
            'amount_usd': amount_usd
        })

    return distributed_budgets


def _trim_field(item, keep_list):
    """Trim a field to only include the fields in keep_list

    Args:
        item (dict | None): a dict containing child items
        keep_list (list): a list of keys possibly included in `item`, to be kept in the trimmed item

    Raises:
        e: any issue with trimming the field

    Returns:
        dict | None: a trimmed item
    """
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


def _split_transactions(transactions):
    """
    Split the transaction into multiple transactions.

    :param transaction: the transaction to split
    :return: the split transaction
    """
    if not transactions:
        return None
    _transactions = []
    for transaction in transactions:
        try:
            _split_transaction(transaction, _transactions)
        except Exception as e:
            logging.error(f"_split_transactions::unable to split transaction {transaction.get('iati-identifier', 'no-id')} due to error: {e}")  # NOQA: E501
    return _transactions


def _split_transaction(transaction, _transactions):
    """Split a single transaction into multiple transactions based on the sdgs.

    Args:
        transaction (dict): a transaction object
        _transactions (list): reference to the list of split transactions created

    Returns:
        None: No return value, the transactions are appended to the list
    """
    # check if there is a a sector, if it is a list, check if len > 1
    recipient_country = transaction.get('recipient-country', [])  # Can be empty
    recipient_country = recipient_country if isinstance(recipient_country, list) else [recipient_country]
    recipient_region = transaction.get('recipient-region', [])  # Can be empty
    recipient_region = recipient_region if isinstance(recipient_region, list) else [recipient_region]
    recipient = set_default_percentage(recipient_country + recipient_region)
    # Can be empty, if empty, sector is reported at transaction level,
    # but in that case, is not relevant to the budget
    sector = transaction.get('sector', [])
    sector = sector if isinstance(sector, list) else [sector]
    sector = set_default_percentage(sector)
    tag = transaction.get('tag', [])
    distributed_transactions = _distribute_transaction(transaction, recipient, sector, tag)
    if not distributed_transactions:
        return None
    for distributed_transaction in distributed_transactions:
        is_sdg = distributed_transaction['is_sdg']
        if not is_sdg:
            continue
        # create a copy of the transaction and add the distributed transaction to it
        recip_code = distributed_transaction['recipient_code']
        sector = distributed_transaction['sector']
        _transaction = deepcopy(transaction)
        _transaction['is-sdg'] = is_sdg
        _transaction['is-sdg.source'] = distributed_transaction['is_sdg_source']
        _transaction['transaction']['value'] = distributed_transaction['amount']
        _transaction['transaction.value-usd'] = distributed_transaction['amount_usd']
        if recip_code in COUNTRIES:
            _transaction['recipient-country'] = {'code': recip_code}
        if recip_code in REGIONS:
            _transaction['recipient-region'] = {'code': recip_code}
        if sector:
            _transaction['sector'] = sector
        # drop any empty fields, for example transaction.value-usd: None in some cases
        _transaction = {k: v for k, v in _transaction.items() if v is not None}
        _transaction = _trim_sdg_item(_transaction)
        _transactions.append(_transaction)


def _distribute_transaction(transaction, recipient, sector, tag):
    """Distribute the transaction amount to each recipient and sector.
    Note: the transaction.sector is not addressed, as it does not contain `percentage` data,
    the same is true for the transaction.recipient-region and transaction.recipient-country.

    Args:
        transaction (dict): a trimmed transaction dictionary
        recipient (_type_): a list of recipient countries or regions
        sector (_type_): a list of sectors
    """
    try:
        transaction_value = transaction.get('transaction', {}).get('value', 0)
        transaction_value_usd = transaction.get('transaction.value-usd', None)
        distributed_transactions = []
        if not recipient and not sector:
            # drop the percentage as we do not store it
            is_sdg, is_sdg_source = _get_is_sdg(None, tag)
            return [{
                'is_sdg': is_sdg,
                'is_sdg_source': is_sdg_source,
                'recipient_code': '',
                'sector': sector,
                'amount': transaction_value,
                'amount_usd': transaction_value_usd,
            }]
        recipient_list = recipient or [{'code': '', 'percentage': 100}]
        sector_list = sector or [{'code': '', 'percentage': 100}]

        # For every recipient and sector, calculate the transaction value
        for rec in recipient_list:
            rec_code = rec.get('code')
            # get the provided percentage, or split equally over the length of the recipient list.
            rec_pct = rec.get('percentage', 100 / len(recipient_list)) / 100
            for sec in sector_list:
                # get the provided percentage, or split equally over the length of the recipient list.
                sec_pct = sec.get('percentage', 100 / len(sector_list)) / 100
                _distributed_transactions_append(distributed_transactions, transaction_value, transaction_value_usd,
                                                 rec_code, rec_pct, sec, sec_pct, tag)
        return distributed_transactions
    except Exception as e:
        logging.error(f"_distribute_transaction::error {e}")
        raise e


def _distributed_transactions_append(distributed_transactions, transaction_value, transaction_value_usd,
                                     rec_code, rec_pct, sector, sec_pct, tag):
    """Function that takes the transaction value, recipient and sector data,
    and creates a distributed transaction object.

    Args:
        distributed_transactions (list): reference to the list of transactions created
        transaction_value (float): transaction value
        transaction_value_usd (float): transaction value in USD
        rec_code (string): recipient code, can be country or region
        rec_pct (float): the percentage of the budget that goes to this recipient
        sec (string): sector dict
        sec_pct (float): the percentage of the budget that goes to this sector
    """
    try:
        amount = round(transaction_value * rec_pct * sec_pct, 2)
        amount_usd = None if not transaction_value_usd else round(transaction_value_usd * rec_pct * sec_pct, 2)
        # drop the percentage as we do not store it
        if sector.get('percentage', None) is not None:
            del sector['percentage']
        is_sdg, is_sdg_source = _get_is_sdg(sector, tag)
        distributed_transactions.append({
            'is_sdg': is_sdg,
            'is_sdg_source': is_sdg_source,
            'recipient_code': rec_code or '',
            'sector': sector,
            'amount': amount,
            'amount_usd': amount_usd
        })
    except Exception as e:
        logging.error(f"_distributed_transactions_append::error {e}")
        raise e


def _trim_sdg_item(item):
    """Trim the SDG item to only include the fields that are needed for the Transaction SDG core.

    Args:
        item (dict): the sdg item to be trimmed

    Returns:
        dict: the item trimmed, or the original item if unable to be trimmed.
    """
    try:
        _item = deepcopy(item)
        for key in item:
            if key in ["last-updated-datetime", 'activity-date.common.start', 'activity-date.common.end',
                       "reporting-org.type.name"]:
                del _item[key]
        _trim_sdg_item_transaction(_item['transaction'])
        _item['tag'] = _trim_field(_item.get('tag', None), ['code', 'vocabulary'])
        _item['reporting-org'] = _trim_field(_item.get('reporting-org', None), ['ref', 'type', 'secondary-reporter'])
        _item['sector'] = _trim_field(_item.get('sector', None), ['code', 'vocabulary'])
        return _item
    except Exception as e:
        logging.error(f"_trim_sdg_item::error {e}")
        return item


def _trim_sdg_item_transaction(_item):
    """Trim the transaction sub-item in the transaction object.

    Args:
        _item (dict): the item to be trimmed

    Raises:
        e: any error with trimming the provided item

    Returns:
        dict: the trimmed item
    """
    try:
        if _item is None:
            return None
        if 'description' in _item:
            del _item['description']
        if 'provider_org' in _item:
            del _item['provider-org']
        _item['receiver-org'] = _trim_field(_item.get('receiver-org', None), ['ref'])
        _item['sector'] = _trim_field(_item.get('sector', None), ['vocabulary'])
    except Exception as e:
        logging.error(f"_trim_sdg_item_transaction::error {e}")
        raise e


def _get_is_sdg(sector, tag):
    """
    Check if the sector or tag is an SDG.

    :param sector: the sector to check
    :param tag: the tag to check
    :return: True if the sector or tag is an SDG, False otherwise
    """
    N_SDG = 17 + 1  # 18 as there are 17 SDGs, plus one for the usage in range
    is_sdg = []
    sdg_source = None
    if sector:
        if sector.get('vocabulary', 0) == 7 and sector.get('code', 0) in range(1, N_SDG):
            is_sdg.append(sector.get('code', 0))
            sdg_source = "sector"
    if tag and is_sdg == []:
        tag = tag if isinstance(tag, list) else [tag]
        for t in tag:
            if t.get('vocabulary', 0) == 2 and t.get('code') in range(1, N_SDG):
                is_sdg.append(t.get('code'))
                sdg_source = 'tag'
    return is_sdg, sdg_source


def _get_budget_year(budget):
    """Retrieve the year from the budget value date.
    Requested for AIDA for simple year filtering.
    Includes a fallback to regex for non-standard formats,
    which are not critical errors in the IATI validator.

    Args:
        budget (dict): budget item from etree

    Returns:
        int | None: the budget's value-date's year
    """
    if not budget:
        return None
    date = budget.get('value.value-date', "")
    if not date:
        return None
    # Try parsing ISO format
    try:
        return datetime.datetime.fromisoformat(date).year
    except (ValueError, TypeError):
        pass
    # Fallback: Extract the first 4-digit series using regex.
    match = re.search(r'\b\d{4}\b', date)
    return int(match.group()) if match else None
