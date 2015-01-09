import pytest
from django.test import RequestFactory
from iati.factory import iati_factory
from api.sector import serializers


class TestSectorSerializers:

    request_dummy = RequestFactory().get('/')

    def test_SectorSerializer(self):
        sector = iati_factory.SectorFactory.build(
            code=10,
            name='Sector A',
            description='Description A'
        )
        serializer = serializers.SectorSerializer(
            sector,
            context={'request': self.request_dummy}
        )
        assert serializer.data['code'] == sector.code, \
            """
            the data in sector.code should be serialized to a field named code
            inside the serialized object
            """
        assert serializer.data['name'] == sector.name, \
            """
            the data in sector.name should be serialized to a field named code
            inside the serialized object
            """
        assert serializer.data['description'] == sector.description, \
            """
            the data in sector.description should be serialized to a field named code
            inside the serialized object
            """
        required_fields = (
            'url',
            'activities',
            'category'
        )
        assertion_msg = "the field '{0}' should be in the serialized sector"
        for field in required_fields:
            assert field in serializer.data, assertion_msg.format(field)

    def test_SectorCategorySerializer(self):
        sector_category = iati_factory.SectorCategoryFactory.build(
            code=2,
        )
        serializer = serializers.SectorCategorySerializer(sector_category)
        assert serializer.data['code'] == sector_category.code,\
            """
            'sector_category.code' should be serialized to a field called 'code'
            """
