

from django.db.models import Q
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel, OneToOneRel
from django_filters import (
    BooleanFilter, CharFilter, DateFilter, DateTimeFilter, FilterSet,
    NumberFilter, TypedChoiceFilter
)
from django_filters.widgets import BooleanWidget
from rest_framework import filters

from api.generics.filters import (
    CommaSeparatedCharFilter, CommaSeparatedStickyCharFilter,
    IsNullBooleanFilter, StartsWithInCommaSeparatedCharFilter,
    TogetherFilterSet, ToManyFilter, ToManyNotInFilter
)
from iati.models import (
    Activity, ActivityParticipatingOrganisation, ActivityPolicyMarker,
    ActivityRecipientCountry, ActivityRecipientRegion,
    ActivityReportingOrganisation, ActivitySector, Budget, DocumentLink,
    HumanitarianScope, OtherIdentifier, RelatedActivity, Result,
    ResultIndicatorPeriod, ResultIndicatorTitle
)
from iati.transaction.models import Transaction
from iati_synchroniser.models import Dataset, Publisher


class ActivityFilter(TogetherFilterSet):

    activity_id = CommaSeparatedCharFilter(
        name='id',
        lookup_expr='in')

    iati_identifier = CommaSeparatedCharFilter(
        name='iati_identifier',
        lookup_expr='in')

    activity_scope = CommaSeparatedCharFilter(
        name='scope__code',
        lookup_expr='in',)

    budget_not_provided = CommaSeparatedCharFilter(
        name='budget_not_provided',
        lookup_expr='in',
    )

    is_secondary_reporter = BooleanFilter(
        name='reporting_organisations__secondary_reporter',
        widget=BooleanWidget())

    has_crs_add = IsNullBooleanFilter(name='crsadd', lookup_expr='isnull',
                                      distinct=True,
                                      widget=BooleanWidget())

    has_other_identifier = IsNullBooleanFilter(name='otheridentifier',
                                               lookup_expr='isnull',
                                               distinct=True,
                                               widget=BooleanWidget()
                                               )

    has_contact_info = IsNullBooleanFilter(name='contactinfo',
                                           lookup_expr='isnull',
                                           distinct=True,
                                           widget=BooleanWidget()
                                           )

    has_activity_scope = IsNullBooleanFilter(name='scope',
                                             lookup_expr='isnull',
                                             distinct=True,
                                             widget=BooleanWidget()
                                             )

    has_recipient_country = IsNullBooleanFilter(
        name='activityrecipientcountry', lookup_expr='isnull',
        distinct=True, widget=BooleanWidget())

    has_recipient_region = IsNullBooleanFilter(name='activityrecipientregion',
                                               lookup_expr='isnull',
                                               distinct=True,
                                               widget=BooleanWidget())

    has_location = IsNullBooleanFilter(name='location',
                                       lookup_expr='isnull', distinct=True,
                                       widget=BooleanWidget())

    has_sector = IsNullBooleanFilter(name='activitysector',
                                     lookup_expr='isnull', distinct=True,
                                     widget=BooleanWidget())

    has_tag = IsNullBooleanFilter(name='activitytag', lookup_expr='isnull',
                                  distinct=True,
                                  widget=BooleanWidget())

    has_country_budget_item = IsNullBooleanFilter(
        name='country_budget_items',
        lookup_expr='isnull',
        distinct=True,
        widget=BooleanWidget()
    )

    has_humanitarian_scope = IsNullBooleanFilter(name='humanitarianscope',
                                                 lookup_expr='isnull',
                                                 distinct=True,
                                                 widget=BooleanWidget()
                                                 )

    has_policy_marker = IsNullBooleanFilter(name='activitypolicymarker',
                                            lookup_expr='isnull',
                                            distinct=True,
                                            widget=BooleanWidget()
                                            )

    has_collaboration_type = IsNullBooleanFilter(name='collaboration_type',
                                                 lookup_expr='isnull',
                                                 distinct=True,
                                                 widget=BooleanWidget()
                                                 )

    has_default_flow_type = IsNullBooleanFilter(name='default_flow_type',
                                                lookup_expr='isnull',
                                                distinct=True,
                                                widget=BooleanWidget()
                                                )

    has_default_finance_type = IsNullBooleanFilter(name='default_finance_type',
                                                   lookup_expr='isnull',
                                                   distinct=True,
                                                   widget=BooleanWidget()
                                                   )

    has_default_aid_type = IsNullBooleanFilter(name='default_aid_types',
                                               lookup_expr='isnull',
                                               distinct=True,
                                               widget=BooleanWidget()
                                               )

    has_default_tied_status = IsNullBooleanFilter(
        name='default_tied_status',
        lookup_expr='isnull',
        distinct=True,
        widget=BooleanWidget()
    )

    has_budget = IsNullBooleanFilter(name='budget', lookup_expr='isnull',
                                     distinct=True, widget=BooleanWidget()
                                     )

    has_planned_disbursement = IsNullBooleanFilter(name='planneddisbursement',
                                                   lookup_expr='isnull',
                                                   distinct=True,
                                                   widget=BooleanWidget()
                                                   )

    has_capital_spend = IsNullBooleanFilter(name='capital_spend',
                                            lookup_expr='isnull',
                                            distinct=True,
                                            widget=BooleanWidget()
                                            )

    has_document_link = IsNullBooleanFilter(name='documentlink',
                                            lookup_expr='isnull',
                                            distinct=True,
                                            widget=BooleanWidget()
                                            )

    has_related_activity = IsNullBooleanFilter(name='relatedactivity',
                                               lookup_expr='isnull',
                                               distinct=True,
                                               widget=BooleanWidget()
                                               )

    has_legacy_data = IsNullBooleanFilter(name='legacydata',
                                          lookup_expr='isnull', distinct=True,
                                          widget=BooleanWidget()
                                          )

    has_condition = IsNullBooleanFilter(name='conditions',
                                        lookup_expr='isnull',  # related name of Foreign Key for `activity` is `conditions` # NOQA: E501
                                        distinct=True,
                                        widget=BooleanWidget()
                                        )
    has_result = IsNullBooleanFilter(name='result', lookup_expr='isnull',
                                     distinct=True, widget=BooleanWidget()
                                     )

    has_fss = IsNullBooleanFilter(name='fss', lookup_expr='isnull',
                                  distinct=True, widget=BooleanWidget()
                                  )

    document_link_category = ToManyFilter(
        qs=DocumentLink,
        lookup_expr='in',
        name='categories',
        fk='activity',
    )

    last_updated_datetime_gt = DateTimeFilter(
        lookup_expr='gt',
        name='last_updated_datetime'
    )

    planned_start_date_lte = DateFilter(
        lookup_expr='lte',
        name='planned_start')

    planned_start_date_gte = DateFilter(
        lookup_expr='gte',
        name='planned_start')

    actual_start_date_lte = DateFilter(
        lookup_expr='lte',
        name='actual_start')

    actual_start_date_gte = DateFilter(
        lookup_expr='gte',
        name='actual_start')

    planned_end_date_lte = DateFilter(
        lookup_expr='lte',
        name='planned_end')

    planned_end_date_gte = DateFilter(
        lookup_expr='gte',
        name='planned_end')

    actual_end_date_lte = DateFilter(
        lookup_expr='lte',
        name='actual_end')

    actual_end_date_gte = DateFilter(
        lookup_expr='gte',
        name='actual_end')

    end_date_lte = DateFilter(
        lookup_expr='lte',
        name='end_date')

    end_date_gte = DateFilter(
        lookup_expr='gte',
        name='end_date')

    start_date_lte = DateFilter(
        lookup_expr='lte',
        name='start_date')

    start_date_gte = DateFilter(
        lookup_expr='gte',
        name='start_date')

    end_date_isnull = BooleanFilter(lookup_expr='isnull', name='end_date')
    start_date_isnull = BooleanFilter(lookup_expr='isnull', name='start_date')

    activity_status = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='activity_status',)

    hierarchy = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='hierarchy',)

    collaboration_type = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='collaboration_type',)

    def flow_type_filter(self, qs, name, value):

        transaction_flowtype_filtered = Transaction.objects.filter(
            flow_type_id__in=value.split(',')
        ).values('activity_id')

        transaction_queryset = qs.filter(
            id__in=transaction_flowtype_filtered)

        return transaction_queryset

    flow_type = CommaSeparatedCharFilter(
        name='flow_type__code', method='flow_type_filter')

    default_flow_type = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='default_flow_type',)

    def aid_type_filter(self, qs, name, value):

        transaction_aidtype_filtered = Transaction.objects.filter(
            transactionaidtype__aid_type__code__in=value.split(',')
        ).values('activity_id')

        transaction_queryset = qs.filter(
            id__in=transaction_aidtype_filtered)

        return transaction_queryset

    aid_type = CommaSeparatedCharFilter(
        name='aid_type', method='aid_type_filter')

    default_aid_type = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='default_aid_types__aid_type__code',)

    def finance_type_filter(self, qs, name, value):

        transaction_financetype_filtered = Transaction.objects.filter(
            finance_type__code__in=value.split(',')
        ).values('activity_id')

        transaction_queryset = qs.filter(
            id__in=transaction_financetype_filtered)

        return transaction_queryset

    finance_type = CommaSeparatedCharFilter(
        name='finance_type', method='finance_type_filter')

    default_finance_type = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='default_finance_type',)

    def tied_status_filter(self, qs, name, value):

        transaction_tied_status_filtered = Transaction.objects.filter(
            tied_status_id__in=value.split(',')
        ).values('activity_id')

        transaction_queryset = qs.filter(
            id__in=transaction_tied_status_filtered)

        return transaction_queryset

    tied_status = CommaSeparatedCharFilter(
        name='tied_status', method='tied_status_filter')

    default_tied_status = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='default_tied_status',)

    budget_period_start = DateFilter(
        lookup_expr='gte',
        name='budget__period_start',)

    budget_period_end = DateFilter(
        lookup_expr='lte',
        name='budget__period_end')

    def humanitarian_filter(qs, name, value):
        activity_queryset = qs.filter(
            humanitarian=value)

        transaction_humanitarian_filtered = Transaction.objects.filter(
            humanitarian=value
        ).values('activity_id')

        transaction_queryset = qs.filter(
            id__in=transaction_humanitarian_filtered)

        # union those three queryset. Cannot use union() function because
        # result queryset cannot be apply filter again which will do in
        # later stages.
        return activity_queryset | transaction_queryset

    humanitarian = TypedChoiceFilter(
        choices=(('0', 'False'), ('1', 'True')),
        method=humanitarian_filter
    )

    # humanitarian = TypedChoiceFilter(
    # choices=(('0', 'False'), ('1', 'True')),
    # coerce=strtobool)

    humanitarian_scope_type = ToManyFilter(
        qs=HumanitarianScope,
        lookup_expr='in',
        name='type__code',
        fk='activity',
    )

    related_activity_id = ToManyFilter(
        qs=RelatedActivity,
        fk='current_activity',
        lookup_expr='in',
        name='ref_activity__normalized_iati_identifier',
    )

    related_activity_type = ToManyFilter(
        qs=RelatedActivity,
        lookup_expr='in',
        name='type__code',
        fk='current_activity',
    )

    related_activity_type_not = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='relatedactivity__type__code',
        exclude=True
    )

    related_activity_transaction_receiver_org_name = ToManyFilter(
        qs=RelatedActivity,
        lookup_expr='in',
        name='ref_activity__transaction__receiver_organisation__narratives__content',  # NOQA: E501
        fk='current_activity',
    )

    related_activity_recipient_country = ToManyFilter(
        qs=RelatedActivity,
        lookup_expr='in',
        name='ref_activity__recipient_country',
        fk='current_activity',
    )

    related_activity_recipient_region = ToManyFilter(
        qs=RelatedActivity,
        lookup_expr='in',
        name='ref_activity__recipient_region',
        fk='current_activity',
    )

    related_activity_sector = ToManyFilter(
        qs=RelatedActivity,
        lookup_expr='in',
        name='ref_activity__sector',
        fk='current_activity',
    )

    related_activity_sector_category = ToManyFilter(
        qs=RelatedActivity,
        lookup_expr='in',
        name='ref_activity__sector__category',
        fk='current_activity',
    )

    def currency_filter(self, qs, name, value):

        budget_currency_filtered = Budget.objects.filter(
            currency__code__in=value.split(',')
        ).values('activity_id')

        budget_queryset = qs.filter(id__in=budget_currency_filtered)

        transaction_currency_filtered = Transaction.objects.filter(
            currency__code__in=value.split(',')
        ).values('activity_id')

        transaction_queryset = qs.filter(
            id__in=transaction_currency_filtered)

        # union those three queryset. Cannot use union() function because
        # result queryset cannot be apply filter again which will do in
        # later stages.
        return budget_queryset | transaction_queryset

    currency = CommaSeparatedCharFilter(
        name='currency', method='currency_filter')

    budget_currency = ToManyFilter(
        qs=Budget,
        lookup_expr='in',
        name='currency__code',
        fk='activity',
    )

    def country_code_filter(self, qs, name, value):
        activity_queryset = qs.filter(
            recipient_country__code__in=value.split(',')
        )

        transaction_country_filtered = Transaction.objects.filter(
            transaction_recipient_country__in=value.split(',')
        ).values('activity_id')

        transaction_queryset = qs.filter(
            id__in=transaction_country_filtered)

        # union those three queryset. Cannot use union() function because
        # result queryset cannot be apply filter again which will do in
        # later stages.
        return activity_queryset | transaction_queryset

    recipient_country = CommaSeparatedCharFilter(
        name='country__code', method='country_code_filter')

    # recipient_country = ToManyFilter(
    # qs=ActivityRecipientCountry,
    # lookup_expr='in',
    # name='country__code',
    # fk='activity',
    # )

    recipient_country_not = ToManyNotInFilter(
        qs=ActivityRecipientCountry,
        lookup_expr='in',
        name='country__code',
        fk='activity',
    )

    def region_code_filter(self, qs, name, value):
        activity_queryset = qs.filter(
            recipient_region__code__in=value.split(','))

        transaction_region_filtered = Transaction.objects.filter(
            transaction_recipient_region__region__code__in=value.split(',')
        ).values('activity_id')

        transaction_queryset = qs.filter(
            id__in=transaction_region_filtered)

        # union those three queryset. Cannot use union() function because
        # result queryset cannot be apply filter again which will do in
        # later stages.
        return activity_queryset | transaction_queryset

    recipient_region = CommaSeparatedCharFilter(
        name='region__code', method='region_code_filter')

    # recipient_region = ToManyFilter(
    # qs=ActivityRecipientRegion,
    # lookup_expr='in',
    # name='region__code',
    # fk='activity',
    # )

    def region_category_filter(self, qs, name, value):
        activity_queryset = qs.filter(
            recipient_region__category__in=value.split(','))

        transaction_region_category_filtered = Transaction.objects.filter(
            transaction_recipient_region__category__code__in=value.split(',')
        ).values('activity_id')

        transaction_queryset = qs.filter(
            id__in=transaction_region_category_filtered)

        # union those three queryset. Cannot use union() function because
        # result queryset cannot be apply filter again which will do in
        # later stages.
        return activity_queryset | transaction_queryset

    recipient_region = CommaSeparatedCharFilter(
        name='region__code', method='region_code_filter')

    recipient_region_not = ToManyNotInFilter(
        qs=ActivityRecipientRegion,
        lookup_expr='in',
        name='region__code',
        fk='activity',
    )

    def sector_code_filter(self, queryset, name, value):
        activity_queryset = queryset.filter(
            sector__code__in=value.split(','))

        # BUDGET DOESN'T HAVE SECTOR OF ITS OWN
        # https://iatistandard.org/en/iati-standard/203/activity-standard
        # /iati-activities/iati-activity/budget/

        # budget_queryset = queryset.prefetch_related(
        #     Prefetch("budget_set",
        #              queryset=Budget.objects.prefetch_related(
        #                  Prefetch("budgetsector_set"))))\
        #     .filter(
        #         budget__budgetsector__sector__code__in=value.split(',')
        #             )

        transaction_sector_filtered = Transaction.objects.filter(
            transactionsector__sector__code__in=value.split(',')
        ).values('activity_id')

        transaction_queryset = queryset.filter(
            id__in=transaction_sector_filtered)
        # transaction_queryset = queryset.prefetch_related(
        #     Prefetch("transaction_set",
        #              queryset=Transaction.objects.prefetch_related(
        #                  Prefetch("transactionsector_set"))))\
        #     .filter(
        #         transaction__transactionsector__sector__code__in=value
        #             .split(',')).distinct('id')  # NOQA: E501

        # union those three queryset. Cannot use union() function because
        # result queryset cannot be apply filter again which will do in
        # later stages.

        return activity_queryset | transaction_queryset

    sector = CommaSeparatedCharFilter(
        name='sector', method='sector_code_filter')

    # sector = ToManyFilter(
    # qs=ActivitySector,
    # lookup_expr='in',
    # name='sector__code',
    # fk='activity',
    # )

    sector_startswith = ToManyFilter(
        qs=ActivitySector,
        lookup_expr='startswith',
        name='sector__code',
        fk='activity',
    )

    def sector_vocabulary_filter(self, qs, name, value):
        activity_queryset = qs.filter(
            sector__vocabulary__code__in=value.split(','))

        transaction_sector_vocabulary_filtered = Transaction.objects.filter(
            transactionsector__vocabulary_id__in=value.split(',')
        ).values('activity_id')

        transaction_queryset = qs.filter(
            id__in=transaction_sector_vocabulary_filtered)

        # union those three queryset. Cannot use union() function because
        # result queryset cannot be apply filter again which will do in
        # later stages.
        return activity_queryset | transaction_queryset

    sector_vocabulary = CommaSeparatedCharFilter(
        name='sector_vocabulary', method='sector_vocabulary_filter')

    # sector_vocabulary = ToManyFilter(
    # qs=ActivitySector,
    # lookup_expr='in',
    # name='vocabulary__code',
    # fk='activity',
    # )

    def sector_category_filter(self, qs, name, value):
        activity_queryset = qs.filter(
            sector__category__code__in=value.split(','))

        transaction_sector_category_filtered = Transaction.objects.filter(
            transactionsector__sector__category__code__in=value.split(',')
        ).values('activity_id')

        transaction_queryset = qs.filter(
            id__in=transaction_sector_category_filtered)

        # union those three queryset. Cannot use union() function because
        # result queryset cannot be apply filter again which will do in
        # later stages.
        return activity_queryset | transaction_queryset

    sector_category = CommaSeparatedCharFilter(
        name='sector_category', method='sector_category_filter')

    # sector_category = ToManyFilter(
    # qs=ActivitySector,
    # lookup_expr='in',
    # name='sector__category__code',
    # fk='activity',
    # )

    sector_startswith_in = StartsWithInCommaSeparatedCharFilter(
        lookup_expr='startswith',
        name='sector__code',
    )

    policy_marker = ToManyFilter(
        qs=ActivityPolicyMarker,
        lookup_expr='in',
        name='code',
        fk='activity',
    )

    participating_org = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        name='normalized_ref',
        fk='activity',
    )

    participating_org_name = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        name='primary_name',
        fk='activity',
    )

    participating_org_role = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        name='role__code',
        fk='activity',
    )

    participating_org_type = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        name='type__code',
        fk='activity',
    )

    reporting_org_identifier = ToManyFilter(
        qs=ActivityReportingOrganisation,
        lookup_expr='in',
        name='organisation__organisation_identifier',
        fk='activity',
    )

    reporting_org_type = ToManyFilter(
        qs=ActivityReportingOrganisation,
        lookup_expr='in',
        name='type',
        fk='activity'
    )

    reporting_org_identifier_startswith = ToManyFilter(
        qs=ActivityReportingOrganisation,
        lookup_expr='startswith',
        name='organisation__organisation_identifier',
        fk='activity',
    )

    result_title = ToManyFilter(
        qs=Result,
        lookup_expr='in',
        name='resulttitle__narratives__content',
        fk='activity',
    )

    indicator_title = ToManyFilter(
        qs=ResultIndicatorTitle,
        lookup_expr='in',
        name='primary_name',
        fk='result_indicator__result__activity')

    indicator_period_end_year = ToManyFilter(
        qs=ResultIndicatorPeriod,
        lookup_expr='year',
        name='period_end',
        fk='result_indicator__result__activity')

    other_identifier = ToManyFilter(
        qs=OtherIdentifier,
        lookup_expr='in',
        name='identifier',
        fk='activity',
    )

    #
    # Publisher meta filters
    #
    dataset_id = ToManyFilter(
        qs=Dataset,
        lookup_expr='in',
        name='id',
        fk='activity'
    )

    dataset_iati_id = ToManyFilter(
        qs=Dataset,
        lookup_expr='in',
        name='iati_id',
        fk='activity'
    )

    publisher_id = ToManyFilter(
        qs=Publisher,
        lookup_expr='in',
        name='id',
        fk='activity'
    )

    publisher_iati_id = ToManyFilter(
        qs=Publisher,
        lookup_expr='in',
        name='iati_id',
        fk='activity'
    )

    publisher_organisation_identifier = ToManyFilter(
        qs=Publisher,
        lookup_expr='in',
        name='publisher_iati_id',
        fk='activity'
    )

    #
    # Transaction filters
    #

    transaction_type = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        name='transaction_type',
        fk='activity',
    )

    provider_org_primary_name = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        name='provider_organisation__primary_name',
        fk='activity',
    )

    receiver_org_primary_name = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        name='receiver_organisation__primary_name',
        fk='activity',
    )

    transaction_provider_org = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        name='provider_organisation__ref',
        fk='activity',
    )

    transaction_receiver_org = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        name='receiver_organisation__ref',
        fk='activity',
    )

    transaction_provider_org_name = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        name='provider_organisation__narratives__content',
        fk='activity',
    )

    transaction_receiver_org_name = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        name='receiver_organisation__narratives__content',
        fk='activity',
    )

    transaction_provider_activity = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        name='provider_organisation__provider_activity_ref',
        fk='activity',
    )

    transaction_receiver_activity = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        name='receiver_organisation__receiver_activity_ref',
        fk='activity',
    )

    transaction_provider_activity_reporting_org = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        name='provider_organisation__provider_activity__reporting_organisations__ref',  # NOQA: E501
        fk='activity',
    )

    transaction_currency = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        name='currency',
        fk='activity',
    )

    transaction_date_year = ToManyFilter(
        qs=Transaction,
        lookup_expr='year',
        name='transaction_date',
        fk='activity'
    )

    #
    # Aggregated values filters
    #

    total_budget_lte = NumberFilter(
        lookup_expr='lte',
        name='activity_aggregation__budget_value')

    total_budget_gte = NumberFilter(
        lookup_expr='gte',
        name='activity_aggregation__budget_value')

    total_disbursement_lte = NumberFilter(
        lookup_expr='lte',
        name='activity_aggregation__disbursement_value')

    total_disbursement_gte = NumberFilter(
        lookup_expr='gte',
        name='activity_aggregation__disbursement_value')

    total_incoming_funds_lte = NumberFilter(
        lookup_expr='lte',
        name='activity_aggregation__incoming_funds_value')

    total_incoming_funds_gte = NumberFilter(
        lookup_expr='gte',
        name='activity_aggregation__incoming_funds_value')

    total_expenditure_lte = NumberFilter(
        lookup_expr='lte',
        name='activity_aggregation__expenditure_value')

    total_expenditure_gte = NumberFilter(
        lookup_expr='gte',
        name='activity_aggregation__expenditure_value')

    total_commitment_lte = NumberFilter(
        lookup_expr='lte',
        name='activity_aggregation__commitment_value')

    total_commitment_gte = NumberFilter(
        lookup_expr='gte',
        name='activity_aggregation__commitment_value')

    total_hierarchy_budget_lte = NumberFilter(
        lookup_expr='lte',
        name='activity_plus_child_aggregation__budget_value')

    total_hierarchy_budget_gte = NumberFilter(
        lookup_expr='gte',
        name='activity_plus_child_aggregation__budget_value')

    total_hierarchy_disbursement_lte = NumberFilter(
        lookup_expr='lte',
        name='activity_plus_child_aggregation__disbursement_value')

    total_hierarchy_disbursement_gte = NumberFilter(
        lookup_expr='gte',
        name='activity_plus_child_aggregation__disbursement_value')

    total_hierarchy_incoming_funds_lte = NumberFilter(
        lookup_expr='lte',
        name='activity_plus_child_aggregation__incoming_funds_value')

    total_hierarchy_incoming_funds_gte = NumberFilter(
        lookup_expr='gte',
        name='activity_plus_child_aggregation__incoming_funds_value')

    total_hierarchy_expenditure_lte = NumberFilter(
        lookup_expr='lte',
        name='activity_plus_child_aggregation__expenditure_value')

    total_hierarchy_expenditure_gte = NumberFilter(
        lookup_expr='gte',
        name='activity_plus_child_aggregation__expenditure_value')

    total_hierarchy_commitment_lte = NumberFilter(
        lookup_expr='lte',
        name='activity_plus_child_aggregation__commitment_value')

    total_hierarchy_commitment_gte = NumberFilter(
        lookup_expr='gte',
        name='activity_plus_child_aggregation__commitment_value')

    #
    # Related to publishing
    #
    def filter_ready_to_publish(self, queryset, name, value):
        return queryset.filter(Q(ready_to_publish=True))
    ready_to_publish = CharFilter(
        name='ready_to_publish', method='filter_ready_to_publish')

    def filter_modified_ready_to_publish(self, queryset, name, value):
        return queryset.filter(Q(modified=True) & Q(ready_to_publish=True))
    modified_ready_to_publish = CharFilter(
        method='filter_modified_ready_to_publish')

    def filter_modified(self, queryset, name, value):
        return queryset.filter(Q(modified=True))
    modified = CharFilter(method='filter_modified')

    def filter_published(self, queryset, name, value):
        if value == "true":
            return queryset.filter(Q(published=True))
        else:
            return queryset.filter(Q(published=False))
    published = CharFilter(method='filter_published')

    class Meta:
        model = Activity
        together_exclusive = [('budget_period_start', 'budget_period_end')]
        fields = '__all__'


