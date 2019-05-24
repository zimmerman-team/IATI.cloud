import os
import os.path

import ujson
from iati_codelists.models import Sector, SectorVocabulary


class SdgSectorImporter():
    """
    Wrapper class for all import methods used on the sector model.
    Only imports SDG targets for now.
    """

    def __init__(self):
        """
        """

    def get_json_data(self, location_from_here):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + location_from_here
        json_data = open(location, encoding="utf-8")
        data = ujson.load(json_data)
        json_data.close()
        return data

    def update(self):
        sectors = self.get_json_data(
            # These look like Unesco-specific Sectors, but despite the fact
            # that they are not in IATI (we can not parse them), they are
            # (will be) used globally, so we have to keep them in OIPA:
            "/data/sdg_target_sectors.json"
        ).get('targets')

        vocabulary = SectorVocabulary.objects.get(pk=8)

        for val in sectors:
            code = val.get('target')
            description = val.get('description')

            Sector.objects.get_or_create(
                code=code,
                defaults={
                    'name': description,
                    'description': description,
                    'vocabulary': vocabulary
                }
            )
