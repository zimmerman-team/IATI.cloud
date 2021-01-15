import datetime

from django.test import TestCase
from lxml.builder import E
from mock import MagicMock

from iati.factory import iati_factory
from iati.models import Activity
from iati.parser.IATI_2_01 import Parse as Parser_201
from iati_codelists.factory.codelist_factory import VersionFactory
from iati_synchroniser.factory.synchroniser_factory import DatasetFactory


class PostSaveFileTestCase(TestCase):
    """
    2.01: post save activity actions called
    """

    def setUp(self):
        self.dataset = DatasetFactory.create(name='source_reference')
        version = VersionFactory(code='2.01')
        self.first_activity = iati_factory.ActivityFactory.create(
            iati_identifier='IATI-0001',
            iati_standard_version=version,
            dataset=self.dataset)
        self.second_activity = iati_factory.ActivityFactory.create(
            iati_identifier='IATI-0002',
            iati_standard_version=self.first_activity.iati_standard_version,
            dataset=self.dataset)

    def test_post_save_file(self):
        """
        Check if all required functions are called
        """
        self.parser = Parser_201(None)
        self.parser.dataset = self.dataset
        self.parser.delete_removed_activities = MagicMock()
        activities_to_keep = []
        self.parser.post_save_file(self.parser.dataset, activities_to_keep)
        self.parser.delete_removed_activities.assert_called_once_with(
            self.parser.dataset)

    def test_delete_removed_activities(self):
        """The parser should remove activities that are not in the source any longer

        create 2 activities
        mock a file with 1 of them
        parsing this file should delete the other activity
        """
        root = E('iati-activities', version='2.01')
        xml_activity = E('iati-activity')
        xml_title = E('title', 'Title of activity 1')
        xml_activity.append(xml_title)
        xml_identifier = E('iati-identifier', 'IATI-0001')
        xml_activity.append(xml_identifier)
        root.append(xml_activity)

        self.parser = Parser_201(root)
        self.parser.dataset = self.dataset
        # mock non related functions that are called (and that use postgres fts
        # which makes the test fail on sqlite)
        self.parser.update_activity_search_index = MagicMock()
        self.parser.post_save_models = MagicMock()

        self.parser.parse_start_datetime = datetime.datetime.now()
        self.parser.parse_activities(root)

        self.assertEqual(Activity.objects.count(), 1)
