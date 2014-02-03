from django.contrib import admin
from IATI.models import activity, organisation
from django.conf.urls import patterns
from IATI.management.commands.update_total_budget import UpdateTotal
from django.http import HttpResponse
from IATI.admin_tools import AdminTools

class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['code', 'name']
    list_display = ['code', 'abbreviation', 'name', 'type', 'total_activities']

    def get_urls(self):
        urls = super(OrganisationAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-organisation-names/$', self.admin_site.admin_view(self.update_organisation_names))
        )
        return my_urls + urls

    def update_organisation_names(self, request):
        admin_tools = AdminTools()
        admin_tools.update_organisation_names()
        return HttpResponse('Success')



class ActivityAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['__unicode__']

    def get_urls(self):
        urls = super(ActivityAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-budget-totals/$', self.admin_site.admin_view(self.update_budget_totals))
        )
        return my_urls + urls

    def update_budget_totals(self, request):
        update_total = UpdateTotal()
        update_total.updateTotal()
        return HttpResponse('Success')

admin.site.register(activity, ActivityAdmin)
admin.site.register(organisation, OrganisationAdmin)


