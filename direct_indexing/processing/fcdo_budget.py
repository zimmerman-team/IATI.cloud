import datetime
import json
import logging
import os
from copy import deepcopy

from django.conf import settings

from direct_indexing.processing.subtypes_util import COUNTRIES, DAC3, DAC5, REGIONS, set_default_percentage
from direct_indexing.util import index_to_core

BASE_FCDO_BUDGET = {
    "iati-identifier": '',  # non_case_sensitive
    "h1-activity": '',  # text_general_single
    "h2-activity": '',  # text_general_single
    "recipient-country.code": '',  # text_general_single
    "recipient-country.name": '',  # text_general_single
    "recipient-region.code": '',  # text_general_single
    "recipient-region.name": '',  # text_general_single
    "reporting-org.ref": '',  # text_general_single
    "dac5-sector.code": '',  # pint
    "dac5-sector.name": '',  # text_general_single
    "dac3-sector.code": '',  # pint
    "dac3-sector.name": '',  # text_general_single
    "sector.code": '',  # pint, alternative to DAC5/DAC3 option to remain true to simple `sector` fields
    "sector.narrative": '',  # text_general_single, same as sector.code
    "budget.value-gbp": '',  # pdouble
    "budget.type": '',  # pint
    "budget.period-start.iso-date": '',  # pdate
    "budget.period-end.iso-date": '',  # pdate
    "dataset.id": '',  # text_general_single
    "dataset.name": '',  # text_general_single
    "dataset.resources.hash": '',  # text_general_single
}


def fcdo_budget(filetype, data, json_path, currencies):
    """Entrypoint of this function is the end of dataset_processing.fun -> index_dataset ->
    convert_and_save_xml_to_processed_json, where we have added dataset metadata and
    all custom fields to the dataset.

    Args:
        filetype (string): "activity" or "organisation" identifying whether or not there are budgets
        data (dict): containing all processed IATI activities
        json_path (string): location where the dataset is saved, to be used to save the fcdo_budget.json
        currencies (dict): containing all known currencies and their exchange rates
    """
    # Skip organisation datasets, as there are no budgets.
    if filetype == "organisation":
        logging.info("Skipping organisation dataset.")
    # Create a json filepath for eventual storage of the fcdo_budget.json
    fcdo_budget_filepath = f'{os.path.splitext(json_path)[0]}_fcdo_budget.json'
    all_fcdo_budgets = []
    data = data if isinstance(data, list) else [data]
    for activity in data:
        budgets = activity.get('budget', [])
        budgets = budgets if isinstance(budgets, list) else [budgets]
        if not budgets:
            continue  # Skip if there is no budget in this activity
        try:
            _fcdo_budget_process_activity(activity, budgets, all_fcdo_budgets, currencies)
        except Exception as e:
            logging.error(f"Error processing fcdo_budget for dataset {activity.get('dataset.name', '')} activity {activity.get('iati-identifier', '')}: {e}")  # NOQA: E501
    # Save the fcdo_budget.json file
    with open(fcdo_budget_filepath, 'w', encoding='utf-8') as f:
        json.dump(all_fcdo_budgets, f)
    # Index the fcdo_budget.json file
    try:
        index_to_core(settings.SOLR_FCDO_BUDGET_URL, fcdo_budget_filepath, remove=True)
    except Exception as e:
        logging.error(f"Error indexing fcdo_budget.json for dataset {activity.get('dataset.name', '')} activity {activity.get('iati-identifier', '')}: {e}")  # NOQA: E501


