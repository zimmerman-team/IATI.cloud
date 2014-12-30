from indicator import models
from rest_framework import serializers

class IndicatorTypeSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    description = serializers.CharField()
    friendly_label = serializers.CharField()
    type_data = serializers.CharField()
    deprivation_type = serializers.CharField()
    category = serializers.CharField()


    class Meta:
        model = models.Indicator
        fields = (
            'id',
            'description',
            'friendly_label',
            'type_data',
            'deprivation_type',
            'category'
        )

class IndicatorSerializer(serializers.ModelSerializer):
    indicator = IndicatorTypeSerializer()
    year = serializers.IntegerField()
    value = serializers.DecimalField(
        max_digits=17,
        decimal_places=4,
        coerce_to_string=False
    )
    selection_type = serializers.CharField


    class Meta:
        model = models.IndicatorData
        fields = (
            'indicator',
            'year',
            'value',
            'selection_type'
        )