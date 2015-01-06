import json
from django.test import TestCase
from iati_synchroniser.dataset_syncer import DatasetSyncer
from iati_synchroniser.models import IatiXmlSource
from iati_synchroniser.models import Publisher


class DatasetSyncerTestCase(TestCase):
    """
    Test DatasetSyncer functionality
    """
    def test_line_parser(self):
        """
        Test if activity source data parsed
        """
        syncer = DatasetSyncer()

        publishers_count = Publisher.objects.count()
        sources_count = IatiXmlSource.objects.count()

        with open('iati_synchroniser/fixtures/test_activity.json') as fixture:
            data = json.load(fixture).get('results', [{}, ])[0]
            syncer.parse_json_line(data, 1)

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
            syncer.parse_json_line(data, 1)

        publisher = Publisher.objects.all()[0]
        self.assertEqual("GB-CHC-1020488", publisher.org_id)
        self.assertEqual("", publisher.org_abbreviate)
        self.assertEqual("Children in Crisis", publisher.org_name)

    def test_parsed_xml_source_data_integrity(self):
        """
        Test if activity source data parsed correctly
        """
        syncer = DatasetSyncer()

        with open('iati_synchroniser/fixtures/test_activity.json') as fixture:
            data = json.load(fixture).get('results', [{}, ])[0]
            syncer.parse_json_line(data, 1)

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
            syncer.parse_json_line(data, 1)

        source = IatiXmlSource.objects.get(ref="cic-sl")
        publisher = Publisher.objects.get(org_id="GB-CHC-1020488")
        self.assertEqual(publisher, source.publisher,
            "IatiXmlSource should have correct publisher")
