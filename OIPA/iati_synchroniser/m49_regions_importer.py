import ujson
from django.conf import settings

from geodata.models import Region, RegionVocabulary


class M49RegionsImporter:
    """
    This is the plugins to import m49 regions if available on the settings.
    The JSON file m49 regions should be put on folder plugins/data of the root
    Django directory.
    The setting will be like below:

    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    DATA_PLUGINS = {
        'codelist': {
            'm48_region_file': '{base_dir}/plugins/data/{filename}'.format(
                base_dir=BASE_DIR, filename='regions.json')
        }
    }

    """

    def __init__(self):
        # If the settings has codelist with m48_region_file
        # then continue this process otherwise just pass it.
        try:
            data = self.get_json_data(
                settings.DATA_PLUGINS['codelist']['m48_region_file'])

            self.loop_through(data=data)
        except KeyError:
            pass

    def get_json_data(self, location_from_here):
        # Open file file json
        json_data = open(location_from_here)
        data = ujson.load(json_data)
        json_data.close()
        return data

    def get_or_create(self, item):
        # To create region data should has region vocabulary
        region_vocabulary = RegionVocabulary.objects.first()
        try:
            # The code of this vocabulary is 2.
            region_vocabulary = RegionVocabulary.objects.get(code='2')
        except RegionVocabulary.DoesNotExist:
            pass

        Region.objects.get_or_create(
            code=str(int(item.get('code'))),
            name=item.get('name'),
            region_vocabulary=region_vocabulary
        )

    def loop_through(self, data):
        for item in data:
            # Create a new region data
            self.get_or_create(item=item)

            # If this item has sub item the looping again
            sub = item.get('sub')
            if sub:
                self.loop_through(data=sub)
