from django.contrib import admin
from django.conf.urls import patterns
from django.http import HttpResponse
from indicator.admin_tools import IndicatorAdminTools
from multiupload.admin import MultiUploadAdmin
from indicator.wbi_parser import WbiParser
from indicator.csv_upload.upload_indicators_helper import find_country
from indicator.csv_upload.upload_indicators_helper import find_city
from indicator.csv_upload.upload_indicators_helper import get_countries
from indicator.csv_upload.upload_indicators_helper import get_cities
from indicator.csv_upload.upload_indicators_helper import save_log
from indicator.csv_upload.upload_indicators_helper import save_city_data
from indicator.csv_upload.upload_indicators_helper import save_country_data
from indicator.csv_upload.upload_indicators_helper import get_value
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

    def get_urls(self):
        urls = super(IndicatorAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-indicator/$', self.admin_site.admin_view(self.update_indicators)),
            (r'^update-indicator-data/$', self.admin_site.admin_view(self.update_indicator_data)),
            (r'^update-indicator-city-data/$', self.admin_site.admin_view(self.update_indicator_city_data)),
            (r'^update-wbi-indicator/$', self.admin_site.admin_view(self.update_wbi_indicators)),
            (r'^old-to-new-urbnnrs-city/$', self.admin_site.admin_view(self.old_to_new_urbnnrs_city)),
            (r'^old-to-new-urbnnrs-country/$', self.admin_site.admin_view(self.old_to_new_urbnnrs_country)),
            (r'^reformat-values/$', self.admin_site.admin_view(self.reformat_values))
        )
        return my_urls + urls

    def reformat_values(self, request):
        name = request.GET["name"]
        data_type = request.GET["data_type"]
        keep_dot = request.GET["keep_dot"]
        admin_tools = IndicatorAdminTools()
        csv_text = admin_tools.reformat_values(name, data_type, keep_dot)
        response = HttpResponse(csv_text, content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename="+name+".csv"
        return response

    def old_to_new_urbnnrs_city(self, request):
        admin_tools = IndicatorAdminTools()
        name = request.GET["name"]
        data_type = request.GET["data_type"]
        indicator_id = request.GET["id"]
        csv_text = admin_tools.old_to_new_urbnnrs_city(indicator_id, name, data_type)
        return HttpResponse(csv_text, content_type='text/csv')

    def old_to_new_urbnnrs_country(self, request):
        admin_tools = IndicatorAdminTools()
        name = request.GET["name"]
        data_type = request.GET["data_type"]
        indicator_id = request.GET["id"]
        csv_text = admin_tools.old_to_new_urbnnrs_country(indicator_id, name, data_type)
        return HttpResponse(csv_text, content_type='text/csv')

    def update_indicator_data(self, request):
        admin_tools = IndicatorAdminTools()
        admin_tools.update_indicator_data()
        return HttpResponse('Success')

    def update_indicator_city_data(self, request):
        admin_tools = IndicatorAdminTools()
        admin_tools.update_indicator_city_data()
        return HttpResponse('Success')

    def update_indicators(self, request):
        admin_tools = IndicatorAdminTools()
        admin_tools.update_indicators()
        return HttpResponse('Success')

    def update_wbi_indicators(self, request):
        wbi_parser = WbiParser()
        wbi_parser.import_wbi_indicators()
        return HttpResponse('Success')

    def update_wbi_indicator_data(self, request):
        wbi_parser = WbiParser()
        wbi_parser.import_wbi_indicators()
        return HttpResponse('Success')


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
        Parameters:
            :uploaded: instance of uploaded file
            :object: instance of object if in form_multiupload else None
            :kwargs: request.POST received with file
        Return:
            It MUST return at least a dict with:
            {
                'url': 'url to download the file',
                'thumbnail_url': 'some url for an image_thumbnail or icon',
                'id': 'id of instance created in this method',
                'name': 'the name of created file',
            }
        """

        #getting the title of the file
        title = kwargs.get('title', [''])[0] or uploaded.name

        import csv
        try:
            dialect = csv.Sniffer().sniff(uploaded.read(4048))
        except csv.Error:
            dialect = csv.excel

        csv_file = csv.DictReader(uploaded, dialect=dialect)

        line_counter = 0
        indicator_from_db = None
        city_found = []
        city_not_found = []
        country_found = []
        country_not_found = []
        total_items_saved = 0

        cities = get_cities()
        countries = get_countries()

        for line in csv_file:
            city_csv = line.get('city')
            deprivation_type_csv = line.get('deprivation_type')
            description_csv = line.get('description')
            selection_type_csv = line.get('selection_type')
            country_csv = line.get('country')
            friendly_label_csv = line.get('friendly_name')
            value_csv = line.get('value')
            indicator_id_csv = line.get('indicator_id')
            year_csv = line.get('year')
            type_data_csv = line.get('type_data')
            category_csv = line.get('category')

            value_csv = get_value(value_csv=value_csv)
            if not value_csv:
                continue

            if line_counter == 0:
                #try to find the indicator that is uploaded or create a new one
                indicator_from_db = Indicator.objects.get_or_create(
                    id=indicator_id_csv,
                    defaults={
                        'description': description_csv,
                        'friendly_label': friendly_label_csv,
                        'type_data': type_data_csv,
                        'deprivation_type': deprivation_type_csv,
                        'category': category_csv})

            #getting country from our database
            country_from_db = find_country(country_name=country_csv, countries=countries)

            #add country to the log array
            if country_from_db:
                country_found.append(country_csv)
            elif country_csv:
                    country_not_found.append(country_csv)

            city_from_db = find_city(city_name=city_csv, cities=cities, country=country_from_db)

            #add city to the log array
            if city_from_db:
                city_found.append(city_csv)
            elif city_csv:
                    city_not_found.append(city_csv)

            if city_from_db:
                #this block is for storing data related to cities
                if save_city_data(
                    city_from_db=city_from_db,
                    selection_type_csv=selection_type_csv,
                    indicator_from_db=indicator_from_db,
                    year_csv=year_csv,
                    value_csv=value_csv
                ):
                    total_items_saved += 1

            elif country_from_db:
                #this block is for storing data related to countries
                if save_country_data(
                    country_from_db=country_from_db,
                    city_csv=city_csv,
                    selection_type_csv=selection_type_csv,
                    year_csv=year_csv,
                    indicator_from_db=indicator_from_db,
                    value_csv=value_csv
                ):
                    total_items_saved += 1

            line_counter += 1

        log = save_log(
            file=uploaded,
            uploaded_by_user=request.user,
            cities_not_found=city_not_found,
            countries_not_found=country_not_found,
            total_cities_found=city_found,
            total_countries_found=country_found,
            total_cities_not_found=city_not_found,
            total_countries_not_found=country_not_found,
            total_items_saved=total_items_saved
        )

        return {
            'url': '/admin/indicator/csvuploadlog/%s/' % str(log.id),
            'thumbnail_url': '',
            'id': str(log.id),
            'name': title,
            'country_not_found': log.countries_not_found,
            'total_countries_not_found': country_not_found.__len__(),
            'city_not_found': log.cities_not_found,
            'total_cities_not_found': city_not_found.__len__(),
            'total_items_saved': str(total_items_saved),
        }

admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(IndicatorData, IndicatorDataUploadAdmin)
admin.site.register(IndicatorSource)
admin.site.register(IncomeLevel)
admin.site.register(LendingType)
admin.site.register(IndicatorTopic)
admin.site.register(CsvUploadLog)

