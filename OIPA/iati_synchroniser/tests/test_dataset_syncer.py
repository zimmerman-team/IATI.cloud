import json
from django.test import TestCase
from iati_synchroniser.dataset_syncer import DatasetSyncer
from iati_synchroniser.models import IatiXmlSource
from iati_synchroniser.models import Publisher
from iati_synchroniser.factory import synchroniser_factory
from django.core import management


class DatasetSyncerTestCase(TestCase):
    """
    Test DatasetSyncer functionality
    """
    def setUp(self):
        management.call_command('flush', interactive=False, verbosity=0)

    def test_line_parser(self):
        """
        Test if activity source data parsed
        """
        syncer = DatasetSyncer()

        publishers_count = Publisher.objects.count()
        sources_count = IatiXmlSource.objects.count()

        with open('iati_synchroniser/fixtures/test_activity.json') as fixture:
            data = json.load(fixture).get('results', [{}, ])[0]
            syncer.parse_json_line(data)

        self.assertNotEqual(publishers_count, Publisher.objects.count(),
            "New publisher should be added into database")

        self.assertNotEqual(sources_count, IatiXmlSource.objects.count(),
            "New IatiXmlSource should be added into database")

    def test_parsed_published_data_integrity(self):
        """
        Test if publisher data parsed correctly
        """
        syncer = DatasetSyncer()

        with open('iati_synchroniser/fixtures/test_activity.json') as fixture:
            data = json.load(fixture).get('results', [{}, ])[0]
            syncer.parse_json_line(data)

        publisher = Publisher.objects.all()[0]
        self.assertEqual("GB-CHC-1020488", publisher.org_id)
        self.assertEqual("cic", publisher.org_abbreviate)
        self.assertEqual("Children in Crisis", publisher.org_name)

    def test_parsed_xml_source_data_integrity(self):
        """
        Test if activity source data parsed correctly
        """
        syncer = DatasetSyncer()

        with open('iati_synchroniser/fixtures/test_activity.json') as fixture:
            data = json.load(fixture).get('results', [{}, ])[0]
            syncer.parse_json_line(data)

        source = IatiXmlSource.objects.all()[0]

        self.assertEqual("cic-sl", source.ref)
        self.assertEqual("http://aidstream.org/files/xml/cic-sl.xml",
                         source.source_url)
        self.assertEqual("Children in Crisis  Activity File for Sierra leone",
                         source.title)

        self.assertFalse(source.is_parsed,
            "New IatiXmlSource should not be marked as parsed")

    def test_if_publisher_assigned_to_source(self):
        """
        Test if correct publisher assigned to IatiXmlSource
        """
        syncer = DatasetSyncer()

        with open('iati_synchroniser/fixtures/test_activity.json') as fixture:
            data = json.load(fixture).get('results', [{}, ])[0]
            syncer.parse_json_line(data)

        source = IatiXmlSource.objects.get(ref="cic-sl")
        publisher = Publisher.objects.get(org_id="GB-CHC-1020488")
        self.assertEqual(publisher, source.publisher,
            "IatiXmlSource should have correct publisher")

    def test_remove_publisher_duplicates(self):

        publisher = synchroniser_factory.PublisherFactory.create(org_id='NL-1')
        publisher_duplicate = synchroniser_factory.PublisherFactory.create(org_id='NL-1')
        synchroniser_factory.DatasetFactory.create(
            ref='first_set',
            source_url='http://www.nourl.com/test1.xml',
            publisher=publisher)
        synchroniser_factory.DatasetFactory.create(
            ref='second_set',
            source_url='http://www.nourl.com/test2.xml',
            publisher=publisher_duplicate)

        syncer = DatasetSyncer()

        syncer.remove_publisher_duplicates('NL-1')

        # publisher duplicate should be removed, all datasets should be under the first publisher

        self.assertEqual(publisher,
                         Publisher.objects.filter(org_id='NL-1')[0],
                        "first publisher should still be in the database")

        self.assertEqual(1,
                         Publisher.objects.count(),
                         "publisher duplicate should be removed from the database")

        self.assertEqual(2,
                         publisher.iatixmlsource_set.all().count(),
                         "Both XML sources should still be in the database")

        self.assertEqual(2,
                         IatiXmlSource.objects.count(),
                         "Both XML sources should still be in the database")

