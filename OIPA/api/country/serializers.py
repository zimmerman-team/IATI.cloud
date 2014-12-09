from rest_framework import serializers
import geodata
from api.serializers import DynamicFieldsModelSerializer


class CountrySerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='country-detail')

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
            'center_longlat',
            'polygon',
            'data_source',

            # Reverse linked data
            'activity_set',
            'adm1region_set',
            'city_set',
            'indicatordata_set',
            'location_set',
            'unescoindicatordata_set',
            'activityrecipientcountry_set',
        )
