from rest_framework import serializers
import geodata


class CountryDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='country-detail')

    class Meta:
        model = geodata.models.Country
        fields = ()


class CountryListSerializer(CountryDetailSerializer):
    class Meta:
        model = geodata.models.Country
        fields = ('url', 'code', 'name',)
