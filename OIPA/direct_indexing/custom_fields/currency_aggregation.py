import logging

from django.conf import settings
from pymongo import MongoClient


def currency_aggregation(data):
    try:
        # Prepare data and connection
        data = prepare_data(data)
        dba, client = connect_to_mongo(data)
        # Aggregate currencies on activity level.
        activity_aggregations = get_aggregations(dba)
        aggregation_fields, formatted_aggregation_fields, child_aggregation_fields, \
            parent_plus_child_aggregation_fields = get_aggregation_fields()
        activity_indexes = index_activity_data(data)
        data = process_activity_aggregations(data, activity_aggregations, activity_indexes, aggregation_fields)

        # Aggregate child currencies
        dba = refresh_mongo_data(dba, data)
        child_aggregations = get_child_aggregations(dba, aggregation_fields)
        data = process_child_aggregations(data, child_aggregations, activity_indexes, aggregation_fields,
                                          child_aggregation_fields, parent_plus_child_aggregation_fields)

        # Close mongo connection
        client.close()

        # Clean up data names
        data = clean_aggregation_result(data, aggregation_fields, formatted_aggregation_fields)
    except Exception as e:  # NOQA
        logging.error("Error in currency aggregation")
        logging.info(e)
    return data


def prepare_data(data):
    # Prep data, mongo cannot query on strings with periods, as they are used as object separators.
    for activity in data:
        if 'transaction.value-usd' in activity.keys():
            activity['transaction-value-usd'] = activity.pop('transaction.value-usd')
        if 'transaction.value-usd-type' in activity.keys():
            activity['transaction-value-usd-type'] = activity.pop('transaction.value-usd-type')
    return data


def connect_to_mongo(data):
    try:
        # Connect to mongo
        client = MongoClient(settings.MONGO_CONNECTION_STRING)
        db = client.activities
        dba = db.activity
        dba.drop()  # Drop previous dataset
        dba.insert_many(data)  # This introduces '_id' key to each data point

        return dba, client
    except:  # NOQA
        logging.error("Error in connecting to mongo")
        raise Exception("A fatal error has occurred.")  # This exception should stop the process


def get_aggregations(dba):
    # Retrieve activity budget aggregation:
    budget_agg = list(dba.aggregate([
        {"$unwind": "$budget"},
        {"$group": {
            "_id": "$iati-identifier",
            "budget-value-sum": {"$sum": "$budget.value"},
        }}
    ]))

    # transactions
    transaction_agg = list(dba.aggregate([
        {"$unwind": "$transaction"},
        {"$group": {
            "_id": ["$iati-identifier", "$transaction.transaction-type.code"],
            "transaction-value-sum": {"$sum": "$transaction.value"},
        }}
    ]))

    # Research array index rather than 2 unwinds.
    transaction_usd_agg = list(dba.aggregate([
        {"$unwind": "$transaction-value-usd-type"},
        {"$unwind": "$transaction-value-usd"},
        {"$group": {
            "_id": ["$iati-identifier", "$transaction-value-usd-type"],
            "transaction-value-usd-sum": {"$sum": "$transaction-value-usd"},
        }}
    ]))

    # Planned disbursement
    planned_disbursement_agg = list(dba.aggregate([
        {"$unwind": "$planned-disbursement"},
        {"$group": {
            "_id": "$iati-identifier",
            "planned-disbursement-value-sum": {"$sum": "$planned-disbursement.value"},
        }}
    ]))

    return {
        'budget': budget_agg,
        'transaction': transaction_agg,
        'transaction-usd': transaction_usd_agg,
        'planned-disbursement': planned_disbursement_agg,
    }


