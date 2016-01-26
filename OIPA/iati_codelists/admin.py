from django.contrib import admin
from iati_codelists.models import *


class CodelistAdmin(admin.ModelAdmin):
    search_fields = ['code', 'name',]


admin.site.register(Sector, CodelistAdmin)
admin.site.register(PolicyMarker, CodelistAdmin)
admin.site.register(FileFormat, CodelistAdmin)
admin.site.register(Currency, CodelistAdmin)
admin.site.register(Language, CodelistAdmin)
admin.site.register(DocumentCategory, CodelistAdmin)