class RelatedActivityFilter(FilterSet):

    related_activity_type = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='type__code')

    class Meta:
        model = RelatedActivity
        fields = '__all__'


class RelatedOrderingFilter(filters.OrderingFilter):
    """
    Extends OrderingFilter to support ordering by fields in related models
    using the Django ORM __ notation

    Also provides support for mapping of fields,
    in remove_invalid_fields a mapping is maintained
    to make 'user-friendly' names possible
    """

    def get_ordering(self, request, queryset, view):
        ordering = super(RelatedOrderingFilter, self).get_ordering(
            request, queryset, view)

        always_ordering = getattr(view, 'always_ordering', None)

        if ordering and always_ordering:
            ordering = ordering + [always_ordering]
            queryset.distinct(always_ordering)

        return ordering

    def filter_queryset(self, request, queryset, view):

        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            ordering = [order.replace("-", "") for order in ordering]

            if 'iati_identifier' not in ordering:
                queryset = queryset.distinct(*ordering)

        return super(RelatedOrderingFilter, self).filter_queryset(
            request, queryset, view)

    def is_valid_field(self, model, field):
        """
        Return true if the field exists within the model (or in the related
        model specified using the Django ORM __ notation)
        """
        components = field.split('__', 1)
        try:
            field = model._meta.get_field(components[0])

            if isinstance(field, OneToOneRel):
                return self.is_valid_field(field.related_model, components[1])

            # reverse relation
            if isinstance(field, ForeignObjectRel):
                return self.is_valid_field(field.model, components[1])

            # foreign key
            if field.remote_field and len(components) == 2:
                return self.is_valid_field(
                    field.remote_field.model, components[1]
                )
            return True
        except FieldDoesNotExist:
            return False

    def remove_invalid_fields(self, queryset, ordering, view, request):

        mapped_fields = {
            'title': 'title__narratives__content',
            'recipient_country': 'recipient_country__name',
            'activity_budget_value': 'activity_aggregation__budget_value',
            'activity_incoming_funds_value': 'activity_aggregation__incoming_funds_value',  # NOQA: E501
            'activity_commitment_value': 'activity_aggregation__commitment_value',  # NOQA: E501
            'activity_disbursement_value': 'activity_aggregation__disbursement_value',  # NOQA: E501
            'activity_expenditure_value': 'activity_aggregation__expenditure_value',  # NOQA: E501
            'activity_plus_child_budget_value': 'activity_plus_child_aggregation__budget_value',  # NOQA: E501
            'planned_start_date': 'planned_start',
            'actual_start_date': 'actual_start',
            'planned_end_date': 'planned_end',
            'actual_end_date': 'actual_end',
            'start_date': 'start_date',
            'end_date': 'end_date',
            'xml_source_ref': 'xml_source_ref'
        }

        for i, term in enumerate(ordering):
            if term.lstrip('-') in mapped_fields:
                ordering[i] = ordering[i].replace(
                    term.lstrip('-'), mapped_fields[term.lstrip('-')])

        return [term for term in ordering
                if self.is_valid_field(queryset.model, term.lstrip('-'))]


class ActivityAggregationFilter(ActivityFilter):
    """
    Activity aggregation filter class
    """

    sector_vocabulary = CommaSeparatedStickyCharFilter(
        name='sector__vocabulary__code',
        lookup_expr='in',
    )