def get_aggregation_fields():
    # Prepare list of fields to be aggregated
    aggregation_fields = {
        "budget": "activity-aggregation-budget-value",
        "budget_usd": "activity-aggregation-budget-value-usd",
        "budget_currency": "activity-aggregation-budget-currency",
        "planned_disbursement": "activity-aggregation-planned-disbursement-value",
        "planned_disbursement_usd": "activity-aggregation-planned-disbursement-value-usd",
        "planned_disbursement_currency": "activity-aggregation-planned-disbursement-currency",
        "incoming_funds": "activity-aggregation-incoming-funds-value",
        "incoming_funds_usd": "activity-aggregation-incoming-funds-value-usd",
        "incoming_funds_currency": "activity-aggregation-incoming-funds-currency",
        "outgoing_commitment": "activity-aggregation-outgoing-commitment-value",
        "outgoing_commitment_usd": "activity-aggregation-outgoing-commitment-value-usd",
        "outgoing_commitment_currency": "activity-aggregation-outgoing-commitment-currency",
        "disbursement": "activity-aggregation-disbursement-value",
        "disbursement_usd": "activity-aggregation-disbursement-value-usd",
        "disbursement_currency": "activity-aggregation-disbursement-currency",
        "expenditure": "activity-aggregation-expenditure-value",
        "expenditure_usd": "activity-aggregation-expenditure-value-usd",
        "expenditure_currency": "activity-aggregation-expenditure-currency",
        "interest_payment": "activity-aggregation-interest-payment-value",
        "interest_payment_usd": "activity-aggregation-interest-payment-value-usd",
        "interest_payment_currency": "activity-aggregation-interest-payment-currency",
        "loan_repayment": "activity-aggregation-loan-repayment-value",
        "loan_repayment_usd": "activity-aggregation-loan-repayment-value-usd",
        "loan_repayment_currency": "activity-aggregation-loan-repayment-currency",
        "reimbursement": "activity-aggregation-reimbursement-value",
        "reimbursement_usd": "activity-aggregation-reimbursement-value-usd",
        "reimbursement_currency": "activity-aggregation-reimbursement-currency",
        "purchase_of_equity": "activity-aggregation-purchase-of-equity-value",
        "purchase_of_equity_usd": "activity-aggregation-purchase-of-equity-value-usd",
        "purchase_of_equity_currency": "activity-aggregation-purchase-of-equity-currency",
        "sale_of_equity": "activity-aggregation-sale-of-equity-value",
        "sale_of_equity_usd": "activity-aggregation-sale-of-equity-value-usd",
        "sale_of_equity_currency": "activity-aggregation-sale-of-equity-currency",
        "credit_guarantee": "activity-aggregation-credit-guarantee-value",
        "credit_guarantee_usd": "activity-aggregation-credit-guarantee-value-usd",
        "credit_guarantee_currency": "activity-aggregation-credit-guarantee-currency",
        "incoming_commitment": "activity-aggregation-incoming-commitment-value",
        "incoming_commitment_usd": "activity-aggregation-incoming-commitment-value-usd",
        "incoming_commitment_currency": "activity-aggregation-incoming-commitment-currency",
        "outgoing_pledge": "activity-aggregation-outgoing-pledge-value",
        "outgoing_pledge_usd": "activity-aggregation-outgoing-pledge-value-usd",
        "outgoing_pledge_currency": "activity-aggregation-outgoing-pledge-currency",
        "incoming_pledge": "activity-aggregation-incoming-pledge-value",
        "incoming_pledge_usd": "activity-aggregation-incoming-pledge-value-usd",
        "incoming_pledge_currency": "activity-aggregation-incoming-pledge-currency",
    }

    # prepare formatted and alternative names for aggregation fields
    formatted_aggregation_fields = {}
    for key in aggregation_fields:
        formatted_aggregation_fields[key] = aggregation_fields[key].replace("aggregation-", "aggregation.").replace(
            "-value", ".value").replace("-currency", ".currency")

    child_aggregation_fields = {}
    for key in formatted_aggregation_fields:
        child_aggregation_fields[key] = formatted_aggregation_fields[key].replace("activity-aggregation",
                                                                                  "child-aggregation")

    parent_plus_child_aggregation_fields = {}
    for key in formatted_aggregation_fields:
        parent_plus_child_aggregation_fields[key] = \
            formatted_aggregation_fields[key].replace("activity-aggregation", "parent-plus-child-aggregation")

    return aggregation_fields, formatted_aggregation_fields, \
        child_aggregation_fields, parent_plus_child_aggregation_fields


def index_activity_data(data):
    i = 0
    activity_indexes = {}
    for activity in data:
        activity_indexes[activity['iati-identifier']] = i
        i = i + 1
    return activity_indexes


def process_activity_aggregations(data, activity_aggregations, activity_indexes, aggregation_fields):
    budget_agg = activity_aggregations['budget']
    transaction_agg = activity_aggregations['transaction']
    transaction_usd_agg = activity_aggregations['transaction-usd']
    planned_disbursement_agg = activity_aggregations['planned-disbursement']

    # Process the aggregated data
    for agg in budget_agg:
        # Find the index of the relevant activity
        if agg['_id'] not in activity_indexes.keys():
            continue
        index_of_activity = activity_indexes[agg['_id']]
        data[index_of_activity][aggregation_fields['budget']] = agg['budget-value-sum']
        if 'budget.value-usd.sum' in data[index_of_activity].keys():
            data[index_of_activity][aggregation_fields['budget_usd']] = data[index_of_activity]['budget.value-usd.sum']
        if 'budget.value-usd.conversion-currency' in data[index_of_activity].keys():
            data[index_of_activity][aggregation_fields['budget_currency']] = data[index_of_activity][
                'budget.value-usd.conversion-currency']

    for agg in planned_disbursement_agg:
        # Find the index of the relevant activity
        if agg['_id'] not in activity_indexes.keys():
            continue
        index_of_activity = activity_indexes[agg['_id']]
        data[index_of_activity][aggregation_fields['planned_disbursement']] = agg['planned-disbursement-value-sum']
        if 'planned-disbursement.value-usd.sum' in data[index_of_activity].keys():
            data[index_of_activity][aggregation_fields['planned_disbursement_usd']] = data[index_of_activity][
                'planned-disbursement.value-usd.sum']
        if 'planned-disbursement.value-usd.conversion-currency' in data[index_of_activity].keys():
            data[index_of_activity][aggregation_fields['planned_disbursement_currency']] = data[index_of_activity][
                'planned-disbursement.value-usd.conversion-currency']

    # Transaction types, starting with none to make array index match the transaction type code from the codelist
    transaction_types = [None, "incoming-funds", "outgoing-commitment", "disbursement",
                         "expenditure", "interest-payment", "loan-repayment",
                         "reimbursement", "purchase-of-equity", "sale-of-equity",
                         "credit-guarantee", "incoming-commitment", "outgoing-pledge",
                         "incoming-pledge"]
    tt_underscored = [t.replace("-", "_") if t else None for t in transaction_types]

    for agg in transaction_agg:
        # Find the index of the relevant activity
        if agg['_id'][0] not in activity_indexes.keys():
            continue
        index_of_activity = activity_indexes[agg['_id'][0]]
        transaction_type = agg['_id'][1]
        data[index_of_activity][f'{aggregation_fields[tt_underscored[transaction_type]]}'] = \
            agg['transaction-value-sum']

    for agg in transaction_usd_agg:
        if agg['_id'][0] not in activity_indexes.keys():
            continue
        # Find the index of the relevant activity
        index_of_activity = activity_indexes[agg['_id'][0]]
        transaction_type = agg['_id'][1]
        data[index_of_activity][f'{aggregation_fields[tt_underscored[transaction_type]]}_usd'] = agg[
            'transaction-value-usd-sum']
        if 'transaction-value-usd-conversion-currency' in data[index_of_activity].keys():
            data[index_of_activity][f'{aggregation_fields[tt_underscored[transaction_type]]}_currency'] = \
                data[index_of_activity]['transaction.value-usd.conversion-currency']

    return data


