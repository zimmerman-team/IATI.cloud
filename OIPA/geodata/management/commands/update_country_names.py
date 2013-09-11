# Django specific
from django.core.management.base import BaseCommand
from data.models import Country
from data.models.common import UnHabitatIndicatorCountry, IndicatorData, Indicator
from data.models.constants import COUNTRY_LOCATION, COUNTRY_ISO_MAP, COUNTRY_ISO_MAP_NO_TRANS


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):

        for c in Country.objects.all():
            try:
                c_name =  COUNTRY_ISO_MAP_NO_TRANS[c.iso]
                if not c.country_name == c_name:
                    c.country_name = c_name
                    c.save()
            except:
                print c.iso
#            if c.iso in COUNTRY_ISO_MAP.values():
#                print 'ha'
#            print [item[0] for item in COUNTRY_ISO_MAP.items() if item[1] == c.iso].pop()

#            print self.mapping_names[i.name]



