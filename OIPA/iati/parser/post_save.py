"""
Methods triggered after activity has been parsed
"""

from decimal import Decimal

from iati import activity_search_indexes, models
from iati.activity_aggregation_calculation import (
    ActivityAggregationCalculation
)
from iati.transaction import models as transaction_models


def set_related_activities(activity):
    """ update related-activity references to this activity """
    models.RelatedActivity.objects.filter(
        ref=activity.iati_identifier).update(
        ref_activity=activity)


def set_participating_organisation_activity_id(participating_organisation):
    """ update activity_id references to this activity """
    # TODO: add reverse relation for participating organisation activity_id
    # - 2016-05-31
    pass


def set_transaction_provider_receiver_activity(activity):
    """ update transaction-provider, transaction-receiver references to this
    activity """
    transaction_models.TransactionProvider.objects.filter(
        provider_activity_ref=activity.iati_identifier
    ).update(provider_activity=activity)

    transaction_models.TransactionReceiver.objects.filter(
        receiver_activity_ref=activity.iati_identifier
    ).update(receiver_activity=activity)


def set_derived_activity_dates(activity):
    """Set derived activity dates

    actual start dates are preferred.
    In case they don't exist, use planned dates.

    This is used for ordering by start/end date.
    """
    if activity.actual_start:
        activity.start_date = activity.actual_start
    else:
        activity.start_date = activity.planned_start

    if activity.actual_end:
        activity.end_date = activity.actual_end
    else:
        activity.end_date = activity.planned_end
    activity.save()


def set_activity_aggregations(activity):
    """
    set total activity aggregations for the different transaction types and
    budget
    """
    aac = ActivityAggregationCalculation()
    aac.parse_activity_aggregations(activity)


def update_activity_search_index(activity):
    """
    Update the Postgres FTS indexes
    """
    activity_search_indexes.reindex_activity(activity)


def set_country_region_transaction(activity):
    """
    IATI business rule: If transaction/recipient-country AND/OR
    transaction/recipient-region are used
    THEN ALL transaction elements MUST contain a recipient-country or
    recipient-region element
    AND (iati-activity/recipient-country AND iati-activity/recipient-region
    MUST NOT be used)

    Functionality:
    -adds TransactionRecipientCountry/TransactionRecipientRegion if recipient
    country/region are not set on the transaction itself
    -sets correct xdr_value on
    TransactionRecipientCountry/TransactionRecipientRegion based on percentages

    Notes:
    for added items, TransactionRecipientCountry.reported_on_transaction is set
    to False.
    This is to make sure we can serialize it correctly on API output;
    when a reporting org does not report recipient-country on the transaction,
    we'll have to be sure we also don't show it when exporting to XML in our
    API.

    Purpose:
    Make both ways of reporting on recipient country / recipient region
    comparable by storing them in the same way.
    Aggregations become less complex when doing so.

    """
    if not activity.transaction_set.count():
        return False

    # check if country or region are set on transaction by checking the first
    # transaction, then 100% of the xdr_value will go to the country/region
    t = activity.transaction_set.all()[0]
    if t.transactionrecipientcountry_set.count()\
            or t.transactionrecipientregion_set.count():
        for t in activity.transaction_set.all():
            for trc in t.transactionrecipientcountry_set.all():
                trc.percentage = 100
                trc.save()
            for trr in t.transactionrecipientregion_set.all():
                trr.percentage = 100
                trr.save()
    else:
        # not set on the transaction, check if percentages given
        # if so use the percentages, else divide equally
        countries = activity.activityrecipientcountry_set.all()
        regions = activity.activityrecipientregion_set.all()

        # check if percentages are not set, then divide equally
        if len(countries.filter(percentage=None))\
                or len(regions.filter(percentage=None)):
            total_count = countries.count() + regions.count()
            percentage = Decimal(100) / Decimal(total_count)
            for recipient_country in countries:
                recipient_country.percentage = percentage
            for recipient_region in regions:
                recipient_region.percentage = percentage

        # create TransactionRecipientCountry/Region for each transaction, for
        # each country/region
        for t in activity.transaction_set.all():
            for recipient_country in countries:
                trc = transaction_models.TransactionRecipientCountry(
                    transaction=t,
                    country=recipient_country.country,
                    percentage=recipient_country.percentage,
                    reported_on_transaction=False
                )
                trc.save()

            for recipient_region in regions:
                trr = transaction_models.TransactionRecipientRegion(
                    transaction=t,
                    region=recipient_region.region,
                    percentage=recipient_region.percentage,
                    reported_on_transaction=False
                )
                trr.save()


def set_sector_transaction(activity):
    """
    IATI business rule: If this element is used then ALL transaction elements
    should contain a transaction/sector element and iati-activity/sector
    should NOT be used.

    For functionality/notes/purpose see set_country_region_transaction.
    This function does the same thing for sectors.
    """
    if not activity.transaction_set.count():
        return False

    t = activity.transaction_set.all().order_by('pk').first()
    # set on transaction?
    if t.transactionsector_set.count():
        # its set on transactions
        for t in activity.transaction_set.all():
            for ts in t.transactionsector_set.all():
                ts.percentage = 100
                ts.save()
    # set on activity level
    else:
        sectors = activity.activitysector_set.all()

        # check if percentages are not set, if so divide percentages equally
        # over amount of sector
        if len(sectors.filter(percentage=None)):
            vocabulary_codes = []
            for val in activity.activitysector_set.values('vocabulary__code'):
                if not val['vocabulary__code'] in vocabulary_codes:
                    vocabulary_codes.append(val['vocabulary__code'])

            for vocabulary_code in vocabulary_codes:
                sectors_filtred = activity.activitysector_set.filter(
                    vocabulary__code=vocabulary_code)
                total_count = sectors_filtred.count()
                percentage = Decimal(100) / Decimal(total_count)
                for s in sectors_filtred:
                    s.percentage = percentage

        # create TransactionSector for each sector for each transaction with
        # correct xdr_value

                for t in activity.transaction_set.all():
                    for recipient_sector in sectors_filtred:
                        transaction_models.TransactionSector(
                            transaction=t,
                            sector=recipient_sector.sector,
                            percentage=recipient_sector.percentage,
                            vocabulary=recipient_sector.sector.vocabulary,
                            reported_on_transaction=False
                        ).save()
        else:
            for t in activity.transaction_set.all():
                for recipient_sector in sectors:
                    transaction_models.TransactionSector(
                        transaction=t,
                        sector=recipient_sector.sector,
                        percentage=recipient_sector.percentage,
                        vocabulary=recipient_sector.sector.vocabulary,
                        reported_on_transaction=False
                    ).save()


def set_sector_budget(activity):
    """
    Purpose:
    Store percentages per sector per budget.
    Aggregations become less complex when doing so.
    """
    if not activity.budget_set.count():
        return False

    sectors = activity.activitysector_set.all()

    # if percentages are not set divide percentages equally over amount of
    # sectors
    if len(sectors.filter(percentage=None)):
        total_count = sectors.count()
        percentage = Decimal(100) / Decimal(total_count)
        for s in sectors:
            s.percentage = percentage

    # create BudgetSector for each sector for each budget
    for b in activity.budget_set.all():
        for recipient_sector in sectors:

            models.BudgetSector(
                budget=b,
                sector=recipient_sector.sector,
                percentage=recipient_sector.percentage
            ).save()
