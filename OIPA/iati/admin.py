import datetime

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.functional import curry
from django.utils.html import format_html
from django import forms
from django.forms import CharField
from django.contrib.gis.geos import Point

from nested_inline.admin import NestedModelAdmin, NestedInline

from iati.models import *
from iati.transaction.models import *
from iati.activity_aggregation_calculation import ActivityAggregationCalculation


class ExtraNestedModelAdmin(NestedModelAdmin):
    def get_inline_instances(self, request, obj=None):
        inline_instances = super(ExtraNestedModelAdmin, self).get_inline_instances(request, obj)
        for inline_instance in inline_instances:
            inline_instance.parent_instance = obj

        return inline_instances


class ExtraNestedInline(NestedInline):
    def get_inline_instances(self, request, obj=None):
        inline_instances = super(ExtraNestedInline, self).get_inline_instances(request, obj)
        for inline_instance in inline_instances:
            inline_instance.parent_instance = self.parent_instance
            inline_instance.direct_parent = obj

        return inline_instances


# TODO: remove django-grappelli-inline dependency by moving these templates to local repo - 2015-12-01
class NestedStackedInline(ExtraNestedInline):
    template = 'admin/edit_inline/stacked.html'
    # template = 'admin/edit_inline/stacked-nested.html'


class NestedTabularInline(ExtraNestedInline):
    # template = 'admin/edit_inline/tabular.html'
    template = 'admin/edit_inline/tabular-nested.html'