def _fcdo_budget_process_activity(activity, budgets, all_fcdo_budgets, currencies):
    """Extracted from the main function to process each activity and its budgets.
    For the activity, get the main data, and for each budget, get the budget value.

    Args:
        activity (dict): activity data
        budgets (list): all budgets in the given activity
        all_fcdo_budgets (list): central list reference for all fcdo budgets to be stored
        currencies (dict): containing all known currencies and their exchange rates
    """
    iati_id = activity.get('iati-identifier', '')  # Can never be empty
    hierarchy = activity.get('hierarchy', 1)  # Can be empty, defaults to 1
    recipient_country = activity.get('recipient-country', [])  # Can be empty
    recipient_country = recipient_country if isinstance(recipient_country, list) else [recipient_country]
    recipient_region = activity.get('recipient-region', [])  # Can be empty
    recipient_region = recipient_region if isinstance(recipient_region, list) else [recipient_region]
    recipient = set_default_percentage(recipient_country + recipient_region)
    reporting_org_ref = activity.get('reporting-org.ref', '')  # Should never be empty
    # Can be empty, if empty, sector is reported at transaction level,
    # but in that case, is not relevant to the budget
    sector = activity.get('sector', [])
    sector = sector if isinstance(sector, list) else [sector]
    sector = set_default_percentage(sector)
    related_parent = _get_parent_activity(activity.get('related-activity', []))
    dataset_id = activity.get('dataset.id', "ID_NOT_FOUND")
    dataset_name = activity.get('dataset.name', "NAME_NOT_FOUND")
    dataset_resources_hash = activity.get('dataset.resources.hash', "HASH_NOT_FOUND")
    for budget in budgets:
        budget_gbp = _get_budget_value(budget, activity.get('default-currency', 'GBP'), currencies)
        if not budget_gbp:
            # Budget is not valid, skipping
            continue
        budget_start = budget.get('period-start', activity.get('start-iso-date', None))
        budget_end = budget.get('period-end', activity.get('end-iso-date', None))
        budget_type = budget.get('type', 1)
        if not budget_start or not budget_end:
            # Budget does not have a start or end date, even through it is a required field. Skip it.
            continue
        distributed_budget = _distribute_budget(budget_gbp, recipient, sector)
        for db in distributed_budget:
            _create_fcdo_budget_item(iati_id, hierarchy, db, budget_type, budget_start, budget_end, dataset_id,
                                     dataset_name, dataset_resources_hash, all_fcdo_budgets, related_parent,
                                     reporting_org_ref)


def _get_budget_value(budget, default_currency, currencies):
    """Get the currency of the budget value,
    if not present, get the activity default currency,
    if not present default to GBP.

    Args:
        budget (dict): IATI budget data
        default_currency (string): the default currency found in the IATI activity
        currencies (dict): containing all known currencies and their exchange rates

    Returns:
        float | none: distributed budget value in GBP or None if not valid
    """
    budget_value = budget.get('value', 0)
    budget_value_currency = budget.get('value.currency', default_currency)
    if budget_value_currency == 'GBP':
        budget_gbp = budget_value
    else:
        budget_value_value_date = budget.get('value.value-date', None)
        if not budget_value_value_date:
            # Budget does not have a value date, even through it is a required field. Skip it.
            return None
        budget_gbp = _convert_to_gbp(budget_value, budget_value_currency, budget_value_value_date, currencies)
    return budget_gbp


def _convert_to_gbp(budget_value, budget_value_currency, budget_value_value_date, currencies):
    """Convert the provided budget value to GBP for the provided currency and date.

    Args:
        budget_value (float): The budget value
        budget_value_currency (string): The budget currency
        budget_value_value_date (ISO date): The IATI budget's value date
        currencies (dict): containing all known currencies and their exchange rates

    Returns:
        float: the budget value converted to GBP at the provided date.
    """
    if budget_value_value_date is None or budget_value_value_date == '':
        return None, None
    # Exclude malformed budget_value_value_dates
    if '-' in budget_value_value_date[:4] or '-' in budget_value_value_date[5:7]:
        return None, None
    year = int(budget_value_value_date[:4])
    month = int(budget_value_value_date[5:7])
    now = datetime.datetime.now()
    if year > now.year:
        year = now.year
        month = now.month
    if year == now.year and month > now.month:
        month = now.month

    converted_value, _ = currencies.convert_currency(
        budget_value_currency, 'GBP', budget_value, month, year)

    return converted_value


def _get_parent_activity(related_activities):
    """Return the first parent activity found in the list of related activities.

    Args:
        related_activities (list | dict): the list of dicts (or dict) of related activities

    Returns:
        string | None: the ref of the first parent activity found, or None if not found
    """
    if not related_activities:
        return None
    if isinstance(related_activities, dict):
        related_activities = [related_activities]
    for related_activity in related_activities:
        # Requested was single valued ref for the parent activity if exists, so return the first encountered instance.
        if related_activity.get('type', '0') == '1' or related_activity.get('type', 0) == 1:
            return related_activity.get('ref', None)
    return None


