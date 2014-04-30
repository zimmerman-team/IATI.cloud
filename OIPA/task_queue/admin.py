from django.contrib import admin
from iati.models import Activity, Organisation
from django.conf.urls import patterns
from iati.management.commands.total_budget_updater import TotalBudgetUpdater
from iati.management.commands.organisation_name_updater import OrganisationNameUpdater
from django.http import HttpResponse


# class ScheduleAdmin(admin.ModelAdmin):
#     search_fields = ['id']
#     list_display = ['__unicode__']
#
#     def get_urls(self):
#         urls = super(ActivityAdmin, self).get_urls()
#
#         my_urls = patterns('',
#             (r'^update-budget-totals', self.admin_site.admin_view(self.update_budget_totals))
#         )
#         return my_urls + urls
#
#     def update_budget_totals(self):
#         update_total = TotalBudgetUpdater()
#         success = update_total.update()
#         if success:
#             return HttpResponse('Success')
#         else:
#             return False
#
# admin.site.register(Activity, ActivityAdmin)

