from rest_framework import serializers
import geodata
from api.generics.serializers import DynamicFieldsModelSerializer
from api.country.serializers import CountrySerializer
from indicator.models import Indicator


class GeometryField(serializers.Field):
    def to_representation(self, obj):
        return {
            'type': 'Point',
            'coordinates': [obj.x, obj.y]
        }


class IndicatorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = ('id',)


class CitySerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='city-detail')
    country = CountrySerializer(fields=('url', 'code', 'name'))
    location = GeometryField()

    class Meta:
        model = geodata.models.City
        fields = (
            'url',
            'id',
            'geoname_id',
            'name',
            'country',
            'location',
            'is_capital',
        )
