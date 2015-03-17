from iati.models import Sector, BudgetType, DescriptionType
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


        def update_rain_sectors(self):

            base = os.path.dirname(os.path.abspath(__file__))
            location = base + "/data_backup/rain_sectors.json"

            json_data = open(location)
            rain_sectors = ujson.load(json_data)

            for cr in rain_sectors:

                try:
                    code = int(cr)
                    name = rain_sectors[cr]['name']

                    if Sector.objects.filter(code=code).exists():
                        the_sector = Sector.objects.get(code=code)
                        the_sector.name = name
                    else:
                        the_sector = Sector(code=code, name=name)
                    the_sector.save()

                except Exception as e:
                    print "error in update_rain_sectors" + str(type)
                    print e.args
                    return False
            json_data.close()



            base = os.path.dirname(os.path.abspath(__file__))
            location = base + "/data_backup/rain_budget_types.json"

            json_data = open(location)
            rain_sectors = ujson.load(json_data)

            for cr in rain_sectors:

                try:
                    code = int(cr)
                    name = rain_sectors[cr]['name']

                    if BudgetType.objects.filter(code=code).exists():
                        the_sector = BudgetType.objects.get(code=code)
                        the_sector.name = name
                    else:
                        the_sector = BudgetType(code=code, name=name, language="en")
                    the_sector.save()

                except Exception as e:
                    print "error in update_rain_sectors" + str(type)
                    print e.args
                    return False
            json_data.close()



            base = os.path.dirname(os.path.abspath(__file__))
            location = base + "/data_backup/rain_description_types.json"

            json_data = open(location)
            rain_sectors = ujson.load(json_data)

            for cr in rain_sectors:

                try:
                    code = int(cr)
                    name = rain_sectors[cr]['name']

                    if DescriptionType.objects.filter(code=code).exists():
                        the_sector = DescriptionType.objects.get(code=code)
                        the_sector.name = name
                    else:
                        the_sector = DescriptionType(code=code, name=name, description="RAIN description")
                    the_sector.save()

                except Exception as e:
                    print "error in update_rain_sectors" + str(type)
                    print e.args
                    return False
            json_data.close()

            return True

