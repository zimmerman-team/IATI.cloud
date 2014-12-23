from rest_framework import serializers
import geodata
from api.generics.serializers import DynamicFieldsModelSerializer
from api.country.serializers import CountrySerializer
from indicator.models import Indicator


class IndicatorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = ('id',)
        unique = True


class CitySerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='city-detail')
    country = CountrySerializer(fields=('url', 'code', 'name'))
    indicator_data = IndicatorDataSerializer(many=True, source='indicators')

    class Meta:
        model = geodata.models.City
        fields = (
            'url',
            'id',
            'geoname_id',
            'name',
            'country',
            'location',
            'indicator_data',

            # Reverse linked data
            'capital_city',
        )
