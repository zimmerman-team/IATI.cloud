from django.db.models import Sum, Max
from iati.models import Activity


def identifier_correct_prefix(self, a):
    """
    Rule: Must be prefixed with either the current org ref for the reporting org or a previous identifier reported in other-identifier, and suffixed with the organisations own activity identifier.
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
        "Must be prefixed with either the current org ref for the reporting org or a previous identifier reported in other-identifier", 
        -1, 
        '-',
        a.iati_identifier)


def geo_percentages_add_up(self, a):
    """
    Rule: Percentages for all reported countries and regions must add up to 100%
    """
    recipient_country_sum = a.activityrecipientcountry_set.all().aggregate(Sum('percentage')).get('percentage__sum')
    recipient_region_sum = a.activityrecipientregion_set.all().aggregate(Sum('percentage')).get('percentage__sum')

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
            "Percentages for all reported countries and regions must add up to 100%", 
            -1, 
            '-',
            a.iati_identifier)


def sector_percentages_add_up(self, a):
    """
    Rule: Percentages for all reported sectors must add up to 100%
    """
    sector_sum = a.activitysector_set.all().aggregate(Sum('percentage')).get('percentage__sum')
    
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
    If this element is used then ALL transaction elements should contain a transaction/sector element and iati-activity/sector should NOT be used
    Either transaction/sector or sector must be present.

    This element can be used multiple times, but only one sector can be reported per vocabulary.

    """
    direct_count = a.activitysector_set.filter(sector__vocabulary='1').count()
    indirect_count = a.transaction_set.filter(
        transaction_sector__isnull=False,
        transaction_sector__sector__vocabulary='1', 
        ).count()

    if direct_count and indirect_count:
        self.append_error(
            "FieldValidationError", 
            "transaction/sector", 
            "-", 
            "If this element is used then ALL transaction elements should contain a transaction/sector element and iati-activity/sector should NOT be used", 
            -1, 
            '-',
            a.iati_identifier)

    if (direct_count + indirect_count) == 0:
        self.append_error(
            "FieldValidationError", 
            "sector", 
            "-", 
            "Either transaction/sector or sector must be present", 
            -1, 
            '-',
            a.iati_identifier)


def use_direct_geo_or_transaction_geo(self, a):
    """
    Rules:
    If this element is used then ALL transaction elements should contain a transaction/recipient-country element and iati-activity/recipient-country should NOT be used
    Either transaction/recipient-country or recipient-country must be present.
    If this element is used then ALL transaction elements should contain a transaction/recipient-region element and iati-activity/recipient-region should NOT be used
    This element can be used multiple times, but only one recipient-region can be reported per vocabulary.
    Either transaction/recipient-region or recipient-region must be present.
    only a recipient-region OR a recipient-country is expected
    """
    direct_count = a.activityrecipientcountry_set.count() + a.activityrecipientregion_set.count()
    indirect_count = a.transaction_set.filter(transaction_recipient_country__isnull=False).count() + a.transaction_set.filter(transaction_recipient_region__isnull=False).count()

    if direct_count and indirect_count:
        self.append_error(
            "FieldValidationError", 
            "transaction/sector", 
            "-", 
            "If this element is used then ALL transaction elements should contain a transaction/sector element and iati-activity/sector should NOT be used", 
            -1, 
            '-',
            a.iati_identifier)

    if (direct_count + indirect_count) == 0:
        self.append_error(
            "FieldValidationError", 
            "recipient-country/recipient-region", 
            "-", 
            "Either transaction/recipient-country,transaction/recipient-region or recipient-country,recipient-region must be present", 
            -1, 
            '-',
            a.iati_identifier)


def transactions_at_multiple_levels(self, dataset):
    """
    Rule: If multiple hierarchy levels are reported then financial transactions should only be reported at the lowest hierarchical level
    """
    max_hierarchy = Activity.objects.filter(dataset=dataset).aggregate(Max('hierarchy')).get('hierarchy__max')
    
    if Activity.objects.filter(dataset=dataset).exclude(hierarchy=max_hierarchy).filter(transaction__isnull=False).count():

        self.append_error(
            "FieldValidationError", 
            "transaction", 
            "-", 
            "If multiple hierarchy levels are reported then financial transactions should only be reported at the lowest hierarchical level", 
            -1, 
            '-',
            "dataset validation error")

