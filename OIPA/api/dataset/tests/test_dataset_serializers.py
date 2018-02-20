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

        self.assertEqual(serializer.data.get('id'), dataset.id)
        self.assertEqual(serializer.data.get('name'), dataset.name)
        self.assertEqual(serializer.data.get('title'), dataset.title)
        self.assertEqual(serializer.data.get('filetype'), 'Activity')
        self.assertEqual(serializer.data.get('source_url'), dataset.source_url)
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
        self.assertEqual(serializer.data.get('iati_version'), dataset.iati_version)

        required_fields = (
            'id',
            'url',
            'name',
            'title',
            'filetype',
            'publisher',
            'source_url',
            'activities',
            'activity_count',
            'date_created',
            'date_updated',
            'last_found_in_registry',
            'iati_version',
            'sha1',
            'note_count',
            'notes'
        )

        assertion_msg = "the field '{0}' should be in the serialized dataset"
        for field in required_fields:
            assert field in serializer.data, assertion_msg.format(field)
