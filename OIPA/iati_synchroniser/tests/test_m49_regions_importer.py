import os

from django.test import TestCase

import iati_synchroniser

from geodata.models import Region, RegionVocabulary
from iati_synchroniser.m49_regions_importer import M49RegionsImporter


class M49RegionsImporterTestCase(TestCase):

    def test_m49_regions_importer_should_ok(self):
        # Region is needed a vocabulary region
        RegionVocabulary(code='2', name='UN').save()

        os.path.dirname(iati_synchroniser.__file__)

        filename = '{app_path}/{file_path}'.format(
            app_path=os.path.dirname(iati_synchroniser.__file__),
            file_path='fixtures/test_m49_regions.json')
        M49RegionsImporter(filename=filename)

        # The name of code '1' should be 'World'
        # Check the fixture file on 'fixtures/test_m49_regions.json'
        region = Region.objects.get(code='1')

        self.assertEqual(region.name, 'World')

    def test_m49_regions_importer_region_should_empty(self):
        # If DATA_PLUGINS is just empty dictionary then not import anything
        # Override DATA_PLUGINS settings

        regions_before = Region.objects.count()

        with self.settings(DATA_PLUGINS={}):
            M49RegionsImporter()

        regions_after = Region.objects.count()

        # The Region should be empty
        self.assertEqual(regions_before, regions_after)
