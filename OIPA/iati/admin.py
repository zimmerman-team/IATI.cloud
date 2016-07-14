import datetime

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from django.core.exceptions import ObjectDoesNotExist

from autocomplete_light import forms as autocomplete_forms
import nested_admin

from iati.forms import NarrativeForm
from iati.forms import ActivityReportingOrganisationForm
from iati.forms import ActivityParticipatingOrganisationForm
from iati.forms import DocumentLinkTitleForm

from iati.forms import DocumentLinkForm
from iati.forms import LocationForm
from iati.forms import RelatedActivityForm
from iati.models import *
from iati.transaction.models import *
from iati.activity_aggregation_calculation import ActivityAggregationCalculation

from iati.parser import post_save


class NarrativeInline(GenericTabularInline):

    model = Narrative
    ct_field = "related_content_type"
    ct_fk_field = "related_object_id"
    inlines = []
    fields = ('activity', 'language', 'content')
    form = NarrativeForm

    extra = 1


class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['code', 'name']
    list_display = ['code', 'abbreviation', 'name', 'type', 'total_activities']


class TransactionDescriptionInline(nested_admin.NestedStackedInline):
    model = TransactionDescription
    inlines = [
        NarrativeInline,
    ]
    classes = ('collapse open',)
    inline_classes = ('collapse open',)

    extra = 1


class TransactionProviderInline(nested_admin.NestedStackedInline):
    model = TransactionProvider
    inlines = [
        NarrativeInline,
    ]
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    exclude = ('normalized_ref', 'organisation', 'provider_activity', 'primary_name')

    form = autocomplete_forms.modelform_factory(TransactionProvider, fields='__all__')
    extra = 1

    def save_model(self, request, obj, form, change):
        obj.normalized_ref = obj.ref
        if obj.provider_activity:
            obj.provider_activity_ref = obj.provider_activity.id
        return super(TransactionProviderInline, self).save_model(request, obj, form, change)


class TransactionReceiverInline(nested_admin.NestedStackedInline):
    model = TransactionReceiver
    inlines = [
        NarrativeInline,
    ]
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    exclude = ('normalized_ref', 'organisation', 'receiver_activity', 'primary_name')

    form = autocomplete_forms.modelform_factory(TransactionReceiver, fields='__all__')

    extra = 1

    def save_model(self, request, obj, form, change):
        obj.normalized_ref = obj.ref
        if obj.receiver_activity:
            obj.receiver_activity_ref = obj.receiver_activity.id
        return super(TransactionReceiverInline, self).save_model(request, obj, form, change)


class ActivityDateInline(nested_admin.NestedStackedInline):
    model = ActivityDate
    extra = 4
    classes = ('collapse open',)
    inline_classes = ('collapse open',)


class ActivityReportingOrganisationInline(nested_admin.NestedStackedInline):

    model = ActivityReportingOrganisation
    inlines = [
        NarrativeInline,
    ]
    extra = 1
    form = ActivityReportingOrganisationForm
    classes = ('collapse open',)
    inline_classes = ('collapse open',)

    fields = (
        'ref',
        'type',
        'secondary_reporter',
        'normalized_ref')


class ActivityParticipatingOrganisationInline(nested_admin.NestedStackedInline):
    model = ActivityParticipatingOrganisation
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    inlines = [
        NarrativeInline,
    ]
    form = ActivityParticipatingOrganisationForm
    fields = (
        'ref',
        'type',
        'role',
        'normalized_ref',
        'primary_name')

    extra = 6


class TransactionInline(nested_admin.NestedStackedInline):
    model = Transaction
    classes = ('collapse open',)
    inline_classes = ('collapse open',)

    fields = (
        'transaction_type',
        'value',
        'currency',
        'value_date',
        'transaction_date',
        'transaction_provider',
        'transaction_receiver',
        'edit_transaction',)
    readonly_fields = ('edit_transaction', 'transaction_provider', 'transaction_receiver')

    form = autocomplete_forms.modelform_factory(Transaction, fields='__all__')

    def transaction_provider(self, obj):
        try:
            return obj.provider_organisation.narratives.all()[0].content
        except Exception as e:
            return 'no provider name'

    def transaction_receiver(self, obj):
        try:
            return obj.receiver_organisation.narratives.all()[0].content
        except Exception as e:
            return 'no receiver name'

    def edit_transaction(self, obj):

        if obj.id:
            return format_html(
                '<a href="/admin/iati/transaction/{}/" onclick="return showAddAnotherPopup(this);">Edit details</a>',
                str(obj.id))
        else:
            return format_html(
                'Please save the activity to edit receiver/provider details')

    extra = 6


