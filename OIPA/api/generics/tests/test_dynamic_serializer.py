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


class TestDynamicFields:
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
        assert 'id' in serializer.data, \
            'id should be serialized since it is defined in the fields kwarg'
        assert 'name' in serializer.data, \
            'name should be serialized since it is defined in the fields kwarg'
        assert 'description' not in serializer.data, \
            'description should not be serialized ' \
            'since it is not defined in the fields kwarg'

    def test_request_fields_serializer(self):
        request = RequestFactory().get('/')
        request.query_params = {'fields': 'id,name'}
        context = {
            'view': SimpleView,
            'request': request
        }
        serializer = SimpleModelSerializer(
            data=self.data,
            fields=('id',),
            context=context
        )
        serializer.is_valid()
        assert 'id' in serializer.data, \
            'id should be serialized since it is defined in query_params'
        assert 'name' in serializer.data, \
            'name should be serialized since it is defined in query_params'
        assert 'description' not in serializer.data, \
            'name should not be serialized ' \
            'since it is not defined in query_params'

    def test_sub_request_fields_serializer(self):
        request = RequestFactory().get('/')
        request.query_params = {'fields[type]': 'code'}
        context = {
            'view': SimpleView,
            'request': request
        }
        serializer = SimpleModelSerializer(
            data=self.data,
            fields=('id','name'),
            context=context
        )
        serializer.is_valid()
        assert 'id' not in serializer.data, \
            'id should not be serialized ' \
            'since it is not defined in query_params'
        assert 'name' not in serializer.data, \
            'name should not be serialized ' \
            'since it is not defined in query_params'
        assert 'description' not in serializer.data, \
            'description should not be serialized ' \
            'since it is not defined in query_params'
        assert 'code' in serializer.data['type'], \
            'type: {code: <code>} should be serialized ' \
            'because it is defined in query_params'

    def test_view_fields_serializer(self):
        context = {
            'view': SimpleView
        }
        serializer = SimpleModelSerializer(data=self.data, context=context)
        serializer.is_valid()
        assert 'id' in serializer.data, \
            'id should be serialized because it is defined in view.fields'
        assert 'name' not in serializer.data, \
            'name should not be serialized ' \
            'because it is not defined in view.fields'
        assert 'description' not in serializer.data, \
            'description should not be serialized ' \
            'because it is not defined in view.fields'