class NarrativeInline(GenericTabularInline):

    model = Narrative
    ct_field = "related_content_type"
    ct_fk_field = "related_object_id"
    inlines = []
    fields = ('activity', 'language', 'content')
    raw_id_fields = ('activity',)
    # form = NarrativeForm

    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        activity = self.parent_instance
        
        if isinstance(self.parent_instance, Transaction):
            activity = self.parent_instance.activity

        if isinstance(self.parent_instance, Result):
            activity = self.parent_instance.activity

        initial = [{'activity': activity} for i in range(self.extra)]
        formset = super(NarrativeInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['code', 'name']
    list_display = ['code', 'abbreviation', 'name', 'type', 'total_activities']


class TransactionDescriptionInline(NestedTabularInline):
    model = TransactionDescription
    inlines = [
        NarrativeInline,
    ]

    extra = 0


class TransactionProviderInline(NestedTabularInline):
    model = TransactionProvider
    inlines = [
        NarrativeInline,
    ]
    exclude = ('normalized_ref', 'organisation', 'provider_activity_ref')

    raw_id_fields = ('provider_activity',)

    autocomplete_lookup_fields = {
        'fk': ['provider_activity'],
    }

    extra = 0

    def save_model(self, request, obj, form, change):
        obj.normalized_ref = obj.ref
        if obj.provider_activity:
            obj.provider_activity_ref = obj.provider_activity.id
        return super(TransactionProviderInline, self).save_model(request, obj, form, change)


class TransactionReceiverInline(NestedTabularInline):
    model = TransactionReceiver
    inlines = [
        NarrativeInline,
    ]
    exclude = ('normalized_ref', 'organisation', 'receiver_activity_ref')

    raw_id_fields = ('receiver_activity',)

    autocomplete_lookup_fields = {
        'fk': ['receiver_activity'],
    }

    extra = 0

    def save_model(self, request, obj, form, change):
        obj.normalized_ref = obj.ref
        if obj.receiver_activity:
            obj.receiver_activity_ref = obj.receiver_activity.id
        return super(TransactionReceiverInline, self).save_model(request, obj, form, change)


class ActivityDateInline(NestedTabularInline):
    model = ActivityDate
    extra = 0


class ActivityReportingOrganisationForm(forms.ModelForm):

    class Meta(object):
        model = RelatedActivity
        exclude = []
        widgets = {'normalized_ref': forms.HiddenInput()}

    def clean(self):
        data = super(ActivityReportingOrganisationForm, self).clean()
        if data['ref']:
            data['normalized_ref'] = data['ref']
        return data


class ActivityReportingOrganisationInline(NestedTabularInline):
    model = ActivityReportingOrganisation
    inlines = [
        NarrativeInline,
    ]
    extra = 0
    form = ActivityReportingOrganisationForm

    fields = (
        'ref',
        'organisation',
        'type',
        'secondary_reporter',
        'normalized_ref')


class ActivityParticipatingOrganisationForm(forms.ModelForm):

    class Meta(object):
        model = RelatedActivity
        exclude = []
        widgets = {
            'normalized_ref': forms.HiddenInput(),
            'primary_name': forms.HiddenInput()}

    def clean(self):
        data = super(ActivityParticipatingOrganisationForm, self).clean()
        if data['ref']:
            data['normalized_ref'] = data['ref']
        return data


class ActivityParticipatingOrganisationInline(NestedTabularInline):
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

    extra = 1


class TransactionInline(NestedTabularInline):
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

    extra = 0


class ActivityPolicyMarkerInline(NestedTabularInline):
    model = ActivityPolicyMarker
    extra = 0


class ActivityRecipientCountryInline(NestedTabularInline):
    model = ActivityRecipientCountry
    extra = 0

    raw_id_fields = ('country',)

    autocomplete_lookup_fields = {
        'fk': ['country'],
    }


class ActivitySectorInline(NestedTabularInline):
    model = ActivitySector
    extra = 0

    raw_id_fields = ('sector',)

    autocomplete_lookup_fields = {
        'fk': ['sector'],
    }


class ActivityRecipientRegionInline(NestedTabularInline):
    model = ActivityRecipientRegion
    extra = 0


class BudgetInline(NestedTabularInline):
    model = Budget
    exclude = ('value_string',)
    extra = 0


class CategoriesInline(NestedTabularInline):
    model = DocumentLinkCategory

    extra = 0

    raw_id_fields = ('category',)

    related_lookup_fields = {
        'fk': ['category'],
    }


class DocumentLinkForm(forms.ModelForm):
    url = CharField(label='url', max_length=500)

    class Meta:
        model = DocumentLink
        exclude = ['']


class DocumentLinkInline(NestedTabularInline):
    inlines = [CategoriesInline, ]
    model = DocumentLink
    extra = 0

    form = DocumentLinkForm

    raw_id_fields = ('file_format',)

    related_lookup_fields = {
        'fk': ['file_format'],
    }


class ResultInline(NestedTabularInline):
    model = Result
    extra = 0

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
        if args:    # If args exist
            data = args[0]
            if data['latitude'] and data['longitude']:    #If lat/lng exist
                latitude = float(data['latitude'])
                longitude = float(data['longitude'])
                data['point_pos'] = Point(longitude, latitude)    # Set PointField
        try:
            coordinates = kwargs['instance'].point_pos.tuple    #If PointField exists
            initial = kwargs.get('initial', {})
            initial['longitude'] = coordinates[0]    #Set Latitude from coordinates
            initial['latitude'] = coordinates[1]    #Set Longitude from coordinates
            kwargs['initial'] = initial
        except (KeyError, AttributeError):
            pass
        super(LocationForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(LocationForm, self).clean()
        if "latitude" in self.changed_data or "longitude" in self.changed_data:
            lat, lng = float(data.pop("latitude", None)), float(data.pop("longitude", None))
            data["point_pos"] = Point(lng, lat)

        if not (data.get("point_pos") or data.get("latitude")):
            raise forms.ValidationError({"point_pos": "Coordinates is required"})
        return data


class LocationInline(NestedTabularInline):
    model = Location
    extra = 0

    form = LocationForm


    fields = (
        'ref',
        'latitude',
        'longitude',
        'location_id_code',
        'point_srs_name',
        'point_pos')


class RelatedActivityForm(forms.ModelForm):

    class Meta(object):
        model = RelatedActivity
        exclude = []
        widgets = {'ref': forms.HiddenInput()}


    def clean(self):
        data = super(RelatedActivityForm, self).clean()
        if data['ref_activity']:
            data['ref'] = data['ref_activity'].id
        return data


class RelatedActivityInline(NestedTabularInline):
    model = RelatedActivity
    fk_name = 'current_activity'
    extra = 0
    form = RelatedActivityForm

    raw_id_fields = ('ref_activity',)

    autocomplete_lookup_fields = {
        'fk': ['ref_activity'],
    }


class DescriptionInline(NestedTabularInline):
    model = Description
    extra = 1
    inlines = [NarrativeInline, ]


class TitleInline(NestedTabularInline):
    model = Title
    extra = 0
    inlines = [NarrativeInline, ]


class ActivityAdmin(ExtraNestedModelAdmin):
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

    def save_formset(self, request, form, formset, change):
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
        if isinstance(form, ActivityParticipatingOrganisationForm) and formset.model == Narrative:
            po = form.instance
            po.primary_name = po.narratives.all()[0].content
            po.save()

        # update aggregations after save of last inline form
        if formset.model == Transaction:
            aggregation_calculator = ActivityAggregationCalculation()
            aggregation_calculator.parse_activity_aggregations(form.instance)


class TransactionAdmin(ExtraNestedModelAdmin):
    search_fields = ['activity__id']
    readonly_fields = ['activity']
    list_display = ['__unicode__']
    exclude = ('value_string',)
    inlines = [
        TransactionDescriptionInline,
        TransactionProviderInline,
        TransactionReceiverInline,
    ]

    raw_id_fields = ('activity', 'recipient_country')

    autocomplete_lookup_fields = {
        'fk': ['activity', 'recipient_country'],

    }

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

        return obj

    def save_model(self, request, obj, form, change):

        super(TransactionAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        super(TransactionAdmin, self).save_formset(request, form, formset, change)

        # update aggregations after save of last inline form
        if formset.model == TransactionReceiver:
            aggregation_calculator = ActivityAggregationCalculation()
            aggregation_calculator.parse_activity_aggregations(form.instance.activity)


class ResultIndicatorTitleInline(NestedTabularInline):
    model = ResultIndicatorTitle
    inlines = [
        NarrativeInline,
    ]

    extra = 1


class ResultIndicatorBaselineCommentInline(NestedTabularInline):
    model = ResultIndicatorBaselineComment
    inlines = [
        NarrativeInline,
    ]

    extra = 0


class ResultIndicatorPeriodInline(NestedTabularInline):
    model = ResultIndicatorPeriod

    extra = 1


class ResultIndicatorInline(NestedTabularInline):
    model = ResultIndicator
    inlines = [
        ResultIndicatorTitleInline,
        ResultIndicatorPeriodInline,
    ]

    extra = 0


class ResultTitleInline(NestedTabularInline):
    model = ResultTitle
    inlines = [
        NarrativeInline,
    ]

    extra = 0


class ResultDescriptionInline(NestedTabularInline):
    model = ResultDescription
    inlines = [
        NarrativeInline,
    ]

    extra = 0


class ResultAdmin(ExtraNestedModelAdmin):
    search_fields = ['activity__id']
    readonly_fields = ['activity']
    list_display = ['__unicode__']
    inlines = [
        ResultTitleInline,
        ResultDescriptionInline,
        ResultIndicatorInline,
    ]

    raw_id_fields = ('activity',)

    autocomplete_lookup_fields = {
        'fk': ['activity'],

    }

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


admin.site.register(Activity, ActivityAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Narrative)