class ActivityPolicyMarkerInline(nested_admin.NestedStackedInline):
    model = ActivityPolicyMarker
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    extra = 4


class ActivityRecipientCountryInline(nested_admin.NestedStackedInline):
    model = ActivityRecipientCountry
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    extra = 6

    form = autocomplete_forms.modelform_factory(ActivityRecipientCountry, fields='__all__')


class ActivitySectorInline(nested_admin.NestedStackedInline):
    model = ActivitySector
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    extra = 6

    form = autocomplete_forms.modelform_factory(Sector, fields='__all__')


class ActivityRecipientRegionInline(nested_admin.NestedStackedInline):
    model = ActivityRecipientRegion
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    extra = 4


class BudgetInline(nested_admin.NestedStackedInline):
    model = Budget
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    exclude = (
        'value_string',
        'xdr_value',
        'usd_value',
        'eur_value',
        'gbp_value',
        'jpy_value',
        'cad_value',)
    extra = 2


class DocumentCategoryInline(nested_admin.NestedStackedInline):
    model = DocumentLinkCategory
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    fields = ('document_link', 'category')
    extra = 1

    form = autocomplete_forms.modelform_factory(DocumentCategory, fields='__all__')


class DocumentLinkTitleInline(nested_admin.NestedStackedInline):
    model = DocumentLinkTitle
    classes = ('collapse open',)
    inline_classes = ('collapse open',)

    inlines = [
        NarrativeInline,
    ]

    # form = DocumentLinkTitleForm

    extra = 1


class DocumentLinkInline(nested_admin.NestedStackedInline):
    inlines = [DocumentLinkTitleInline, DocumentCategoryInline]
    model = DocumentLink
    # classes = ('collapse open',)
    # inline_classes = ('collapse open',)
    extra = 4

    form = DocumentLinkForm


class ResultInline(nested_admin.NestedStackedInline):
    model = Result
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    extra = 6

    fields = ('read_title', 'type', 'aggregation_status', 'read_description', 'edit_result',)
    readonly_fields = ('read_title', 'read_description', 'edit_result',)

    def read_title(self, obj):
        try:
            return obj.title.narratives.all()[0].content
        except Exception as e:
            return 'no title given'

    def read_description(self, obj):
        try:
            return obj.title.narratives.all()[0].content
        except Exception as e:
            return 'no title given'

    def edit_result(self, obj):

        if obj.id:
            return format_html(
                '<a href="/admin/iati/result/{}/" onclick="return showAddAnotherPopup(this);">Edit</a>',
                str(obj.id))
        else:
            return format_html(
                'Please save the activity to edit result details and to add indicator periods')


class LocationInline(nested_admin.NestedStackedInline):
    model = Location
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    extra = 4

    form = LocationForm

    fields = (
        'ref',
        'latitude',
        'longitude',
        'location_id_code',
        'point_srs_name',
        'point_pos')


class RelatedActivityInline(nested_admin.NestedStackedInline):
    model = RelatedActivity
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    fk_name = 'current_activity'
    extra = 3
    form = RelatedActivityForm


class DescriptionInline(nested_admin.NestedStackedInline):
    model = Description
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    extra = 4
    inlines = [NarrativeInline, ]


class TitleInline(nested_admin.NestedStackedInline):
    model = Title
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    extra = 1
    inlines = [NarrativeInline, ]


