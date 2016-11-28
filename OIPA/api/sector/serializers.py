from rest_framework import serializers
import iati
from api.generics.serializers import DynamicFieldsModelSerializer, DynamicFieldsSerializer


class SectorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.SectorCategory
        fields = (
            'code',
        )


class SectorSerializer(DynamicFieldsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sectors:sector-detail', read_only=True)
    category = SectorCategorySerializer(read_only=True)

    code = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = iati.models.Sector
        fields = (
            'url',
            'code',
            'name',
            'description',
            'category',
        )

class SectorCategoryV2Serializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.SectorCategory
        fields = (
            'code',
        )


class SectorV2Serializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    url = serializers.HyperlinkedIdentityField(view_name='apiv2:sector-detail')
    category = SectorCategoryV2Serializer()


    class Meta:
        model = iati.models.Sector
        fields = (
            'id',
            'url',
            'code',
            'name',
            'description',
            'category',
        )

    def create(self, validated_data):
        cat = validated_data.pop('category', None)
        category = iati.models.SectorCategory(**cat)
        category.save()
        sector = iati.models.Sector(category=category, **validated_data)
        sector.save()
        return sector

    def update(self, instance, validated_data):
        cat = validated_data.pop('category', None)
        instance_id = validated_data.pop('id', None)
        update_category_instance = iati.models.SectorCategory(**cat)
        update_category_instance.save()
        update_instance = iati.models.Sector(category=update_category_instance, **validated_data)
        update_instance.id = instance_id
        update_instance.save()
        return update_instance
