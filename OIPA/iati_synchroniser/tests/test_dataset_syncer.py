import json

from django.test import TestCase
from mock import MagicMock

from iati.factory import iati_factory
from iati_synchroniser.dataset_syncer import DatasetSyncer
from iati_synchroniser.models import Dataset, Publisher


class DatasetSyncerTestCase(TestCase):
    """
    Test DatasetSyncer functionality
    """

    def setUp(self):
        # XXX: previously, django's 'flush' management command was called to
        # flush the database, but it breaks tests ('no table blah blah exists')
        # and etc., so let's just manually remove objects which were created
        # during previous fixtures.
        # TODO: get rid of fixtures and use factory-boy everywhere.
        Publisher.objects.all().delete()

        self.datasetSyncer = DatasetSyncer()
        iati_factory.LanguageFactory.create(code='en', name='English')
        iati_factory.VersionFactory.create(code='2.02', name='2.02')
        iati_factory.OrganisationTypeFactory.create(
            code='22', name='Multilateral')

    def test_get_val_in_list_of_dicts(self):
        """
        test if returns correct key's data
        """
        input_list = [
            {"key": "filetype", "value": "organisation"},
            {"key": "version", "value": "2.02"},
        ]
        keyval = self.datasetSyncer.get_val_in_list_of_dicts(
            "filetype", input_list)

        self.assertEqual(keyval, input_list[0])

    def test_synchronize_with_iati_api(self):
        """

        """

        with open('iati_synchroniser/fixtures/test_publisher.json') as fixture:
            publisher = json.load(fixture).get('result')[0]

        with open('iati_synchroniser/fixtures/test_dataset.json') as fixture:
            dataset = json.load(fixture)['result']['results'][0]

        self.datasetSyncer.get_data = MagicMock(side_effect=[
            {'result': [publisher]},  # first occurance, return 1 publisher
            {'result': []},  # 2nd, return empty publisher db return
            {'result': {'results': [dataset]}},  # 3rd, return 1 dataset
            {'result': {'results': []}}  # 4th, return empty dataset db return
        ])

        self.datasetSyncer.synchronize_with_iati_api()

        self.assertEqual(Publisher.objects.count(), 1)
        self.assertEqual(Dataset.objects.count(), 1)

    def test_update_or_create_publisher(self):
        """
        check if dataset is saved as expected
        """

        with open('iati_synchroniser/fixtures/test_publisher.json') as fixture:
            data = json.load(fixture).get('result')[0]
            self.datasetSyncer.update_or_create_publisher(data)

        publisher = Publisher.objects.last()
        self.assertEqual("NP-SWC-27693", publisher.publisher_iati_id)
        self.assertEqual("Aasaman Nepal", publisher.display_name)
        self.assertEqual("aasaman", publisher.name)

    def test_update_or_create_dataset(self):
        """

        """
        publisher = Publisher(
            iati_id="85d72513-66b6-4642-a526-214b1081fff1",
            publisher_iati_id="",
            display_name="jica",
            name="Japan International Cooperation Agency (JICA)")

        publisher.save()

        with open('iati_synchroniser/fixtures/test_dataset.json') as fixture:
            data = json.load(fixture)['result']['results'][0]
            self.datasetSyncer.update_or_create_dataset(data)

        dataset = Dataset.objects.all()[0]
        self.assertEqual(
            "43aa0616-58a4-4d16-b0a9-1181e3871827", dataset.iati_id)
        self.assertEqual("cic-sl", dataset.name)
        self.assertEqual(
            "088States Ex-Yugoslavia unspecified2013", dataset.title)
        self.assertEqual(publisher, dataset.publisher)
        self.assertEqual(
            "http://aidstream.org/files/xml/cic-sl.xml", dataset.source_url)
        self.assertEqual(1, dataset.filetype)
