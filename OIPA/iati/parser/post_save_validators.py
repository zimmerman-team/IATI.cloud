from django.db.models import Max, Sum

from iati.models import (
    Activity, ActivityParticipatingOrganisation, RelatedActivity,
    ResultIndicatorReference, ResultReference
)
from iati.transaction.models import TransactionProvider, TransactionReceiver


def identifier_correct_prefix(self, a):
    """
    Rule: Must be prefixed with either the current org ref for the reporting
    org or a previous identifier reported in other-identifier, and suffixed
    with the organisations own activity identifier.
    """
    reporting_org = a.reporting_organisations.first()
    if not reporting_org:
        return
    if a.iati_identifier.startswith(reporting_org.ref):
        return
    else:
        for oi in a.otheridentifier_set.all():
            if a.iati_identifier.startswith(oi.identifier):
                return
    self.append_error(
        "FieldValidationError",
        "iati-identifier",
        "ref",
        ("Must be prefixed with either the current org ref for the reporting "
         "org or a previous identifier reported in other-identifier"),
        -1,
        reporting_org.ref,
        a.iati_identifier)


def geo_percentages_add_up(self, a):
    """
    Rule: Percentages for all reported countries and regions must add up to
    100%
    """
    recipient_country_sum = a.activityrecipientcountry_set.all().aggregate(
        Sum('percentage')
    ).get('percentage__sum')
    recipient_region_sum = a.activityrecipientregion_set.all(
    ).aggregate(Sum('percentage')).get('percentage__sum')

    total_sum = 0
    if recipient_country_sum:
        total_sum += recipient_country_sum
    if recipient_region_sum:
        total_sum += recipient_region_sum

    if not (total_sum == 0 or total_sum == 100):
        self.append_error(
            "FieldValidationError",
            "recipient-country/recipient-region",
            "percentage",
            ("Percentages for all reported countries and regions must add up "
             "to 100%"),
            -1,
            '-',
            a.iati_identifier)


def sector_percentages_add_up(self, a):
    """
    Rule: Percentages for all reported sectors must add up to 100%
    """
    sector_sum = a.activitysector_set.all().aggregate(
        Sum('percentage')).get('percentage__sum')

    if not (sector_sum is None or sector_sum == 0 or sector_sum == 100):
        self.append_error(
            "FieldValidationError",
            "sector",
            "percentage",
            "Percentages for all reported sectors must add up to 100%",
            -1,
            '-',
            a.iati_identifier)


def use_sector_or_transaction_sector(self, a):
    """
    Rules:
    If this element is used then ALL transaction elements should contain a
    transaction/sector element and iati-activity/sector should NOT be used
    Either transaction/sector or sector must be present.

    This element can be used multiple times, but only one sector can be
    reported per vocabulary.

    """
    direct_count = a.activitysector_set.count()
    indirect_count = a.transaction_set.filter(
        transaction_sector__isnull=False,
    ).count()

    if direct_count and indirect_count:
        self.append_error(
            "FieldValidationError",
            "transaction/sector",
            "-",
            ("If this element is used then ALL transaction elements should "
             "contain a transaction/sector element and "
             "iati-activity/sector should NOT be used"),
            -1,
            '-',
            a.iati_identifier)

    if (direct_count + indirect_count) == 0:
        self.append_error(
            "FieldValidationError",
            "sector",
            "-",
            ("Either transaction/sector or sector must be present (DAC "
             "vocabulary)"),
            -1,
            '-',
            a.iati_identifier)


def use_direct_geo_or_transaction_geo(self, a):
    """
    A supranational geopolitical region that will benefit from this
    transaction. If a specific country is not known, then this element MUST be
    used.

    If transaction/recipient-country AND/OR transaction/recipient-region are
    used THEN ALL transaction elements MUST contain a recipient-country or
    recipient-region element AND (iati-activity/recipient-country AND
    iati-activity/recipient-region MUST NOT be used)
    """
    direct_count = a.activityrecipientcountry_set.count()\
        + a.activityrecipientregion_set.count()

    indirect_count = a.transaction_set.filter(
        transaction_recipient_country__isnull=False
    ).count() + a.transaction_set.filter(
        transaction_recipient_region__isnull=False
    ).count()

    if direct_count and indirect_count:
        self.append_error(
            "FieldValidationError",
            "transaction/sector",
            "-",
            ("If this element is used then ALL transaction elements should "
                "contain a transaction/sector element and "
                "iati-activity/sector should NOT be used"),
            -1,
            '-',
            a.iati_identifier)

    if (direct_count + indirect_count) == 0:
        self.append_error(
            "FieldValidationError",
            "recipient-country/recipient-region",
            "-",
            ("Either transaction/recipient-country,transaction/recipient- "
                "region or recipient-country,recipient-region must be present "
                "(DAC vocabulary)"),
            -1,
            '-',
            a.iati_identifier)


