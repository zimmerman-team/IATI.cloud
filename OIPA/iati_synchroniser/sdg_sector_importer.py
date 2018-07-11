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
        json_data = open(location)
        data = ujson.load(json_data)
        json_data.close()
        return data

    def update(self):
        sectors = self.get_json_data(
            # FIXME: this should be imported dynamically ??:
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
