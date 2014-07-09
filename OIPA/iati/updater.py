from iati.models import Sector
import ujson
import os
import os.path

class SectorUpdater():

        def update_unesco_sectors(self):

            base = os.path.dirname(os.path.abspath(__file__))
            location = base + "/data_backup/unesco_sectors.json"

            json_data = open(location)
            unesco_sectors = ujson.load(json_data)

            for cr in unesco_sectors:

                try:
                    code = int(cr)
                    name = unesco_sectors[cr]['name']

                    if Sector.objects.filter(code=code).exists():
                        the_sector = Sector.objects.get(code=code)
                        the_sector.name = name
                    else:
                        the_sector = Sector(code=code, name=name)
                    the_sector.save()

                except Exception as e:
                    print "error in update_country_sectors" + str(type)
                    print e.args
                    return False
            json_data.close()
            return True
