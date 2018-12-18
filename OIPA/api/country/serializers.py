from django.urls import reverse
from rest_framework import serializers

import geodata
from api.fields import JSONField
from api.generics.serializers import DynamicFieldsModelSerializer
from api.region.serializers import RegionSerializer


class CountrySerializer(DynamicFieldsModelSerializer):

    code = serializers.CharField()
    name = serializers.CharField(required=False)
    url = serializers.HyperlinkedIdentityField(
        view_name='countries:country-detail', read_only=True)
    region = RegionSerializer(fields=('url', 'code', 'name'))
    un_region = RegionSerializer(fields=('url', 'code', 'name'))
    unesco_region = RegionSerializer(fields=('url', 'code', 'name'))
    location = JSONField(source='center_longlat.json')
    polygon = JSONField()
    activities = serializers.SerializerMethodField()

    def get_activities(self, obj):
        request = self.context.get('request')
        url = request.build_absolute_uri(reverse('activities:activity-list'))
        return url + '?recipient_country=' + obj.code

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
            'region',
            'un_region',
            'unesco_region',
            'dac_country_code',
            'iso3',
            'alpha3',
            'fips10',
            'data_source',
            'activities',
            'location',
            'polygon',
        )
