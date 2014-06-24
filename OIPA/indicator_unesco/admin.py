import xml.etree.cElementTree as etree
from django.contrib import admin
from django.shortcuts import get_object_or_404
from multiupload.admin import MultiUploadAdmin

from indicator.upload_indicators_helper import find_country, find_city, get_countries, get_cities, get_value, save_log, save_city_data, save_country_data
from indicator_unesco.models import UnescoIndicatorData, UnescoIndicator
from translation_model.models import TranslationModel


class UnescoIndicatorDataUploadAdmin(MultiUploadAdmin):
    list_display = ['unesco_indicator','country', 'value']
    search_fields = ['unesco_indicator']
    list_filter = ['unesco_indicator', 'country']
    # default value of all parameters:
    change_form_template = 'multiupload/change_form.html'
    change_list_template = 'multiupload/change_list.html'
    multiupload_template = 'multiupload/upload_unesco.html'
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
    multiupload_acceptedformats = ("text/xml",)

    def process_uploaded_file(self, uploaded, object,request, **kwargs):
        '''
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
        '''
        line_counter = 0
        country_found = []
        country_not_found = []
        total_items_saved = 0
        countries = get_countries()

        #getting the title of the file
        title = kwargs.get('title', [''])[0] or uploaded.name

        xmlDoc = uploaded
        xmlDocData = xmlDoc.read()
        xmlDocTree = etree.XML(xmlDocData)

        for indicator in xmlDocTree.iter('CountryId'):
            indicator_name_en = indicator[1].text.rstrip()
            indicator_name_fr = indicator[2].text.rstrip()
            indicator_country = indicator[0].text.rstrip()
            country_iso = indicator.get('countryid').rstrip()
            value = indicator[3].text.rstrip()
            type_value = None
            try:
                website_en = indicator[4].text.rstrip()
                website_fr = indicator[5].text.rstrip()
            except IndexError:
                website_en = None
                website_fr = None

            #try to find the indicator that is uploaded or create a new one
            indicator_from_db = UnescoIndicator.objects.get_or_create(id=indicator_name_en)[0]

            #getting country from our database
            country_from_db = find_country(country_name=indicator_country, countries=countries, iso2=country_iso)

            #add country to the log array
            if country_from_db:
                country_found.append(indicator_country)
            else:
                if indicator_country:
                    country_not_found.append(indicator_country)

            #saving the unesco indicator data
            if country_from_db:
                indicator_data_from_db = UnescoIndicatorData.objects.get_or_create(unesco_indicator=indicator_from_db, country=country_from_db, value=value)[0]

                #storing the translation of the indicator
                TranslationModel.objects.get_or_create(key=indicator_name_en, language='en', translation=indicator_name_en)
                TranslationModel.objects.get_or_create(key=indicator_name_en, language='fr', translation=indicator_name_fr)

                if website_en:
                    indicator_data_from_db.website = website_en
                    indicator_data_from_db.save()

                    #we need to store the translations as well
                    TranslationModel.objects.get_or_create(key=website_en, language='en', translation=website_en)
                    TranslationModel.objects.get_or_create(key=website_en, language='fr', translation=website_fr)


                total_items_saved += 1


            line_counter += 1


        log = save_log(file=uploaded,
                 uploaded_by_user=request.user,
                 cities_not_found=[],
                 countries_not_found=country_not_found,
                 total_cities_found=[],
                 total_countries_found=country_found,
                 total_cities_not_found=[],
                 total_countries_not_found=country_not_found,
                 total_items_saved=total_items_saved
        )


        return {
            'url': '/admin/indicator/csvuploadlog/%s/' % str(log.id),
            'thumbnail_url': '',
            'id': str(log.id),
            'name' : title,
            'country_not_found' : log.countries_not_found,
            'total_countries_not_found' : country_not_found.__len__(),
            'city_not_found' : log.cities_not_found,
            'total_cities_not_found' : 0,
            'total_items_saved' : str(total_items_saved),

        }

    def delete_file(self, pk, request):
        '''
        Function to delete a file.
        '''
        # This is the default implementation.
        obj = get_object_or_404(self.queryset(request), pk=pk)
        obj.delete()




admin.site.register(UnescoIndicatorData, UnescoIndicatorDataUploadAdmin)
admin.site.register(UnescoIndicator)



