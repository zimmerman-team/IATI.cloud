from rest_framework import serializers

import geodata
from api.country.serializers import CountrySerializer
from api.fields import GeometryField
from api.generics.serializers import DynamicFieldsModelSerializer


class CitySerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='cities:city-detail')
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
