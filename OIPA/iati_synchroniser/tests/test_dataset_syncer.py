import json
from django.test import TestCase
from iati_synchroniser.dataset_syncer import DatasetSyncer
from iati_synchroniser.models import Dataset
from iati_synchroniser.models import Publisher
from iati_synchroniser.factory import synchroniser_factory
from django.core import management


class DatasetSyncerTestCase(TestCase):
    """
    Test DatasetSyncer functionality
    """
    def setUp(self):
        management.call_command('flush', interactive=False, verbosity=0)
        self.datasetSyncer = DatasetSyncer()

    def test_get_val_in_list_of_dicts(self):
        """
        test if returns correct key's data
        """
        input_list = [
            {"key": "filetype", "value": "organisation"},
            {"key": "version", "value": "2.02"},
        ]
        keyval = self.datasetSyncer.get_val_in_list_of_dicts("filetype", input_list)

        self.assertEqual(keyval, input_list[0])

    def test_synchronize_with_iati_api(self):
        """

        """
        #TODO

    def test_update_or_create_publisher(self):
        """

        """

    def test_update_or_create_dataset(self):
        """

        """

    def test_remove_deprecated(self):
        """

        """




    def test_line_parser(self):
        """
        Test if activity source data parsed
        """
        

        publishers_count = Publisher.objects.count()
        sources_count = Dataset.objects.count()

        with open('iati_synchroniser/fixtures/test_dataset.json') as fixture:
            data = json.load(fixture).get('results', [{}, ])[0]
            syncer.parse_json_line(data)

        self.assertNotEqual(publishers_count, Publisher.objects.count(),
            "New publisher should be added into database")

        self.assertNotEqual(sources_count, Dataset.objects.count(),
            "New Dataset should be added into database")

    def test_parsed_published_data_integrity(self):
        """
        Test if publisher data parsed correctly
        """
        syncer = DatasetSyncer()

        with open('iati_synchroniser/fixtures/test_dataset.json') as fixture:
            data = json.load(fixture).get('results', [{}, ])[0]
            syncer.parse_json_line(data)

        publisher = Publisher.objects.all()[0]
        self.assertEqual("GB-CHC-1020488", publisher.publisher_iati_id)
        self.assertEqual("cic", publisher.display_name)
        self.assertEqual("Children in Crisis", publisher.name)

    def test_parsed_xml_source_data_integrity(self):
        """
        Test if activity source data parsed correctly
        """
        syncer = DatasetSyncer()

        with open('iati_synchroniser/fixtures/test_dataset.json') as fixture:
            data = json.load(fixture).get('results', [{}, ])[0]
            syncer.parse_json_line(data)

        dataset = Dataset.objects.all()[0]

        self.assertEqual("cic-sl", dataset.name)
        self.assertEqual("http://aidstream.org/files/xml/cic-sl.xml",
                         source.source_url)
        self.assertEqual("Children in Crisis  Activity File for Sierra leone",
                         source.title)

        self.assertFalse(source.is_parsed,
            "New Dataset should not be marked as parsed")

    def test_if_publisher_assigned_to_source(self):
        """
        Test if correct publisher assigned to Dataset
        """
        syncer = DatasetSyncer()

        with open('iati_synchroniser/fixtures/test_dataset.json') as fixture:
            data = json.load(fixture).get('results', [{}, ])[0]
            syncer.parse_json_line(data)

        source = Dataset.objects.get(name="cic-sl")
        publisher = Publisher.objects.get(publisher_iati_id="GB-CHC-1020488")
        self.assertEqual(publisher, source.publisher,
            "Dataset should have correct publisher")

    def test_remove_publisher_duplicates(self):

        publisher = synchroniser_factory.PublisherFactory.create(publisher_iati_id='NL-1')
        publisher_duplicate = synchroniser_factory.PublisherFactory.create(publisher_iati_id='NL-1')
        synchroniser_factory.DatasetFactory.create(
            id='1',
            name='first_set',
            source_url='http://www.nourl.com/test1.xml',
            publisher=publisher)
        synchroniser_factory.DatasetFactory.create(
            id='2',
            name='second_set',
            source_url='http://www.nourl.com/test2.xml',
            publisher=publisher_duplicate)

        syncer = DatasetSyncer()

        syncer.remove_publisher_duplicates('NL-1')

        # publisher duplicate should be removed, all datasets should be under the first publisher

        self.assertEqual(publisher,
                         Publisher.objects.filter(publisher_iati_id='NL-1')[0],
                        "first publisher should still be in the database")

        self.assertEqual(1,
                         Publisher.objects.count(),
                         "publisher duplicate should be removed from the database")

        self.assertEqual(2,
                         publisher.dataset_set.all().count(),
                         "Both XML sources should still be in the database")

        self.assertEqual(2,
                         Dataset.objects.count(),
                         "Both XML sources should still be in the database")

