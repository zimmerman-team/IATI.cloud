import os
import os.path

import ujson
from iati_codelists.models import AidType, AidTypeVocabulary


class AidTypeVocab3Importer():

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
        data = self.get_json_data("/data/aid_type_vocab3.json")
        aid_type_vocabulary = AidTypeVocabulary.objects.get(pk=3)

        for aid_type in data:
            AidType.objects.get_or_create(
                code=aid_type.get('code'),
                vocabulary=aid_type_vocabulary,
                defaults={
                    'name': aid_type.get('name'),
                    'description': aid_type.get('description'),
                    'category': None,
                })
