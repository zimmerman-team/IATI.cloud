from django.contrib import admin
from django import forms
from iati.models import *
from iati.transaction.models import *
from django.conf.urls import patterns
from django.contrib.contenttypes.admin import GenericTabularInline
from django.http import HttpResponse
from iati.updater import SectorUpdater

from nested_inline.admin import NestedStackedInline, NestedTabularInline, NestedModelAdmin, NestedInline

from django.core.exceptions import (ValidationError,)

# Avoid giant delete confirmation intermediate window
def delete_selected(self, request, queryset):
    queryset.delete()


class NarrativeInline(GenericTabularInline):
    model = Narrative
    ct_field = "related_content_type"
    ct_fk_field = "related_object_id"
    exclude = ('parent_content_type', 'parent_object_id')
    inlines = []

    extra = 0


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


class ActivityDateInline(admin.TabularInline):
    model = ActivityDate
    extra = 0


class ActivityReportingOrganisationInline(admin.TabularInline):
    model = ActivityReportingOrganisation
    extra = 0


class ActivityParticipatingOrganisationInline(admin.TabularInline):
    model = ActivityParticipatingOrganisation
    extra = 0


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    exclude = ('value_string',)


class ActivityPolicyMarkerInline(admin.TabularInline):
    model = ActivityPolicyMarker
    extra = 0


class ActivityRecipientCountryInline(admin.TabularInline):
    model = ActivityRecipientCountry
    extra = 0

    raw_id_fields = ('country',)

    autocomplete_lookup_fields = {
        'fk': ['country'],
    }


class ActivitySectorInline(admin.TabularInline):
    model = ActivitySector
    extra = 0


class ActivityRecipientRegionInline(admin.TabularInline):
    model = ActivityRecipientRegion
    extra = 0


class BudgetInline(admin.TabularInline):
    model = Budget
    exclude = ('value_string',)
    extra = 0


class DocumentLinkInline(admin.TabularInline):
    model = DocumentLink
    extra = 0


class ResultInline(admin.TabularInline):
    model = Result
    extra = 0


class LocationInline(admin.TabularInline):
    model = Location
    extra = 0


class RelatedActivityInline(admin.TabularInline):
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


class ActivityAdmin(NestedModelAdmin):
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


class SectorAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['code', 'name', 'description', 'category']

    def get_urls(self):
        urls = super(SectorAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-unesco-sectors', self.admin_site.admin_view(self.update_unesco_sectors)),
        )
        return my_urls + urls

    def update_unesco_sectors(self, request):
        sector_updater = SectorUpdater()
        success = sector_updater.update_unesco_sectors()
        if success:
            return HttpResponse('Success')
        else:
            return False


admin.site.register(Activity, ActivityAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(Narrative)




