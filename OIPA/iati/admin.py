from django.contrib import admin
from iati.models import *
from django import forms
from iati.transaction.models import *
from django.contrib.contenttypes.admin import GenericTabularInline
from nested_inline.admin import NestedStackedInline, NestedTabularInline, NestedModelAdmin, NestedInline
from django.utils.functional import curry

# Avoid giant delete confirmation intermediate window
def delete_selected(self, request, queryset):
    queryset.delete()

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
    template = 'admin/edit_inline/tabular.html'
    # template = 'admin/edit_inline/tabular-nested.html'

class NarrativeForm(forms.ModelForm):
    class Meta:
        model = Narrative
        fields = '__all__'

class NarrativeInline(GenericTabularInline):
    raw_id_fields = ('activity',)

    autocomplete_lookup_fields = {
        'fk': ['activity'],
    }

    model = Narrative
    ct_field = "related_content_type"
    ct_fk_field = "related_object_id"
    inlines = []
    form=NarrativeForm

    extra = 3
    # max_num = 0
    # exclude = ('activity',)

    # def get_max_num(self, request, obj=None, **kwargs):
    #     count = len(self.direct_parent.narratives) if self.direct_parent else 0
    #     return self.extra

    def get_formset(self, request, instance, *args, **kwargs):
        initial = [{'activity': self.parent_instance} for i in range(self.extra)]
        formset =  super(NarrativeInline, self).get_formset(request, instance, *args, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        a = formset()
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

    extra = 0


class TransactionReceiverInline(NestedTabularInline):
    model = TransactionReceiver
    inlines = [
        NarrativeInline,
    ]

    extra = 0


class TransactionAdmin(NestedModelAdmin):
    search_fields = ['activity__id']
    list_display = ['__unicode__']
    exclude = ('value_string',)
    actions = (delete_selected,)
    inlines = [
        TransactionDescriptionInline,
        TransactionProviderInline,
        TransactionReceiverInline,
    ]


class TransactionInline(NestedTabularInline):
    exclude = ('value_string',)
    inlines = [
        TransactionDescriptionInline,
        TransactionProviderInline,
        TransactionReceiverInline,
    ]


class ActivityDateInline(NestedTabularInline):
    model = ActivityDate
    extra = 0


class ActivityReportingOrganisationInline(NestedTabularInline):
    model = ActivityReportingOrganisation
    extra = 0


class ActivityParticipatingOrganisationInline(NestedTabularInline):
    model = ActivityParticipatingOrganisation
    extra = 0


class TransactionInline(NestedTabularInline):
    model = Transaction
    extra = 0
    exclude = ('value_string',)


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

    # raw_id_fields = ('currency',)

    # autocomplete_lookup_fields = {
    #     'fk': ['currency'],
    # }


class CategoriesInline(NestedTabularInline):
    model = DocumentLinkCategory
    # extra = 0

class DocumentLinkInline(NestedStackedInline):
    inlines = [CategoriesInline, ]

    model = DocumentLink
    extra = 0


class ResultInline(NestedTabularInline):
    model = Result
    extra = 0


class LocationInline(NestedTabularInline):
    model = Location
    extra = 0


class RelatedActivityInline(NestedTabularInline):
    model = RelatedActivity
    fk_name='current_activity'
    extra = 0

    raw_id_fields = ('ref_activity',)

    autocomplete_lookup_fields = {
        'fk': ['ref_activity'],
    }


class DescriptionInline(NestedStackedInline):
    model = Description
    extra = 0
    inlines = [NarrativeInline, ]

class TitleInline(NestedStackedInline):
    model = Title
    extra = 0
    inlines = [NarrativeInline, ]

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        instances = formset.save()

        for form in formset.forms:
            if hasattr(form, 'nested_formsets') and form not in formset.deleted_forms:
                for nested_formset in form.nested_formsets:
                    self.save_formset(request, form, nested_formset, change)


class ActivityAdmin(ExtraNestedModelAdmin):
    search_fields = ['id']
    exclude = ('activity_aggregations',)
    list_display = ['__unicode__']
    actions = (delete_selected,)
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

        super(ActivityAdmin, self).save_model(request, obj, form, change)

        if not change:
            title = Title()
            title.activity = obj
            title.save()

            description = Description()
            description.activity = obj
            description.save()


    # raw_id_fields = ('default_currency',)

    # autocomplete_lookup_fields = {
    #     'fk': ['default_currency'],
    # }

class SectorAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['code', 'name', 'description', 'category']


admin.site.register(Activity, ActivityAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(Narrative)




