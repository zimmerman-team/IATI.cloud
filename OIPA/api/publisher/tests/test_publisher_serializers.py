from django.test import RequestFactory
from iati_synchroniser.factory.synchroniser_factory import PublisherFactory
from api.publisher.serializers import PublisherSerializer


class TestPublisherSerializers:
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
        assert serializer.data['publisher'] == publisher.publisher,\
            """
            'publisher.publisher' should be serialized to a field called 'publisher'
            """
        assert serializer.data['source_url'] == publisher.source_url,\
            """
            'publisher.source_url' should be serialized to a field called 'source_url'
            """

        required_fields = (
            'url',
            'org_id',
            'org_abbreviate',
            'org_name',
            'datasets')

        assertion_msg = "the field '{0}' should be in the serialized dataset"
        for field in required_fields:
            assert field in serializer.data, assertion_msg.format(field)
