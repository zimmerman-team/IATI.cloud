from django.test import TestCase
from mock import MagicMock

from geodata.factory.geodata_factory import RegionFactory
from geodata.importer.region import RegionImport
from geodata.models import Region
from iati_vocabulary.factory import vocabulary_factory


class RegionAdminTestCase(TestCase):

    def setUp(self):
        self.region_import = RegionImport()

        self.rv = vocabulary_factory.RegionVocabularyFactory()
        self.region = RegionFactory.create(
            code='689',
            region_vocabulary=self.rv
        )

    def test_import_region_center(self):
        data = {"689": {"latitude": "38.526682", "longitude": "69.697266"}, }
        self.region_import.get_json_data = MagicMock(return_value=data)
        self.region_import.update_region_center()
        region = Region.objects.all()[0]
        self.assertEqual(region.center_longlat.y, 38.526682)
        self.assertEqual(region.center_longlat.x, 69.697266)
