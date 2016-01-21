from django.contrib import admin
from iati_organisation.models import Organisation

from django.utils.safestring import mark_safe
# Register your models here.

class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('code',)

admin.site.register(Organisation, OrganisationAdmin)
