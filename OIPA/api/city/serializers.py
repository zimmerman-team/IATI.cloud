from rest_framework import serializers
import geodata
from api.generics.serializers import DynamicFieldsModelSerializer
from api.country.serializers import CountrySerializer
from api.fields import GeometryField


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
