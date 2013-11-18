from django.contrib import admin
from IATI.models import activity, organisation
from django.conf.urls import patterns
from IATI.management.commands.update_total_budget import UpdateTotal
from django.http import HttpResponse

class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['code', 'name']
    list_display = ['__unicode__', 'code', 'type', 'total_activities']

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

