from rest_framework import serializers
import geodata
from api.generics.serializers import DynamicFieldsModelSerializer
from api.region.serializers import RegionSerializer
from api.fields import JSONField


class CountrySerializer(DynamicFieldsModelSerializer):
    class BasicCitySerializer(serializers.ModelSerializer):
        url = serializers.HyperlinkedIdentityField(view_name='city-detail')

        class Meta:
            model = geodata.models.City
            fields = (
                'url',
                'id',
                'name'
            )

    url = serializers.HyperlinkedIdentityField(view_name='country-detail')
    region = RegionSerializer(fields=('url', 'code', 'name'))
    un_region = RegionSerializer(fields=('url', 'code', 'name'))
    unesco_region = RegionSerializer(fields=('url', 'code', 'name'))
    capital_city = BasicCitySerializer()
    location = JSONField(source='center_longlat.json')
    polygon = JSONField()
    activities = serializers.HyperlinkedIdentityField(view_name='country-activities')
    cities = BasicCitySerializer(source='city_set', many=True)

    class Meta:
        model = geodata.models.Country
        fields = (
            'url',
            'code',
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
            'location',
            'polygon',
            'data_source',

            # Reverse linked data
            'activities',
            # 'adm1region_set',
            'cities',
            'indicatordata_set',
            'unescoindicatordata_set',
        )
