from django.test import TestCase
from django.test import RequestFactory
from iati_synchroniser.factory.synchroniser_factory import PublisherFactory
from api.publisher.serializers import PublisherSerializer


class TestPublisherSerializers(TestCase):
    request_dummy = RequestFactory().get('/')

    def test_PublisherSerializer(self):
        publisher = PublisherFactory.build()
        serializer = PublisherSerializer(
            publisher,
            context={'request': self.request_dummy}
        )

        assert serializer.data['org_id'] == publisher.org_id,\
            """
            'publisher.type' should be serialized to a field called 'type'
            """
        assert serializer.data['org_abbreviate'] == publisher.org_abbreviate,\
            """
            'publisher.source_url' should be serialized to a field called 'source_url'
            """
        assert serializer.data['org_name'] == publisher.org_name,\
            """
            'publisher.org_name' should be serialized to a field called 'org_name'
            """
        assert serializer.data['datasets'] == [],\
            """
            'publisher.datasets' should be serialized to a field called 'datasets'
            """
        assert serializer.data['activity_count'] == 0,\
            """
            'publisher.activity_count' should be serialized to a field called 'activity_count'
            """

        required_fields = (
            'url',
            'org_id',
            'org_abbreviate',
            'org_name',
            'datasets',
            'activities',
            'activity_count')

        assertion_msg = "the field '{0}' should be in the serialized dataset"
        for field in required_fields:
            assert field in serializer.data, assertion_msg.format(field)
