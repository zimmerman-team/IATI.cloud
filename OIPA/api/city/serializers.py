from rest_framework import serializers
import geodata


class CityDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='city-detail')

    class Meta:
        model = geodata.models.City
        fields = ()


class CityListSerializer(CityDetailSerializer):
    class Meta:
        model = geodata.models.City
        fields = ('url', 'id', 'name')
