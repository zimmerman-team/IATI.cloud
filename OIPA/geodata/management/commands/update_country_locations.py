# Django specific
from django.core.management.base import BaseCommand
from data.models import Country
from data.models.common import UnHabitatIndicatorCountry, IndicatorData, Indicator
from geodata.data_Backup.country_location import COUNTRY_LOCATION


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        print "Check latitude and longitude locations countries..."
        for c in Country.objects.all():
            try:
                if not c.latitude == COUNTRY_LOCATION[c.iso]['longitude']:
                    c.latitude = COUNTRY_LOCATION[c.iso]['longitude']
                    c.longitude = COUNTRY_LOCATION[c.iso]['latitude']
                    c.save()
                    print "Country %s has been updated" % c.country_name
            except KeyError:
                print "Country with iso %s not found..." % c.iso
#            if c.iso in COUNTRY_ISO_MAP.values():
#                print 'ha'
#            print [item[0] for item in COUNTRY_ISO_MAP.items() if item[1] == c.iso].pop()

#            print self.mapping_names[i.name]



