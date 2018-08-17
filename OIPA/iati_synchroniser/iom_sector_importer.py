import ujson
import os
import os.path

from iati_codelists.models import Sector, SectorCategory, SectorVocabulary


class IOMSectorImporter():
    """
    Wrapper class for all import methods used on the sector model.
    For IOM specific sectors.
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
        sectors = self.get_json_data("/data/iom_sectors.json")
        for val in sectors:
            code = val.get('code')
            description = val.get('description')

            # default vocabulary is 99
            vocabulary = SectorVocabulary.objects.get(pk=99)
            # if vocabulary number then code 98
            if code.isdigit():
                vocabulary = SectorVocabulary.objects.get(pk=98)

            sector, created = Sector.objects.get_or_create(
                code=code,
                defaults={
                    'name': description,
                    'description': description,
                    'vocabulary': vocabulary
                }
            )

            if not created:
                sector.name = description
                sector.description = description
                sector.save()

