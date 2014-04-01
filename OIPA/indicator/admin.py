from django.contrib import admin
from django.shortcuts import get_object_or_404
from multiupload.admin import MultiUploadAdmin
from indicator.models import Indicator, IndicatorData, IndicatorSource, IncomeLevel, LendingType, IndicatorTopic
from django.conf.urls import patterns
from indicator.admin_tools import IndicatorAdminTools
from django.http import HttpResponse
from indicator.upload_indicators_helper import find_country, find_city, get_countries, get_cities
from indicator.wbi_parser import WBI_Parser


class IndicatorAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super(IndicatorAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-indicator/$', self.admin_site.admin_view(self.update_indicators)),
            (r'^update-indicator-data/$', self.admin_site.admin_view(self.update_indicator_data)),
            (r'^update-indicator-city-data/$', self.admin_site.admin_view(self.update_indicator_city_data)),
            (r'^update-wbi-indicator/$', self.admin_site.admin_view(self.update_WBI_indicators))
        )
        return my_urls + urls

    def update_indicator_data(self, request):
        admTools = IndicatorAdminTools()
        admTools.update_indicator_data()
        return HttpResponse('Success')

    def update_indicator_city_data(self, request):
        admTools = IndicatorAdminTools()
        admTools.update_indicator_city_data()
        return HttpResponse('Success')

    def update_indicators(self, request):
        admTools = IndicatorAdminTools()
        admTools.update_indicators()
        return HttpResponse('Success')

    def update_WBI_indicators(self, request):
        wbi_parser = WBI_Parser()
        wbi_parser.import_wbi_indicators()
        return HttpResponse('Success')

class IndicatorDataAdmin(admin.ModelAdmin):
    list_display = ['indicator', 'city','country', 'region', 'year', 'value']
    search_fields = ['year', 'indicator__friendly_label', 'value']
    list_filter = ['indicator', 'city', 'country', 'year']