class ActivityAdmin(nested_admin.NestedAdmin):
    search_fields = ['id']
    exclude = (
        'activity_aggregations',
        'planned_start',
        'actual_start',
        'start_date',
        'planned_end',
        'actual_end',
        'end_date',
        'is_searchable',
        'default_lang')
    list_display = ['__unicode__']
    inlines = [
        ActivityDateInline,
        ActivityReportingOrganisationInline,
        ActivityParticipatingOrganisationInline,
        ActivityPolicyMarkerInline,
        ActivityRecipientCountryInline,
        ActivitySectorInline,
        ActivityRecipientRegionInline,
        BudgetInline,
        TitleInline,
        DescriptionInline,
        DocumentLinkInline,
        ResultInline,
        LocationInline,
        RelatedActivityInline,
        TransactionInline,
    ]

    form = autocomplete_forms.modelform_factory(Activity, fields='__all__')

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []

        inline_instances = super(ActivityAdmin, self).get_inline_instances(request, obj)

        return inline_instances

    def save_model(self, request, obj, form, change):
        obj.last_updated_datetime = datetime.datetime.now()

        super(ActivityAdmin, self).save_model(request, obj, form, change)

        try:
            if obj.title.id is None:
                obj.title.save()
        except ObjectDoesNotExist:
            title = Title()
            title.activity = obj
            title.save()

        if not obj.description_set.count():
            description = Description()
            description.activity = obj
            description.save()

        if not change:
            obj.default_lang = 'en'

        self.act = obj

    def save_formset(self, request, form, formset, change):
        if formset.model == Narrative:
            for entry in formset.cleaned_data:
                if entry and entry['id'] is None:
                    if isinstance(formset.instance, DocumentLinkTitle):
                        formset.instance.document_link_id = formset.instance.document_link.id
                        formset.instance.save()
                    entry['activity'] = self.act

        super(ActivityAdmin, self).save_formset(request, form, formset, change)

        # set derived activity dates (used for sorting)
        if formset.model == ActivityDate:

            activity = form.instance
            for ad in activity.activitydate_set.all():
                if ad.type.code == '1':
                    activity.planned_start = ad.iso_date
                if ad.type.code == '2':
                    activity.actual_start = ad.iso_date
                if ad.type.code == '3':
                    activity.planned_end = ad.iso_date
                if ad.type.code == '4':
                    activity.actual_end = ad.iso_date

            if activity.actual_start:
                activity.start_date = activity.actual_start
            else:
                activity.start_date = activity.planned_start

            if activity.actual_end:
                activity.end_date = activity.actual_end
            else:
                activity.end_date = activity.planned_end
            activity.save()

        # save primary name on participating organisation to make querying work
        if isinstance(formset.instance, ActivityParticipatingOrganisation):
            if formset.cleaned_data[0]:
                po = formset.instance
                if po.narratives.all().count() > 0:
                    po.primary_name = po.narratives.all()[0].content.strip()
                    po.save()

        # update aggregations after save of last inline form
        if formset.model == Transaction:
            aggregation_calculator = ActivityAggregationCalculation()
            aggregation_calculator.parse_activity_aggregations(form.instance)

    def save_related(self, request, form, formsets, change):
        super(ActivityAdmin, self).save_related(request, form, formsets, change)
        post_save.set_derived_activity_dates(self.act)
        post_save.set_activity_aggregations(self.act)
        post_save.update_activity_search_index(self.act)

        # remove old
        BudgetSector.objects.filter(budget__activity=self.act).delete()
        TransactionSector.objects.filter(transaction__activity=self.act).delete()
        TransactionRecipientCountry.objects.filter(transaction__activity=self.act).delete()
        TransactionRecipientRegion.objects.filter(transaction__activity=self.act).delete()

        # add new
        post_save.set_country_region_transaction(self.act)
        post_save.set_sector_transaction(self.act)
        post_save.set_sector_budget(self.act)