def refresh_mongo_data(dba, data):
    # Refresh mongo data so we can access the new activity aggregation,
    # as the child aggregations are the sums of their children
    dba.drop()  # Drop previous dataset
    dba.insert_many(data)  # Re-submit updated dataset
    return dba


def get_child_aggregations(dba, aggregation_fields):
    # Prepare group object which sums up each aggregation field.
    group_object = {"_id": "$related-activity.ref"}
    for key in aggregation_fields:
        if "currency" not in aggregation_fields[key]:
            group_object[key] = {"$sum": f'${aggregation_fields[key]}'}

    # Get aggregations for all fields
    children_agg = list(dba.aggregate([
        {"$unwind": "$related-activity"},
        {"$match": {"related-activity.type": 2}},
        {"$group": group_object}
    ]))
    return children_agg


def process_child_aggregations(data, children_agg, activity_indexes, aggregation_fields, child_aggregation_fields,
                               parent_plus_child_aggregation_fields):
    for agg in children_agg:
        if agg['_id'] not in activity_indexes.keys():
            # skip activities that are not in the parent dataset
            # TODO: Add "post indexing" function that adds these remaining aggregations to the data
            continue
            # Find the index of the relevant activity
        index_of_activity = activity_indexes[agg.pop('_id')]

        for key in agg.keys():
            # Add the child aggregations to the data
            data[index_of_activity][child_aggregation_fields[key]] = agg[key]
            # Add the parent plus child aggregations to the data
            parent_value = 0  # Only retrieve value if the value exists in parent
            if aggregation_fields[key] in data[index_of_activity].keys():
                parent_value = data[index_of_activity][aggregation_fields[key]]
            data[index_of_activity][parent_plus_child_aggregation_fields[key]] = agg[key] + parent_value

            # Make sure we add the currency as well:
            if key + "_currency" in child_aggregation_fields.keys():  # Check once as both have the same keys
                currency = "USD"  # Default to USD
                if key == 'budget' and 'budget.value-usd.conversion-currency' in data[index_of_activity].keys():
                    currency = data[index_of_activity]['budget.value-usd.conversion-currency']
                if key == 'planned-disbursement' \
                        and 'budget.value-usd.conversion-currency' in data[index_of_activity].keys():
                    currency = data[index_of_activity]['planned-disbursement.value-usd.conversion-currency']
                if key == 'transaction' \
                        and 'transaction.value-usd.conversion-currency' in data[index_of_activity].keys():
                    currency = data[index_of_activity]['transaction.value-usd.conversion-currency']
                data[index_of_activity][child_aggregation_fields[key + "_currency"]] = currency
                data[index_of_activity][parent_plus_child_aggregation_fields[key + "_currency"]] = currency

    return data


def clean_aggregation_result(data, aggregation_fields, formatted_aggregation_fields):
    for activity in data:
        if '_id' in activity.keys():
            activity.pop('_id')  # Remove mongo introduced '_id'.
        if 'transaction-value-usd' in activity.keys():
            activity['transaction.value-usd'] = activity.pop('transaction-value-usd')
        if 'transaction-value-usd-type' in activity.keys():
            activity['transaction.value-usd-type'] = activity.pop('transaction-value-usd-type')

        # Go through the - appended aggregation_fields and rename to formatted_aggregation_fields
        for key, value in aggregation_fields.items():
            if value not in activity.keys():
                continue
            activity[formatted_aggregation_fields[key]] = activity.pop(value)
    return data
