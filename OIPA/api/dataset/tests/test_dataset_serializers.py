from django.test import TestCase
from django.test import RequestFactory
from iati_synchroniser.factory.synchroniser_factory import DatasetFactory
from api.dataset.serializers import DatasetSerializer


class TestDatasetSerializers(TestCase):
    request_dummy = RequestFactory().get('/')

    def test_DatasetSerializer(self):
        dataset = DatasetFactory.build()
        serializer = DatasetSerializer(
            dataset,
            context={'request': self.request_dummy}
        )

        assert serializer.data['ref'] == dataset.ref,\
            """
            'dataset.ref' should be serialized to a field called 'ref'
            """
        assert serializer.data['title'] == dataset.title,\
            """
            'dataset.title' should be serialized to a field called 'title'
            """
        assert serializer.data['type'] == 'Activity standard',\
            """
            'dataset.type' should be serialized to a field called 'type'
            """
        assert serializer.data['source_url'] == dataset.source_url,\
            """
            'dataset.source_url' should be serialized to a field called 'source_url'
            """
        # assert serializer.data['date_created'] == dataset.date_created,\
        #     """
        #     'dataset.date_created' should be serialized to a field called 'date_created'
        #     """
        # assert serializer.data['date_updated'] == dataset.date_updated,\
        #     """
        #     'dataset.date_updated' should be serialized to a field called 'date_updated'
        #     """
        # assert serializer.data['last_found_in_registry'] == dataset.last_found_in_registry,\
        #     """
        #     'dataset.last_found_in_registry' should be serialized to a field called 'last_found_in_registry'
        #     """
        assert serializer.data['iati_standard_version'] == dataset.iati_standard_version,\
            """
            'dataset.iati_standard_version' should be serialized to a field called 'iati_standard_version'
            """

        required_fields = (
            'ref',
            'title',
            'type',
            'publisher',
            'url',
            'source_url',
            'date_created',
            'date_updated',
            'last_found_in_registry',
            'iati_standard_version'
        )

        assertion_msg = "the field '{0}' should be in the serialized dataset"
        for field in required_fields:
            assert field in serializer.data, assertion_msg.format(field)
