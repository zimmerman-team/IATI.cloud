import ujson
import os
import os.path

from iati_codelists.models import Sector, SectorCategory, SectorVocabulary


class DacSectorImporter():
    """
    Wrapper class for all import methods used on the Country model
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
        sectors = self.get_json_data("/data/dac_sectors.json")

        current_dac3 = None
        dac5_vocabulary = SectorVocabulary.objects.get(pk=1)

        for key, value in sectors.iteritems():
            if len(key) == 3:
                # dac 3
                current_dac3, created = SectorCategory.objects.get_or_create(
                    code=key,
                    defaults={
                        'name': value,
                        'description': ''
                    })

            if len(key) == 5:
                # dac 5
                Sector.objects.get_or_create(
                    code=key,
                    defaults={
                        'name': value,
                        'description': '',
                        'category': current_dac3,
                        'vocabulary': dac5_vocabulary
                    })
