from django.contrib import admin
from translation_model.models import TranslationModel


class TranslationModelAdmin(admin.ModelAdmin):
    list_display = ['key', 'language','translation']
    search_fields = ['key']
    list_filter = ['language']

admin.site.register(TranslationModel, TranslationModelAdmin)