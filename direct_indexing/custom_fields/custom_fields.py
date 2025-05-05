from django.conf import settings

from direct_indexing.custom_fields.activity_dates import activity_dates
from direct_indexing.custom_fields.activity_status import activity_status
from direct_indexing.custom_fields.add_default_hierarchy import add_default_hierarchy
from direct_indexing.custom_fields.codelists import add_codelist_fields
from direct_indexing.custom_fields.currency_aggregation import currency_aggregation
from direct_indexing.custom_fields.currency_conversion import currency_conversion
from direct_indexing.custom_fields.dataset_metadata import add_meta_to_activity, dataset_metadata
from direct_indexing.custom_fields.date_quarters import add_date_quarter_fields
from direct_indexing.custom_fields.document_link_category_combined import document_link_category_combined
from direct_indexing.custom_fields.json_dumps import add_json_dumps
from direct_indexing.custom_fields.policy_marker_combined import policy_marker_combined
from direct_indexing.custom_fields.raise_h2_budget_data_to_h1 import raise_h2_budget_data_to_h1
from direct_indexing.custom_fields.title_narrative import title_narrative_first


def add_all(data, codelists, currencies, metadata):
    """
    Start activity processing.

    :param data: the cleaned dataset.
    :param codelists: an initialized codelist object.
    :param currencies: an initialized currencies object.
    :return: the updated dataset.
    """
    if type(data) is list:
        for activity in data:
            process_activity(activity, codelists, currencies, metadata)
    else:
        process_activity(data, codelists, currencies, metadata)
    # Currency aggregation is done on the whole dataset, rather than on the activity level
    data, id_found = currency_aggregation(data)
    if id_found:
        # if an id was found, there was an issue with the submission of the data to mongoDB.
        # This is a known issue which appears to be unstable. The issue should be prevented by
        # Batch uploading the data to MongoDB in small enough chunks, however,
        # in practice, this does not always resolve the issue.
        # To add one final attempt to resolve the issue, we will run the currency aggregation again.
        # This time with the flag insert_one=True, to attempt to insert each activity separately.
        # Note: This will be slow, but is a last resort only applied to, as seen by the latest test,
        # around 5 datasets at most. In these cases, it is worth the attempt to get around
        # the unstable nature of the issue.
        data, id_found = currency_aggregation(data, insert_one=True)
    if settings.FCDO_INSTANCE:
        # this must be done after the currency aggregation as it increases the size of the data
        add_json_dumps(data)
        # this must be done last as it relies on budgets and date quarters being processed
        data = raise_h2_budget_data_to_h1(data)
    return data, not id_found  # not id_found means that the data was processed correctly


def process_activity(activity, codelists, currencies, metadata):
    """
    Add all custom fields as described above.

    :param activity: the cleaned dataset.
    :param codelists: an initialized codelist object.
    :param currencies: an initialized currencies object.
    :return: the updated dataset.
    """
    add_codelist_fields(activity, codelists)
    title_narrative_first(activity)
    activity_dates(activity)
    activity_status(activity)
    policy_marker_combined(activity)
    currency_conversion(activity, currencies)
    add_meta_to_activity(activity, metadata)
    add_default_hierarchy(activity)
    # FCDO Custom feature
    if settings.FCDO_INSTANCE:
        add_date_quarter_fields(activity)
        document_link_category_combined(activity)


def get_custom_metadata(metadata):
    """
    Pretty wrapper function

    :param metadata: the metadata to be processed
    :return: a subselection of the metadata
    """
    return dataset_metadata(metadata)
