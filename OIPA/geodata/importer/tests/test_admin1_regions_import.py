from django.test import TestCase
from mock import MagicMock

from geodata.factory.geodata_factory import Adm1RegionFactory, CountryFactory
from geodata.importer.admin1region import Adm1RegionImport
from geodata.models import Adm1Region


class Adm1RegionAdminTestCase(TestCase):

    def setUp(self):
        self.adm1_region_import = Adm1RegionImport()
        self.country = CountryFactory.create(code="AF")
        self.adm1_region = Adm1RegionFactory.build()

    def test_import_region_center(self):
        data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "adm1_code": "ABW-5150",
                        "OBJECTID_1": 3604,
                        "diss_me": 5150,
                        "adm1_cod_1": "ABW-5150",
                        "iso_3166_2": "AW-",
                        "wikipedia": "",
                        "iso_a2": "AF",
                        "adm0_sr": 3,
                        "name": "State in AF",
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-69.996938, 12.577582],
                                [-69.936391, 12.531724],
                            ]
                        ]
                    }
                }]
        }

        self.adm1_region_import.get_json_data = MagicMock(return_value=data)
        self.adm1_region_import.update_from_json()
        adm1_region = Adm1Region.objects.all()[0]
        self.assertEqual(adm1_region.country.code, 'AF')
        self.assertEqual(adm1_region.name, "State in AF")
        self.assertIsNotNone(adm1_region.polygon)