def _distribute_budget(total_budget, recipients, sectors):
    """Distribute budget to recipients and sectors based on their percentage.

    Args:
        total_budget (float): Total budget.
        recipients (list): List of recipients with their percentage.
        sectors (list): List of sectors with their percentage.

    Returns:
        dict: Dictionary with distributed budget for each recipient and sector.
    """
    if not recipients and not sectors:
        return [{
            'recipient_code': '',
            'sector_code': '',
            'amount': round(total_budget, 2)
        }]

    budgets = []
    # Ensure there is at least one recipient and sector, if not, add a default empty one
    recipient_list = recipients or [{'code': '', 'percentage': 100}]
    sector_list = sectors or [{'code': '', 'percentage': 100}]

    # For every recipient and sector, calculate the budget
    for rec in recipient_list:
        rec_code = rec.get('code')
        rec_pct = rec.get('percentage', 100 / len(recipient_list)) / 100
        for sec in sector_list:
            sec_code = sec.get('code')
            sec_pct = sec.get('percentage', 100 / len(sector_list)) / 100
            _distribute_budget_append(budgets, total_budget, rec_code, rec_pct, sec_code, sec_pct)

    return budgets


def _distribute_budget_append(budgets, total_budget, rec_code, rec_pct, sec_code, sec_pct):
    """Function that takes the budget value, recipient and sector data,
    and creates a distributed budget object.

    Args:
        budgets (list): reference to the list of budgets created
        total_budget (float): budget value
        rec_code (string): recipient code, can be country or region
        rec_pct (float): the percentage of the budget that goes to this recipient
        sec_code (string): sector code, can be DAC5 or DAC3
        sec_pct (float): the percentage of the budget that goes to this sector
    """
    amount = total_budget * rec_pct * sec_pct
    budgets.append({
        'recipient_code': rec_code or '',
        'sector_code': sec_code or '',
        'amount': round(amount, 2)
    })


def _create_fcdo_budget_item(iati_id, hierarchy, db, budget_type, budget_start, budget_end, dataset_id, dataset_name,
                             dataset_resources_hash, all_fcdo_budgets, related_parent, reporting_org_ref):
    """Extracted from the main function to create a fcdo budget item.
    Takes the input data and inserts it into a copy of the base fcdo budget item.

    Args:
        iati_id (string): IATI identifier
        hierarchy (int): IATI activity hierarchy
        db (dict): distributed budget data
        budget_type (int): IATI budget type related to db
        budget_start (ISO date): IATI budget start date related to db
        budget_end (ISO date): IATI budget end date related to db
        dataset_id (string): IATI Dataset id
        dataset_name (string): IATI Dataset name
        dataset_resources_hash (string): IATI Dataset hash
        all_fcdo_budgets (list): reference to the list of fcdo budget items created.
        related_parent (string): the ref of the parent activity if exists
        reporting_org_ref (string): the ref of the reporting organisation
    """
    item = deepcopy(BASE_FCDO_BUDGET)
    item['iati-identifier'] = iati_id
    if hierarchy == 1:
        item['h1-activity'] = iati_id
        item['h2-activity'] = ''
    elif hierarchy == 2:
        item['h1-activity'] = related_parent if related_parent else ''
        item['h2-activity'] = iati_id
    recip_code = db.get('recipient_code', '')
    if recip_code in COUNTRIES:
        item['recipient-country.code'] = recip_code
        item['recipient-country.name'] = COUNTRIES.get(recip_code, '')
    if recip_code in REGIONS:
        item['recipient-region.code'] = recip_code
        item['recipient-region.name'] = REGIONS.get(recip_code, '')
    item["reporting-org.ref"] = reporting_org_ref
    sector_code = db.get('sector_code', '')
    dac3_name = DAC3.get(sector_code, '')
    dac5_name = DAC5.get(sector_code, '')
    if sector_code in DAC5:
        item['dac5-sector.code'] = sector_code
        item['dac5-sector.name'] = dac5_name
    if sector_code in DAC3:
        item['dac3-sector.code'] = sector_code
        item['dac3-sector.name'] = dac3_name
    item['sector.code'] = sector_code
    item['sector.narrative'] = dac3_name if dac3_name else dac5_name  # if both are empty, defaulkts to empty
    item["budget.value-gbp"] = round(db.get('amount', 0), 2)
    item["budget.type"] = budget_type
    item["budget.period-start.iso-date"] = budget_start
    item["budget.period-end.iso-date"] = budget_end
    item["dataset.id"] = dataset_id
    item["dataset.name"] = dataset_name
    item["dataset.resources.hash"] = dataset_resources_hash
    all_fcdo_budgets.append(item)
