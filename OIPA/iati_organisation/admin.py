from django.contrib import admin
from iati_organisation.models import Organisation

from django.utils.safestring import mark_safe
# Register your models here.

class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['id', ]
    list_display = ('id',)

admin.site.register(Organisation, OrganisationAdmin)
