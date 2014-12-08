from rest_framework import serializers
import geodata
from api.serializers import DynamicFieldsModelSerializer


class CitySerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='city-detail')

    class Meta:
        model = geodata.models.City
        fields = (
            'url',
            'id',
            'geoname_id',
            'name',
            'country',
            'location',
            'ascii_name',
            'alt_name',
            'namepar',

            # Reverse linked data
            # 'indicatordata_set',
            # 'capital_city',
        )
