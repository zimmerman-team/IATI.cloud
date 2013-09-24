from django.contrib import admin
from IATI.models import activity, organisation


class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['code', 'name']
    list_display = ['__unicode__', 'code', 'type', 'total_activities']

class ActivityAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['__unicode__']



admin.site.register(activity, ActivityAdmin)
admin.site.register(organisation, OrganisationAdmin)

