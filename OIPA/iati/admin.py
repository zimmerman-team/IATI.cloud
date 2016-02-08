import datetime
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from django import forms
from django.contrib.gis.geos import Point
from iati.models import *
from iati.transaction.models import *
from iati.activity_aggregation_calculation import ActivityAggregationCalculation
from autocomplete_light import forms as autocomplete_forms
import nested_admin
from exceptions import TypeError, ValueError


class NarrativeForm(autocomplete_forms.ModelForm):
    activity = forms.ModelChoiceField(Activity.objects.none(), required=False, empty_label='----')

    class Meta(object):
        model = Narrative
        fields = ('activity', 'language', 'content')

    def save(self, commit=True):
        if not self.instance.activity_id:
            self.instance.activity = self.cleaned_data['activity']
        instance = super(NarrativeForm, self).save(commit=False)
        instance.save()
        return instance


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

    extra = 1


class TransactionProviderInline(nested_admin.NestedStackedInline):
    model = TransactionProvider
    inlines = [
        NarrativeInline,
    ]
    exclude = ('normalized_ref', 'organisation', 'provider_activity_ref')

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
    exclude = ('normalized_ref', 'organisation', 'receiver_activity_ref')

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


class ActivityReportingOrganisationForm(forms.ModelForm):

    class Meta(object):
        model = ActivityReportingOrganisation
        exclude = []
        widgets = {'normalized_ref': forms.HiddenInput()}

    def clean(self):
        if self.cleaned_data['ref']:
            self.cleaned_data['normalized_ref'] = self.cleaned_data['ref']
        data = super(ActivityReportingOrganisationForm, self).clean()

        return data


class ActivityReportingOrganisationInline(nested_admin.NestedStackedInline):

    model = ActivityReportingOrganisation
    inlines = [
        NarrativeInline,
    ]
    extra = 2
    form = ActivityReportingOrganisationForm

    fields = (
        'ref',
        'type',
        'secondary_reporter',
        'normalized_ref')


class ActivityParticipatingOrganisationForm(forms.ModelForm):

    class Meta(object):
        model = ActivityParticipatingOrganisation
        exclude = []
        widgets = {
            'normalized_ref': forms.HiddenInput(),
            'primary_name': forms.HiddenInput()}

    def clean(self):
        data = super(ActivityParticipatingOrganisationForm, self).clean()
        if data['ref']:
            data['normalized_ref'] = data['ref']
        return data


class ActivityParticipatingOrganisationInline(nested_admin.NestedStackedInline):
    model = ActivityParticipatingOrganisation
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

    extra = 8


class TransactionInline(nested_admin.NestedStackedInline):
    model = Transaction

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

    extra = 8


class ActivityPolicyMarkerInline(nested_admin.NestedStackedInline):
    model = ActivityPolicyMarker
    extra = 8


class ActivityRecipientCountryInline(nested_admin.NestedStackedInline):
    model = ActivityRecipientCountry
    extra = 8

    form = autocomplete_forms.modelform_factory(ActivityRecipientCountry, fields='__all__')


class ActivitySectorInline(nested_admin.NestedStackedInline):
    model = ActivitySector
    extra = 8

    form = autocomplete_forms.modelform_factory(Sector, fields='__all__')


class ActivityRecipientRegionInline(nested_admin.NestedStackedInline):
    model = ActivityRecipientRegion
    extra = 8


class BudgetInline(nested_admin.NestedStackedInline):
    model = Budget
    exclude = ('value_string',)
    extra = 2


class DocumentCategoryInline(nested_admin.NestedStackedInline):
    model = DocumentLinkCategory
    fields = ('document_link', 'category')
    extra = 0

    form = autocomplete_forms.modelform_factory(DocumentCategory, fields='__all__')


class DocumentLinkTitleForm(autocomplete_forms.ModelForm):

    def save(self, commit=True):
        instance = super(DocumentLinkTitleForm, self).save(commit=False)
        instance.save()
        return instance


class DocumentLinkTitleInline(nested_admin.NestedStackedInline):
    model = DocumentLinkTitle
    inlines = [
        NarrativeInline,
    ]

    # form = DocumentLinkTitleForm

    extra = 1


class DocumentLinkForm(autocomplete_forms.ModelForm):
    class Meta:
        model = DocumentLink
        exclude = ['']
        widgets = {'url': forms.TextInput(attrs={'class': 'admin-charfield-more-width'})}

    def save(self, commit=True):
        instance = super(DocumentLinkForm, self).save(commit=False)
        instance.save()
        return instance


class DocumentLinkInline(nested_admin.NestedStackedInline):
    inlines = [DocumentLinkTitleInline]
    model = DocumentLink
    extra = 6

    form = DocumentLinkForm


class ResultInline(nested_admin.NestedStackedInline):
    model = Result
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


