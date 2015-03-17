from django.contrib import admin
from iati.models import Activity, Organisation, Sector, Narrative
from django.conf.urls import patterns
from iati.management.commands.total_budget_updater import TotalBudgetUpdater
from iati.management.commands.organisation_name_updater import OrganisationNameUpdater
from django.http import HttpResponse
from iati.updater import SectorUpdater

class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['code', 'name']
    list_display = ['code', 'abbreviation', 'name', 'type', 'total_activities']

    def get_urls(self):
        urls = super(OrganisationAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-organisation-names', self.admin_site.admin_view(self.update_organisation_names))
        )
        return my_urls + urls

    def update_organisation_names(self):
        org_updater = OrganisationNameUpdater()
        success = org_updater.update()
        if success:
            return HttpResponse('Success')
        else:
            return False



class ActivityAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['__unicode__']

    def get_urls(self):
        urls = super(ActivityAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-budget-totals', self.admin_site.admin_view(self.update_budget_totals))
        )
        return my_urls + urls

    def update_budget_totals(self):
        update_total = TotalBudgetUpdater()
        success = update_total.update()
        if success:
            return HttpResponse('Success')
        else:
            return False


class SectorAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['code', 'name', 'description', 'category']

    def get_urls(self):
        urls = super(SectorAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-unesco-sectors', self.admin_site.admin_view(self.update_unesco_sectors)),
            (r'^update-rain-sectors', self.admin_site.admin_view(self.update_rain_sectors))
        )
        return my_urls + urls

    def update_unesco_sectors(self, request):
        sector_updater = SectorUpdater()
        success = sector_updater.update_unesco_sectors()
        if success:
            return HttpResponse('Success')
        else:
            return False

    def update_rain_sectors(self, request):
        sector_updater = SectorUpdater()
        success = sector_updater.update_rain_sectors()
        if success:
            return HttpResponse('Success')
        else:
            return False

admin.site.register(Activity, ActivityAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(Narrative)




