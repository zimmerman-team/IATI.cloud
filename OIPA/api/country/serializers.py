from rest_framework import serializers
import geodata
from api.generics.serializers import DynamicFieldsModelSerializer
from api.region.serializers import RegionSerializer
from api.fields import JSONField
from django.core.urlresolvers import reverse


class CountrySerializer(DynamicFieldsModelSerializer):
    class BasicCitySerializer(serializers.ModelSerializer):
        url = serializers.HyperlinkedIdentityField(view_name='cities:city-detail')

        class Meta:
            model = geodata.models.City
            fields = (
                'url',
                'id',
                'name'
            )

        
    code = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(view_name='countries:country-detail', read_only=True)
    region = RegionSerializer(fields=('url', 'code', 'name'))
    un_region = RegionSerializer(fields=('url', 'code', 'name'))
    unesco_region = RegionSerializer(fields=('url', 'code', 'name'))
    capital_city = BasicCitySerializer()
    location = JSONField(source='center_longlat.json')
    polygon = JSONField()
    activities = serializers.SerializerMethodField()
    cities = serializers.SerializerMethodField()

    def get_activities(self, obj):
        request = self.context.get('request')
        url = request.build_absolute_uri(reverse('activities:activity-list'))
        return url + '?recipient_country=' + obj.code

    def get_cities(self, obj):
        request = self.context.get('request')
        url = request.build_absolute_uri(reverse('cities:city-list'))
        return url + '?country=' + obj.code

    class Meta:
        model = geodata.models.Country
        fields = (
            'url',
            'code',
            'pk',
            'numerical_code_un',
            'name',
            'alt_name',
            'language',
            'capital_city',
            'region',
            'un_region',
            'unesco_region',
            'dac_country_code',
            'iso3',
            'alpha3',
            'fips10',
            'data_source',
            'activities',
            'cities',
            'location',
            'polygon',
        )