class TransactionAdmin(nested_admin.NestedAdmin):
    search_fields = ['activity__id']
    readonly_fields = ['activity']
    list_display = ['__unicode__']
    exclude = (
        'value_string',
        'xdr_value',
        'usd_value',
        'eur_value',
        'gbp_value',
        'jpy_value',
        'cad_value',)
    inlines = [
        TransactionDescriptionInline,
        TransactionProviderInline,
        TransactionReceiverInline,
    ]

    form = autocomplete_forms.modelform_factory(Transaction, fields='__all__')

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []

        inline_instances = super(TransactionAdmin, self).get_inline_instances(request, obj)

        return inline_instances

    def get_object(self, request, object_id, from_field=None):
        obj = super(TransactionAdmin, self).get_object(request, object_id)

        # if not getattr(obj, 'receiver_organisation', None):
        #     transaction_receiver = TransactionReceiver()
        #     transaction_receiver.transaction = obj
        #     transaction_receiver.save()
        #     obj.receiver_organisation = transaction_receiver
        #
        # if not getattr(obj, 'provider_organisation', None):
        #     transaction_provider = TransactionProvider()
        #     transaction_provider.transaction = obj
        #     transaction_provider.save()
        #     obj.provider_organisation = transaction_provider

        self.act = obj.activity

        return obj

    def save_formset(self, request, form, formset, change):
        if formset.model == Narrative:
            for entry in formset.cleaned_data:
                if entry and entry['id'] is None:
                    entry['activity'] = self.act

        super(TransactionAdmin, self).save_formset(request, form, formset, change)

        if formset.model == TransactionDescription:
            try:
                if formset.instance.description.id is None:
                    formset.instance.description.save()
            except ObjectDoesNotExist:
                pass

        if formset.model == TransactionProvider:
            try:
                if formset.instance.provider_organisation.id is None:
                    formset.instance.provider_organisation.save()
            except ObjectDoesNotExist:
                pass

        if isinstance(formset.instance, TransactionProvider):
            if formset.cleaned_data[0]:
                tp = formset.instance
                if tp.narratives.all().count() > 0:
                    tp.primary_name = tp.narratives.all()[0].content.strip()
                    tp.save()

        if isinstance(formset.instance, TransactionReceiver):
            if formset.cleaned_data[0]:
                tr = formset.instance
                if tr.narratives.all().count() > 0:
                    tr.primary_name = tr.narratives.all()[0].content.strip()
                    tr.save()

        # update aggregations after save of last inline form
        if formset.model == TransactionReceiver:
            try:
                if formset.instance.receiver_organisation.id is None:
                    formset.instance.receiver_organisation.save()
            except ObjectDoesNotExist:
                pass

            aggregation_calculator = ActivityAggregationCalculation()
            aggregation_calculator.parse_activity_aggregations(form.instance.activity)

    def save_related(self, request, form, formsets, change):
        super(TransactionAdmin, self).save_related(request, form, formsets, change)

        # remove old
        TransactionSector.objects.filter(transaction__activity=self.act).delete()
        TransactionRecipientCountry.objects.filter(transaction__activity=self.act).delete()
        TransactionRecipientRegion.objects.filter(transaction__activity=self.act).delete()

        # add new
        post_save.set_transaction_provider_receiver_activity(self.act)
        post_save.set_activity_aggregations(self.act)
        post_save.set_country_region_transaction(self.act)
        post_save.set_sector_transaction(self.act)


class ResultIndicatorTitleInline(nested_admin.NestedStackedInline):
    model = ResultIndicatorTitle
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    inlines = [
        NarrativeInline,
    ]
    exclude = (
        'primary_name',
    )

    extra = 1


class ResultIndicatorDescriptionInline(nested_admin.NestedStackedInline):
    model = ResultIndicatorDescription
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    inlines = [
        NarrativeInline,
    ]

    extra = 1


class ResultIndicatorBaselineCommentInline(nested_admin.NestedStackedInline):
    model = ResultIndicatorBaselineComment
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    inlines = [
        NarrativeInline,
    ]

    extra = 1

class ResultIndicatorPeriodTargetCommentInline(nested_admin.NestedStackedInline):
    model = ResultIndicatorPeriodTargetComment
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    inlines = [
        NarrativeInline,
    ]

    extra = 1

class ResultIndicatorPeriodActualCommentInline(nested_admin.NestedStackedInline):
    model = ResultIndicatorPeriodActualComment
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    inlines = [
        NarrativeInline,
    ]

    extra = 1


class ResultIndicatorPeriodInline(nested_admin.NestedStackedInline):
    model = ResultIndicatorPeriod
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    inlines = [
        ResultIndicatorPeriodTargetCommentInline,
        ResultIndicatorPeriodActualCommentInline,
    ]
    extra = 4


