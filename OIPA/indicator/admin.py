from django.contrib import admin
from multiupload.admin import MultiUploadAdmin

from indicator.csv_upload.indicator_parser import IndicatorParser
from indicator.models import Indicator
from indicator.models import IndicatorData
from indicator.models import IndicatorDataValue
from indicator.models import IndicatorSource
from indicator.models import IncomeLevel
from indicator.models import LendingType
from indicator.models import IndicatorTopic
from indicator.models import CsvUploadLog


class IndicatorAdmin(admin.ModelAdmin):
    list_display = ['friendly_label', 'category', 'type_data']


class IndicatorDataValueInline(admin.TabularInline):
    model = IndicatorDataValue
    extra = 0


class IndicatorDataAdmin(admin.ModelAdmin):
    inlines = [IndicatorDataValueInline]

    list_display = ['indicator', 'city', 'country', 'region']
    search_fields = ['indicator__friendly_label']
    list_filter = ['indicator', 'city', 'country']


class IndicatorDataUploadAdmin(MultiUploadAdmin):
    list_display = ['indicator', 'selection_type', 'city', 'country', 'region']
    search_fields = ['indicator__friendly_label']
    list_filter = ['indicator', 'selection_type', 'city', 'country', 'region']
    change_form_template = 'multiupload/change_form.html'
    change_list_template = 'multiupload/change_list.html'
    multiupload_template = 'multiupload/upload.html'
    multiupload_list = True
    multiupload_form = True
    # 6 Mb max
    multiupload_maxfilesize = 6 * 2 ** 20
    multiupload_minfilesize = 0
    multiupload_acceptedformats = ("text/csv", "text/xml", "text/comma-separated-values")

    def process_uploaded_file(self, uploaded, object, request, **kwargs):
        """
        This method will be called for every csv file uploaded.

        See django-multiupload lib for more info
        """
        parser = IndicatorParser()
        return parser.parse(uploaded, object, request, **kwargs)


admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(IndicatorData, IndicatorDataUploadAdmin)
admin.site.register(IndicatorSource)
admin.site.register(IncomeLevel)
admin.site.register(LendingType)
admin.site.register(IndicatorTopic)
admin.site.register(CsvUploadLog)

