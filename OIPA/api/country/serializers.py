from rest_framework import serializers
import geodata
from api.generics.serializers import XMLMetaMixin, DynamicFieldsModelSerializer
from api.region.serializers import RegionSerializer
from api.fields import JSONField

class CountrySerializer(XMLMetaMixin, DynamicFieldsModelSerializer):
    xml_meta = {'only': 'code'}

    class BasicCitySerializer(serializers.ModelSerializer):
        url = serializers.HyperlinkedIdentityField(view_name='cities:city-detail')

        class Meta:
            model = geodata.models.City
            fields = (
                'url',
                'id',
                'name'
            )

    url = serializers.HyperlinkedIdentityField(view_name='countries:country-detail')
    region = RegionSerializer(fields=('url', 'code', 'name'))
    un_region = RegionSerializer(fields=('url', 'code', 'name'))
    unesco_region = RegionSerializer(fields=('url', 'code', 'name'))
    capital_city = BasicCitySerializer()
    location = JSONField(source='center_longlat.json')
    polygon = JSONField()
    activities = serializers.HyperlinkedIdentityField(
        view_name='countries:country-activities')
    indicators = serializers.HyperlinkedIdentityField(
        view_name='countries:country-indicators')
    cities = serializers.HyperlinkedIdentityField(view_name='countries:country-cities')

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
            'indicators',
            # 'adm1region_set',
            'cities',
            'location',
            'polygon',
        )
