import os
import os.path

import ujson
from iati_codelists.models import Sector, SectorVocabulary


class Vocab7Importer():

    def __init__(self):
        """
        """

    def get_json_data(self, location_from_here):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + location_from_here
        json_data = open(location, encoding="utf-8")
        data = ujson.load(json_data)
        data = data.get('data')
        json_data.close()
        return data

    def update(self):
        data = self.get_json_data("/data/vocab7.json")
        clusters_vocabulary = SectorVocabulary.objects.get(pk=7)

        for sector in data:
            Sector.objects.get_or_create(
                code=sector.get('code'),
                vocabulary=clusters_vocabulary,
                defaults={
                    'name': sector.get('name'),
                    'description': sector.get('description'),
                    'category': None,
                })
