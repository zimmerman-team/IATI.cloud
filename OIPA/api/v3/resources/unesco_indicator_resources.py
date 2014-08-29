from django.db.models import Q
from tastypie.constants import ALL
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from indicator_unesco.models import UnescoIndicatorData
from translation_model.models import TranslationModel


class UnescoIndicatorResource(ModelResource):

    class Meta:
        queryset = UnescoIndicatorData.objects.all()
        resource_name = 'unesco-indicators'
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])
        allowed_methods = ['get']

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(UnescoIndicatorResource, self).apply_filters(request, applicable_filters)

        #try to see if the client wants to filter based on a country
        country = request.GET.get('country', None)

        #if so, change the query set
        if country:
            qset = (
                Q(country__code=country, )
            )

            return base_object_list.filter(qset)

        #give back the default queryset
        else:
            return base_object_list

    #we use this function to add country and indicator name to the results
    def dehydrate(self, bundle):
        #add option to filter on language
        filter_language = bundle.request.GET.get('language', None)

        #if the user prefers a language than return the translation (now able to filter on "en" and "fr"
        if filter_language:
            bundle.data['indicator'] = TranslationModel.objects.get(key=bundle.obj.unesco_indicator.id, language__icontains=filter_language).translation

        #if there is no filter, just return the default value
        else:
            bundle.data['indicator'] = bundle.obj.unesco_indicator.id

        #return the iso value of a country
        bundle.data['country'] = bundle.obj.country.code

        #return the new bundle with country and inidcato
        return bundle