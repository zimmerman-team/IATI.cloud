from rest_framework import serializers
import geodata
from api.generics.serializers import DynamicFieldsModelSerializer
from api.region.serializers import RegionSerializer
from api.fields import JSONField
from api.activity.aggregation import AggregationsSerializer

from api.generics import utils
from iati.models import Activity

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
    
    activities = serializers.SerializerMethodField()
    
    indicators = serializers.HyperlinkedIdentityField(
        view_name='country-indicators')
    cities = serializers.HyperlinkedIdentityField(view_name='country-cities')
  
    aggregations = serializers.SerializerMethodField()

    def get_filtered_activities(self, obj):
        # Circular imports!!!, must be refactored
        from api.activity.serializers import ActivitySerializer
        from api.activity.filters import ActivityFilter

        activity_filter = ActivityFilter()

        country_activities = Activity.objects.all().filter(
            recipient_country=obj
        )

        final_activities = activity_filter.filter_queryset(country_activities,
                                                           utils.query_params_from_context(self.context))

        return final_activities

    def get_activities(self, obj):

        serializer = ActivitySerializer(self.get_filtered_activities(obj),
                                        context={'request': self.context['request']},
                                        fields=('url', 'id', 'title', 'total_budget'),
                                        many=True)

        return serializer.data

    def get_aggregations(self, obj):
        fields = tuple(utils.query_params_from_context(self.context)['fields[aggregations]'].split(','))

        serializer = AggregationsSerializer(
            self.get_filtered_activities(obj),
            fields=fields
        )

        return serializer.data

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
            'data_source',
            'activities',
            'indicators',
            # 'adm1region_set',
            'cities',
            'aggregations',
            'location',
            'polygon',
        )
