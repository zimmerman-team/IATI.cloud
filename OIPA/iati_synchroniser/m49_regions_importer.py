from django.conf import settings

import ujson
from geodata.models import Region, RegionVocabulary


class M49RegionsImporter:
    """
    This is the plugins to import m49 regions if available on the settings.
    The JSON file m49 regions should be put on folder plugins/data of the root
    Django directory.
    The setting will be like below:
    """
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    DATA_PLUGINS = {
        'codelist': {
            'm49_region_file': '{base_dir}/plugins/data/{filename}'.format(
                base_dir=BASE_DIR, filename='regions.json')
        }
    }

    def __init__(self, filename=None):
        # The filename should be including full path of file itself.
        if not filename:
            try:
                # If the settings has codelist with m49_region_file
                # then continue this process otherwise just pass it.
                filename = settings.DATA_PLUGINS['codelist']['m49_region_file']
            except KeyError:
                pass

        if filename:
            data = self.get_json_data(filename)
            self.loop_through(data=data)

    def get_json_data(self, location_from_here):
        # Open file file json
        json_data = open(location_from_here, encoding='utf-8')
        data = ujson.load(json_data)
        json_data.close()
        return data

    def loop_through(self, data):
        for item in data:
            region_vocabulary = RegionVocabulary.objects.first()
            try:
                # The code of this vocabulary is 2.
                region_vocabulary = RegionVocabulary.objects.get(code='2')
            except RegionVocabulary.DoesNotExist:
                pass

            Region.objects.get_or_create(
                code=data[item],
                name=item,
                region_vocabulary=region_vocabulary
            )