class ResultIndicatorInline(nested_admin.NestedStackedInline):
    model = ResultIndicator
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    inlines = [
        ResultIndicatorTitleInline,
        ResultIndicatorDescriptionInline,
        ResultIndicatorBaselineCommentInline,
        ResultIndicatorPeriodInline,
    ]

    extra = 4


class ResultTitleInline(nested_admin.NestedStackedInline):
    model = ResultTitle
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    inlines = [
        NarrativeInline,
    ]

    extra = 1


class ResultDescriptionInline(nested_admin.NestedStackedInline):
    model = ResultDescription
    classes = ('collapse open',)
    inline_classes = ('collapse open',)
    inlines = [
        NarrativeInline,
    ]

    extra = 1


class ResultAdmin(nested_admin.NestedAdmin):
    search_fields = ['activity__id']
    readonly_fields = ['activity']
    list_display = ['__unicode__']
    inlines = [
        ResultTitleInline,
        ResultDescriptionInline,
        ResultIndicatorInline,
    ]

    form = autocomplete_forms.modelform_factory(Result, fields='__all__')

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []

        inline_instances = super(ResultAdmin, self).get_inline_instances(request, obj)

        return inline_instances

    def get_object(self, request, object_id, from_field=None):
        obj = super(ResultAdmin, self).get_object(request, object_id)

        if not obj.resultindicator_set.count():
            result_indicator = ResultIndicator()
            result_indicator.result = obj
            result_indicator.save()

        for result_indicator in obj.resultindicator_set.all():
            if not getattr(result_indicator, 'resultindicatortitle', None):
                title = ResultIndicatorTitle()
                title.result_indicator = result_indicator
                title.save()
                result_indicator.resultindicatortitle = title

        return obj

    def save_model(self, request, obj, form, change):
        super(ResultAdmin, self).save_model(request, obj, form, change)
        self.act = obj.activity

    def save_formset(self, request, form, formset, change):
        if formset.model == Narrative:
            for entry in formset.cleaned_data:
                if entry and entry['id'] is None:
                    entry['activity'] = self.act
        super(ResultAdmin, self).save_formset(request, form, formset, change)

        if formset.model == ResultTitle:
            try:
                if formset.instance.resulttitle.id is None:
                    formset.instance.resulttitle.save()
            except ObjectDoesNotExist:
                pass

        if formset.model == ResultDescription:
            try:
                if formset.instance.resultdescription.id is None:
                    formset.instance.resultdescription.save()
            except ObjectDoesNotExist:
                pass

        if formset.model == ResultIndicatorPeriodActualComment:
            try:
                if formset.instance.resultindicatorperiodactualcomment.id is None:
                    if formset.instance.resultindicatorperiodactualcomment.result_indicator_period_id is None:
                        formset.instance.resultindicatorperiodactualcomment.result_indicator_period_id = formset.instance.resultindicatorperiodactualcomment.result_indicator_period.id
                    formset.instance.resultindicatorperiodactualcomment.save()
            except ObjectDoesNotExist:
                pass

        if formset.model == ResultIndicatorPeriodTargetComment:
            try:
                if formset.instance.resultindicatorperiodtargetcomment.id is None:
                    if formset.instance.resultindicatorperiodtargetcomment.result_indicator_period_id is None:
                        formset.instance.resultindicatorperiodtargetcomment.result_indicator_period_id = formset.instance.resultindicatorperiodtargetcomment.result_indicator_period.id
                    formset.instance.resultindicatorperiodtargetcomment.save()
            except ObjectDoesNotExist:
                pass

        # save primary name on result indicator title to make aggregations work
        if isinstance(formset.instance, ResultIndicatorTitle):
            if formset.cleaned_data[0]:
                rit = formset.instance
                if rit.narratives.all().count() > 0:
                    rit.primary_name = rit.narratives.all()[0].content.strip()
                    rit.save()

        if formset.model == ResultIndicatorDescription:
            try:
                if formset.instance.resultindicatordescription.id is None:
                    if formset.instance.id is None:
                        formset.instance.save()
                        formset.instance.resultindicatordescription.result_indicator = formset.instance
                    formset.instance.resultindicatordescription.save()
            except ObjectDoesNotExist:
                pass


admin.site.register(Activity, ActivityAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Narrative)
