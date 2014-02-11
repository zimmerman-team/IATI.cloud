from django.contrib import admin
from iatip.models import Activity, Organisation
from django.conf.urls import patterns
from iatip.management.commands.total_budget_updater import TotalBudgetUpdater
from iatip.management.commands.organisation_name_updater import OrganisationNameUpdater
from django.http import HttpResponse

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

admin.site.register(Activity, ActivityAdmin)
admin.site.register(Organisation, OrganisationAdmin)