class MyModelAdmin(MultiUploadAdmin):
    list_display = ['indicator','selection_type', 'city','country', 'region', 'year', 'value']
    search_fields = ['year', 'indicator__friendly_label', 'value']
    list_filter = ['indicator','selection_type', 'city', 'country', 'year']
    # default value of all parameters:
    change_form_template = 'multiupload/change_form.html'
    change_list_template = 'multiupload/change_list.html'
    multiupload_template = 'multiupload/upload.html'
    # if true, enable multiupload on list screen
    # generaly used when the model is the uploaded element
    multiupload_list = True
    # if true enable multiupload on edit screen
    # generaly used when the model is a container for uploaded files
    # eg: gallery
    # can upload files direct inside a gallery.
    multiupload_form = True
    # max allowed filesize for uploads in bytes
    multiupload_maxfilesize = 3 * 2 ** 20 # 3 Mb
    # min allowed filesize for uploads in bytes
    multiupload_minfilesize = 0
    # tuple with mimetype accepted
    multiupload_acceptedformats = ( "text/csv",)

    def process_uploaded_file(self, uploaded, object,not_sure, **kwargs):
        '''
        This method will be called for every file uploaded.
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
        '''
        # example:
        title = kwargs.get('title', [''])[0] or uploaded.name

        #check here how to save the file, i think we have to create a model, check https://github.com/gkuhn1/django-adminfiles/blob/master/adminfiles/models.py
        #f = self.model(upload=uploaded, title=title)
        #f.save()
        import csv
        try:
            dialect = csv.Sniffer().sniff(uploaded.read(4048))
        except csv.Error:
            dialect = csv.excel

        file = csv.DictReader(uploaded, dialect=dialect)
        keys = []
        for key in file.next().iterkeys():
            keys.append(key)

        line_counter = 0
        indicator_from_db = None
        city_found = []
        city_not_found = []
        country_found = []
        country_not_found = []

        cities = get_cities()
        countries = get_countries()
        for line in file:
            #getting data from the csv file
            city_csv = line.get('city')
            deprivation_type_csv = line.get('deprivation_type')
            description_csv = line.get('description')
            selection_type_csv = line.get('selection_type')
            country_csv = line.get('country')
            region_csv = line.get('region_csv')
            friendly_label_csv = line.get('friendly_name')
            value_csv = line.get('value')
            #todo replace , with . for floating numbers, check if this is always the case
            value_csv = value_csv.replace(',', '.')
            year_range_csv = line.get('year_range')
            indicator_id_csv = line.get('indicator_id')
            year_csv = line.get('year')
            type_data_csv = line.get('type_data')

            if line_counter == 0:
                #try to find the indicator that is uploaded or create a new one
                #todo I think an indicator is unique together with a selection_type or derivation_type
                indicator_from_db = Indicator.objects.get_or_create(id=indicator_id_csv)[0]

                #update the indicator fields
                indicator_from_db.description = description_csv
                indicator_from_db.friendly_label = friendly_label_csv
                indicator_from_db.type_data = type_data_csv
                indicator_from_db.selection_type = selection_type_csv
                indicator_from_db.deprivation_type = deprivation_type_csv
                indicator_from_db.save()

            #getting city from our database
            try:
                if city_csv:
                    city_from_db = find_city(city_name=city_csv, cities=cities)
                else:
                    city_from_db = None
            except:
                city_from_db = None

                #continue

            #getting country from our database
            try:
                if country_csv:
                    country_from_db = find_country(country_name=country_csv, countries=countries)
                else:
                    country_from_db = None
            except:
                country_from_db = None

            if country_from_db:
                country_found.append(country_csv)
            else:
                country_not_found.append(country_csv)

            if city_from_db:
                city_found.append(city_csv)
            else:
                city_not_found.append(city_csv)

            #this block is for storing data related to cities
            try:
                if city_from_db:
                    #if the indicator data a selection type contains than we need to store that correctly
                    if selection_type_csv:
                        indicator_data_from_db = IndicatorData.objects.get_or_create(year=year_csv, indicator=indicator_from_db, selection_type=selection_type_csv, city=city_from_db)[0]
                    else:
                        indicator_data_from_db = IndicatorData.objects.get_or_create(year=year_csv, indicator=indicator_from_db, city=city_from_db)[0]
                    if country_from_db:
                        indicator_data_from_db.country = country_from_db
                    indicator_data_from_db.city = city_from_db
                    #todo get region from db
                    indicator_data_from_db.value = float(value_csv)
                    #todo add year range to model IndicatorData
                    #if year_range_csv:
                    #    indicator_data_from_db.year_range = year_range_csv
                    indicator_data_from_db.save()
            except:
                pass

            #this block is for storing country related indicator data
            try:
                if country_from_db and not city_csv:
                    if selection_type_csv:
                        indicator_data_from_db = IndicatorData.objects.get_or_create(year=year_csv, indicator=indicator_from_db, selection_type=selection_type_csv, country=country_from_db)[0]
                    else:
                        indicator_data_from_db = IndicatorData.objects.get_or_create(year=year_csv, indicator=indicator_from_db, country=country_from_db)[0]
                    #todo get region from db
                    indicator_data_from_db.value = float(value_csv)
                    #todo add year range to model IndicatorData
                    #if year_range_csv:
                    #    indicator_data_from_db.year_range = year_range_csv
                    indicator_data_from_db.save()
            except:
                pass

            line_counter += 1




        return {
            'url': 'f.image_thumb()',
            'thumbnail_url': 'f.image_thumb()',
            'id': 'f.id',
            'name': title
        }

    def delete_file(self, pk, request):
        '''
        Function to delete a file.
        '''
        # This is the default implementation.
        obj = get_object_or_404(self.queryset(request), pk=pk)
        obj.delete()



admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(IndicatorData, MyModelAdmin)
admin.site.register(IndicatorSource)
admin.site.register(IncomeLevel)
admin.site.register(LendingType)
admin.site.register(IndicatorTopic)

