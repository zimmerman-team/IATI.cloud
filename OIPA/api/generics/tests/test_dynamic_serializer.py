from unittest import skip
from django.test import TestCase
from rest_framework.views import APIView
from api.generics.serializers import DynamicFieldsSerializer
from django.test import RequestFactory
from rest_framework import serializers


class SimpleModelTypeSerializer(DynamicFieldsSerializer):
    code = serializers.CharField()


class SimpleModelSerializer(DynamicFieldsSerializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    type = SimpleModelTypeSerializer()


class SimpleView(APIView):
    fields = (
            'id',
            )


class TestDynamicFields(TestCase):
    data = {'id': '10A',
            'name': 'NAME-10A',
            'description': 'DESC-10A',
            'type': {
                'code': 'CODE-10A'
                }
            }

    def test_fields_serializer(self):
        request = RequestFactory().get('/')

        context = {
                'view': SimpleView,
                'request': request
                }
        serializer = SimpleModelSerializer(
                data=self.data,
                context=context,
                fields=('id','name')
                )
        serializer.is_valid()

        self.assertIn('id', serializer.data)
        self.assertIn('name', serializer.data)
        self.assertNotIn('description', serializer.data)

    @skip('Is now handled in view, # TODO: write unittests for the views - 2016-02-18')
    def test_request_fields_serializer(self):
        pass

    @skip('Is now handled in view, # TODO: write unittests for the views - 2016-02-18')
    def test_sub_request_fields_serializer(self):
        pass

    @skip('Is now handled in view, # TODO: write unittests for the views - 2016-02-18')
    def test_view_fields_serializer(self):
        context = {
                'view': SimpleView
                }
        serializer = SimpleModelSerializer(data=self.data, context=context)
        serializer.is_valid()

        self.assertIn('id', serializer.data)
        self.assertNotIn('name', serializer.data)
        self.assertNotIn('description', serializer.data)


