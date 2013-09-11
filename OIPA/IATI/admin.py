from django.contrib import admin
from IATI.models import activity, organisation


class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['code', 'name']
    list_display = ['__unicode__', 'code', 'type', 'total_activities']


admin.site.register(activity)
admin.site.register(organisation, OrganisationAdmin)