def transactions_at_multiple_levels(self, dataset):
    """
    Rule: If multiple hierarchy levels are reported then financial transactions
    should only be reported at the lowest hierarchical level
    """

    # TODO - query this from the Dataset since the query below is presumeably
    # slower - 2017-06-20

    max_hierarchy = Activity.objects.filter(
        dataset=dataset).aggregate(
        Max('hierarchy')).get('hierarchy__max')

    if Activity.objects.filter(dataset=dataset).exclude(
            hierarchy=max_hierarchy).filter(transaction__isnull=False).count():

        self.append_error(
            "FieldValidationError",
            "transaction",
            "-",
            ("If multiple hierarchy levels are reported then financial "
             "transactions should only be reported at the lowest "
             "hierarchical level"),
            -1,
            '-',
            "dataset validation error")


def unfound_identifiers(self, dataset):

    for ra in RelatedActivity.objects.filter(
            current_activity__dataset=dataset, ref_activity=None):
        variable = ra.ref
        activity_id = ra.current_activity.iati_identifier
        self.append_error(
            "FieldValidationError",
            "related-activity",
            "ref",
            "Must be an existing IATI activity",
            -1,
            variable,
            activity_id)

    for tp in TransactionProvider.objects.filter(
            transaction__activity__dataset=dataset,
            provider_activity=None,
            provider_activity_ref__isnull=False):
        variable = tp.provider_activity_ref
        activity_id = tp.transaction.activity.iati_identifier

        self.append_error(
            "FieldValidationError",
            "transaction/provider-org",
            "provider-activity-id",
            "Must be an existing IATI activity",
            -1,
            variable,
            activity_id)

    for tr in TransactionReceiver.objects.filter(
            transaction__activity__dataset=dataset,
            receiver_activity=None,
            receiver_activity_ref__isnull=False):
        variable = tr.receiver_activity_ref
        activity_id = tr.transaction.activity.iati_identifier

        self.append_error(
            "FieldValidationError",
            "transaction/receiver-org",
            "receiver-activity-id",
            "Must be an existing IATI activity",
            -1,
            variable,
            activity_id)

    for po in ActivityParticipatingOrganisation.objects.filter(
            activity__dataset=dataset, org_activity_id__isnull=False,
            org_activity_obj=None):
        variable = po.org_activity_id
        activity_id = po.activity.iati_identifier
        self.append_error(
            "FieldValidationError",
            "participating-org",
            "activity-id",
            "Must be an existing IATI activity",
            -1,
            variable,
            activity_id)


# TODO: test:
def use_result_reference_or_indicator_reference(self, activity):
    '''New (optional) <reference> element for <result> element in IATI v. 2.03

    The reference element can be repeated in any result. If the reference
    element is reported at result level it must not be reported at
    indicator level
    '''

    activity_result_references = ResultReference.objects.filter(
        result__activity=activity)
    activity_result_indicator_references = ResultIndicatorReference.objects\
        .filter(result_indicator__result__activity=activity)

    if (activity_result_references.exists()
            and activity_result_indicator_references.exists()):

        self.append_error(
            "FieldValidationError",
            "iati-activity/result/reference",
            "-",
            ("If the reference element is reported at result level it must "
             "not be reported at indicator level"),
            -1,
            '-',
            activity.iati_identifier)


# TODO: test:
def one_aid_type_for_each_vocabulary(self, activity):
    '''On a Activity transaction level, multiple AidTypes can be reported, but
    different vocabularies have to be used
    '''

    for transaction in activity.transaction_set.all():
        vocabularies = transaction.transactionaidtype_set.values_list(
            'aid_type__vocabulary__code', flat=True
        )

        if len(vocabularies) != len(set(vocabularies)):

            self.append_error(
                "FieldValidationError",
                "iati-activities/iati-activity/transaction/aid-type",
                "-",
                ("AidTypes within Transaction level must use different "
                 "vocabularies"),
                -1,
                '-',
                activity.iati_identifier)