class LocationForm(forms.ModelForm):

    latitude = forms.DecimalField(
        label='latitude',
        min_value=-90,
        max_value=90,
        required=True,
    )
    longitude = forms.DecimalField(
        label='longitude',
        min_value=-180,
        max_value=180,
        required=True,
    )

    class Meta(object):
        model = Location
        exclude = []
        widgets = {'point_pos': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        if args:
            data = args[0]
            if data['latitude'] and data['longitude']:
                latitude = float(data['latitude'])
                longitude = float(data['longitude'])
                data['point_pos'] = Point(longitude, latitude)

        try:
            coordinates = kwargs['instance'].point_pos.tuple
            initial = kwargs.get('initial', {})
            initial['longitude'] = coordinates[0]
            initial['latitude'] = coordinates[1]
            kwargs['initial'] = initial
        except (KeyError, AttributeError):
            pass
        super(LocationForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(LocationForm, self).clean()
        if "latitude" in self.changed_data or "longitude" in self.changed_data:
            try:
                lat, lng = float(data.pop("latitude", None)), float(data.pop("longitude", None))
                data['point_pos'] = Point(lng, lat)
            except (TypeError, ValueError):
                data['point_pos'] = None

        if not (data.get("point_pos") or data.get("latitude")):
            raise forms.ValidationError({"point_pos": "Coordinates is required"})
        return data


class LocationInline(nested_admin.NestedStackedInline):
    model = Location
    extra = 6

    form = LocationForm

    fields = (
        'ref',
        'latitude',
        'longitude',
        'location_id_code',
        'point_srs_name',
        'point_pos')


class RelatedActivityForm(autocomplete_forms.ModelForm):

    class Meta(object):
        model = RelatedActivity
        exclude = []
        widgets = {'ref': forms.HiddenInput()}


    def clean(self):
        data = super(RelatedActivityForm, self).clean()
        if data['ref_activity']:
            data['ref'] = data['ref_activity'].id
        return data


class RelatedActivityInline(nested_admin.NestedStackedInline):
    model = RelatedActivity
    fk_name = 'current_activity'
    extra = 3
    form = RelatedActivityForm


class DescriptionInline(nested_admin.NestedStackedInline):
    model = Description
    extra = 4
    inlines = [NarrativeInline, ]


class TitleInline(nested_admin.NestedStackedInline):
    model = Title
    extra = 2
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

        if not change:
            obj.default_lang = 'en'

            title = Title()
            title.activity = obj
            title.save()

            description = Description()
            description.activity = obj
            description.save()

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
            po = formset.instance
            if po.narratives.all().count() > 0:
                po.primary_name = po.narratives.all()[0].content.strip()
                po.save()

        # update aggregations after save of last inline form
        if formset.model == Transaction:
            aggregation_calculator = ActivityAggregationCalculation()
            aggregation_calculator.parse_activity_aggregations(form.instance)


class TransactionAdmin(nested_admin.NestedAdmin):
    search_fields = ['activity__id']
    readonly_fields = ['activity']
    list_display = ['__unicode__']
    exclude = ('value_string',)
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

        # ugly workaround to get narratives in on edit
        if not getattr(obj, 'description', None):
            description = TransactionDescription()
            description.transaction = obj
            description.save()
            obj.description = description

        if not getattr(obj, 'receiver_organisation', None):
            transaction_receiver = TransactionReceiver()
            transaction_receiver.transaction = obj
            transaction_receiver.save()
            obj.receiver_organisation = transaction_receiver

        if not getattr(obj, 'provider_organisation', None):
            transaction_provider = TransactionProvider()
            transaction_provider.transaction = obj
            transaction_provider.save()
            obj.provider_organisation = transaction_provider

        self.act = obj.activity

        return obj

    def save_formset(self, request, form, formset, change):
        if formset.model == Narrative:
            for entry in formset.cleaned_data:
                if entry and entry['id'] is None:
                    entry['activity'] = self.act
        super(TransactionAdmin, self).save_formset(request, form, formset, change)

        # update aggregations after save of last inline form
        if formset.model == TransactionReceiver:
            aggregation_calculator = ActivityAggregationCalculation()
            aggregation_calculator.parse_activity_aggregations(form.instance.activity)


class ResultIndicatorTitleInline(nested_admin.NestedStackedInline):
    model = ResultIndicatorTitle
    inlines = [
        NarrativeInline,
    ]

    extra = 1


class ResultIndicatorBaselineCommentInline(nested_admin.NestedStackedInline):
    model = ResultIndicatorBaselineComment
    inlines = [
        NarrativeInline,
    ]

    extra = 1


class ResultIndicatorPeriodInline(nested_admin.NestedStackedInline):
    model = ResultIndicatorPeriod

    extra = 4


class ResultIndicatorInline(nested_admin.NestedStackedInline):
    model = ResultIndicator
    inlines = [
        ResultIndicatorTitleInline,
        ResultIndicatorPeriodInline,
    ]

    extra = 4


class ResultTitleInline(nested_admin.NestedStackedInline):
    model = ResultTitle
    inlines = [
        NarrativeInline,
    ]

    extra = 1


class ResultDescriptionInline(nested_admin.NestedStackedInline):
    model = ResultDescription
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

        # ugly workaround to get narratives in on change
        if not getattr(obj, 'resultdescription', None):
            description = ResultDescription()
            description.result = obj
            description.save()
            obj.resultdescription = description

        if not getattr(obj, 'resulttitle', None):
            title = ResultTitle()
            title.result = obj
            title.save()
            obj.resulttitle = title

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

        # ugly workaround to get narratives in on add
        if not change:
            title = ResultTitle()
            title.result = obj
            title.save()

            description = ResultDescription()
            description.result = obj
            description.save()

        self.act = obj.activity

    def save_formset(self, request, form, formset, change):
        if formset.model == Narrative:
            for entry in formset.cleaned_data:
                if entry and entry['id'] is None:
                    entry['activity'] = self.act
        super(ResultAdmin, self).save_formset(request, form, formset, change)


admin.site.register(Activity, ActivityAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Narrative)
